#!/usr/bin/env python3
"""
工具服务类
包含所有工具相关的业务逻辑
"""
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import os
import sys
import chromadb
from pathlib import Path
from typing import List, Dict, Any, Optional
from chromadb.config import Settings
from schemas.tool_node import ToolNode, ToolParameter, ToolResponse
from utils.exception_handler import print_exception_stack, safe_execute


# 添加项目根目录到 Python 路径（如果还没有添加）
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class ToolService:
    """工具服务类，包含所有工具相关的业务逻辑"""

    def __init__(self):
        self.chromadb_manager = get_chromadb_manager()

    def is_connected(self) -> bool:
        """检查 ChromaDB 连接状态"""
        return self.chromadb_manager.is_connected()

    def get_all_tools(self) -> List[ToolNode]:
        """获取所有工具节点"""
        tools = self.chromadb_manager.get_all_tools()
        
        return ToolNormalizer.normalize_tool_list(tools)

    def search_tools(self, query: str, n_results: int = 10) -> List[ToolNode]:
        """搜索工具节点"""
        return self.chromadb_manager.search_tools(query, n_results)

    def get_tool_by_id(self, tool_id: str) -> Optional[ToolNode]:
        """根据 ID 获取工具节点"""
        return self.chromadb_manager.get_tool_by_id(tool_id)

    def get_tool_by_name(self, tool_name: str) -> Optional[ToolNode]:
        """根据名称获取工具节点"""
        return self.chromadb_manager.get_tool_by_name(tool_name)

    def get_tool_by_module_and_function(self, module_path: str, function_name: str) -> Optional[ToolNode]:
        """根据模块路径和函数名称获取工具节点"""
        return self.chromadb_manager.get_tool_by_module_and_function(module_path, function_name)

    def get_tool_statistics(self) -> Dict[str, Any]:
        """获取工具统计信息"""
        return self.chromadb_manager.get_tool_statistics()

    def get_tools_by_type(self, tool_type: str) -> List[ToolNode]:
        """根据类型获取工具节点"""
        return self.chromadb_manager.get_tools_by_type(tool_type)

    def get_tools_by_category(self, category: str) -> List[ToolNode]:
        """根据分类获取工具节点"""
        return self.chromadb_manager.get_tools_by_category(category)

class ToolNormalizer:
    """工具节点标准化工具类"""
    
    @staticmethod
    def normalize_module_path(tool_node: ToolNode) -> ToolNode:
        """
        标准化工具节点的 module_path 属性
        
        处理规则：
        1. 去掉 pyservices/ 前缀
        2. 去掉 tool_set/ 前缀  
        3. 去掉 .py 后缀
        4. 将 "." 替换为 "/"
        
        Args:
            tool_node: 需要处理的工具节点
            
        Returns:
            处理后的工具节点
        """
        if not tool_node or not hasattr(tool_node, 'module_path') or not tool_node.module_path:
            return tool_node
            
        module_path = tool_node.module_path
        
        # 去掉 pyservices/ 前缀
        module_path = module_path.replace('pyservices/', '', 1)
            
        # 去掉 tool_set/ 前缀
        module_path = module_path.replace('tool_set/', '', 1)
            
        # 去掉 .py 后缀（只去掉末尾的 .py）
        if module_path.endswith('.py'):
            module_path = module_path[:-3]
            
        # 将 "." 替换为 "/"（在去掉 .py 后缀之后）
        module_path = module_path.replace('.', '/')
        
        # 创建新的工具节点对象（保持其他属性不变）
        tool_node.module_path = module_path
        return tool_node

    @staticmethod
    def normalize_tool_list(tool_nodes: List[ToolNode]) -> List[ToolNode]:
        """
        批量标准化工具节点列表的 module_path 属性
        
        Args:
            tool_nodes: 需要处理的工具节点列表
            
        Returns:
            处理后的工具节点列表
        """
        return [ToolNormalizer.normalize_module_path(tool) for tool in tool_nodes]



class ChromaDBManager:
    """ChromaDB 管理器，用于保存和检索 ToolNode 对象"""
    
    def __init__(self, persist_directory: Optional[str] = None):
        if persist_directory is None:
            persist_directory = os.getenv("CHROMA_DB_PATH", "/Users/dinghaitao/vs_projecty/lupin_studio/pyservices/chroma_db")
        
        self.persist_directory = Path(persist_directory)
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True,
                is_persistent=True
            )
        )
        
        # 创建或获取集合
        self.collection = self.client.get_or_create_collection(
            name="tools",
            metadata={"description": "工具节点集合"}
        )

    def _metadata_to_tool_node(self, tool_id: str, metadata: Dict[str, Any]) -> ToolNode:
        """将 ChromaDB 元数据转换为 ToolNode 对象"""
        try:
            # 解析参数
            parameters = []
            if metadata.get('parameters'):
                try:
                    import json
                    params_data = json.loads(metadata['parameters']) if isinstance(metadata['parameters'], str) else metadata['parameters']
                    for param_data in params_data:
                        param = ToolParameter(
                            name=param_data.get('name', ''),
                            type=param_data.get('type', 'string'),
                            description=param_data.get('description', ''),
                            required=param_data.get('required', False),
                            default=param_data.get('default')
                        )
                        parameters.append(param)
                except Exception as e:
                    print_exception_stack(e, "解析参数", "WARNING")
                    print(f"⚠️ 解析参数失败: {e}")
            
            # 解析响应
            response = None
            if metadata.get('response'):
                try:
                    import json
                    response_data = json.loads(metadata['response']) if isinstance(metadata['response'], str) else metadata['response']
                    response = ToolResponse(
                        type=response_data.get('type', 'string'),
                        description=response_data.get('description', ''),
                        response_schema=response_data.get('response_schema')
                    )
                except Exception as e:
                    print_exception_stack(e, "解析响应", "WARNING")
                    print(f"⚠️ 解析响应失败: {e}")
            
            # 处理日期时间字段
            modified_at = None
            if metadata.get('modified_at') and metadata['modified_at'].strip():
                try:
                    from datetime import datetime
                    modified_at = datetime.fromisoformat(metadata['modified_at'])
                except:
                    modified_at = None
            
            last_called_at = None
            if metadata.get('last_called_at') and metadata['last_called_at'].strip():
                try:
                    from datetime import datetime
                    last_called_at = datetime.fromisoformat(metadata['last_called_at'])
                except:
                    last_called_at = None
            
            # 解析 tags
            tags = []
            if metadata.get('tags'):
                try:
                    tags = json.loads(metadata['tags']) if isinstance(metadata['tags'], str) else metadata['tags']
                except Exception as e:
                    print_exception_stack(e, "解析 tags", "WARNING")
                    print(f"⚠️ 解析 tags 失败: {e}")
                    tags = []
            
            children = []
            if metadata.get('children'):
                try:
                    children = json.loads(metadata['children']) if isinstance(metadata['children'], str) else metadata['children']
                except Exception as e:
                    print_exception_stack(e, "解析 children", "WARNING")
                    print(f"⚠️ 解析 children 失败: {e}")
                    children = []

            # 创建 ToolNode
            return ToolNode(
                id=tool_id,
                name=metadata.get('name', ''),
                title=metadata.get('title', ''),
                description=metadata.get('description', ''),
                icon=metadata.get('icon', '🔧'),
                type=metadata.get('type', 'function'),
                parameters=parameters,
                response=response,
                function_name=metadata.get('function_name'),
                category=metadata.get('category'),
                tags=tags,
                module_path=metadata.get('module_path', ''),
                modified_at=modified_at,
                last_called_at=last_called_at,
                call_count=metadata.get('call_count', 0),
                children=children,
                parent=metadata.get('parent', '')
            )
            
        except Exception as e:
            print_exception_stack(e, "转换 ToolNode", "ERROR")
            print(f"❌ 转换 ToolNode 失败: {e}")
            # 返回一个基本的 ToolNode
            return ToolNode(
                id=tool_id,
                name=metadata.get('name', 'Unknown'),
                title=metadata.get('title', 'Unknown'),
                description=metadata.get('description', ''),
                icon='🔧',
                type='function',
                parameters=[],
                response=None,
                function_name=None,
                category=None,
                tags=[],
                module_path='',
                modified_at=None,
                last_called_at=None,
                call_count=0,
                children=[]
            )  
    def is_connected(self) -> bool:
        """检查 ChromaDB 连接状态"""
        return self.client is not None and self.collection is not None

    def get_all_tools(self) -> List[ToolNode]:
        """获取所有工具节点"""
        try:
            if not self.is_connected():
                raise Exception("ChromaDB 未连接")
            
            # 获取所有数据
            results = self.collection.get()
            
            print(f"🔍 调试: ChromaDB 返回了 {len(results['ids'])} 个工具")
            
            if not results['ids']:
                return []
            
            # 转换为 ToolNode 对象
            tools = []
            for i, tool_id in enumerate(results['ids']):
                metadata = results['metadatas'][i]
                print(f"🔍 调试: 处理工具 {i+1}: {tool_id} (type: {metadata.get('type')}, function_name: {metadata.get('function_name')})")
                tool_node = self._metadata_to_tool_node(tool_id, metadata)
                tools.append(tool_node)
            
            print(f"🔍 调试: 成功转换了 {len(tools)} 个工具节点")
            return tools
            
        except Exception as e:
            print_exception_stack(e, "获取所有工具", "ERROR")
            print(f"❌ 获取所有工具失败: {e}")
            return []
    
    

# 全局单例实例
_chromadb_manager = None

def get_chromadb_manager() -> ChromaDBManager:
    """获取 ChromaDB 管理器的单例实例"""
    global _chromadb_manager
    if _chromadb_manager is None:
        _chromadb_manager = ChromaDBManager()
    return _chromadb_manager

