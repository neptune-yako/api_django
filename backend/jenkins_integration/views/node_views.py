from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
import traceback
import logging
from ..utils import R

logger = logging.getLogger(__name__)

class JenkinsNodesListView(APIView):
    """查询数据库中的 Jenkins 节点列表"""
    
    @extend_schema(
        tags=['Jenkins 节点管理'],
        summary='查询 Jenkins 节点列表',
        description='''
        获取数据库中存储的 Jenkins 节点列表。
        
        功能说明:
        - 查询所有已同步的节点信息
        - 支持按服务器ID筛选
        - 支持按在线状态筛选
        - 返回序列化的节点详细信息
        ''',
        parameters=[
            OpenApiParameter(
                name='server_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='服务器 ID - 筛选指定服务器的节点',
                required=False,
                examples=[
                    OpenApiExample('示例', value=1)
                ]
            ),
            OpenApiParameter(
                name='is_online',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='在线状态 - true:在线节点, false:离线节点',
                required=False,
                examples=[
                    OpenApiExample('查询在线节点', value=True),
                    OpenApiExample('查询离线节点', value=False)
                ]
            )
        ],
        responses={
            200: {
                'description': '查询成功',
                'content': {
                    'application/json': {
                        'example': {
                            'code': 200,
                            'message': '成功获取 3 个节点',
                            'data': [
                                {
                                    'id': 1,
                                    'server': 1,
                                    'server_name': 'Default Jenkins Server',
                                    'name': 'master',
                                    'display_name': 'Built-In Node',
                                    'description': 'the Jenkins controller\'s built-in node',
                                    'num_executors': 2,
                                    'labels': 'master',
                                    'is_online': True,
                                    'is_idle': False,
                                    'offline_cause': '',
                                    'last_sync_time': '2025-12-18T11:50:00',
                                    'create_time': '2025-12-18T11:45:00',
                                    'update_time': '2025-12-18T11:50:00'
                                }
                            ]
                        }
                    }
                }
            },
            500: {'description': '服务器内部错误'}
        }
    )
    def get(self, request):
        """
        获取数据库中存储的 Jenkins 节点列表
        
        Query Parameters:
            server_id: 服务器 ID (可选,筛选指定服务器的节点)
            is_online: true/false (可选,筛选在线/离线节点)
            
        Returns:
            {
                "code": 200,
                "message": "成功获取 3 个节点",
                "data": [
                    {
                        "id": 1,
                        "server_name": "Default Jenkins Server",
                        "name": "master",
                        "display_name": "Built-In Node",
                        "is_online": true,
                        "is_idle": false,
                        "num_executors": 2,
                        "labels": "master",
                        "last_sync_time": "2024-01-01T12:00:00Z"
                    },
                    ...
                ]
            }
        """
        try:
            from ..models import JenkinsNode
            from ..serializers import JenkinsNodeSerializer
            
            # 基础查询
            queryset = JenkinsNode.objects.select_related('server').all()
            
            # 筛选条件
            server_id = request.query_params.get('server_id')
            if server_id:
                queryset = queryset.filter(server_id=server_id)
            
            is_online = request.query_params.get('is_online')
            if is_online is not None:
                is_online_bool = is_online.lower() == 'true'
                queryset = queryset.filter(is_online=is_online_bool)
            
            # 排序
            queryset = queryset.order_by('server', 'name')
            
            # 序列化
            serializer = JenkinsNodeSerializer(queryset, many=True)
            
            return R.success(
                message=f'成功获取 {queryset.count()} 个节点',
                data=serializer.data
            )
            
        except Exception as e:
            error_msg = f"获取节点列表失败: {str(e)}"
            logger.error(error_msg)
            return R.internal_error(message=error_msg)


class JenkinsNodeGetConfigView(APIView):
    """获取节点配置和当前IP"""
    
    @extend_schema(
        tags=['Jenkins 节点管理'],
        summary='获取节点IP配置',
        description='''
        获取指定Jenkins节点的当前IP配置信息。
        
        功能说明:
        - 从Jenkins服务器获取节点XML配置
        - 解析并返回当前IP地址和SSH端口
        - 支持SSH launcher类型的节点
        ''',
        parameters=[
            OpenApiParameter(
                name='node_name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description='节点名称',
                required=True,
                examples=[
                    OpenApiExample('示例', value='my-node')
                ]
            )
        ],
        responses={
            200: {
                'description': '获取成功',
                'content': {
                    'application/json': {
                        'example': {
                            'code': 200,
                            'message': '成功获取节点IP配置',
                            'data': {
                                'node_name': 'my-node',
                                'current_ip': '192.168.1.100',
                                'ssh_port': '22'
                            }
                        }
                    }
                }
            },
            400: {'description': '请求参数错误'},
            500: {'description': '服务器内部错误'}
        }
    )
    def get(self, request, node_name):
        """
        获取节点当前IP配置
        
        Args:
            node_name: 节点名称(URL路径参数)
            
        Returns:
            {
                "code": 200,
                "message": "成功获取节点IP配置",
                "data": {
                    "node_name": "my-node",
                    "current_ip": "192.168.1.100",
                    "ssh_port": "22"
                }
            }
        """
        try:
            from ..jenkins_client import get_node_current_ip
            
            logger.info(f"获取节点 [{node_name}] 的IP配置")
            
            success, message, data = get_node_current_ip(node_name)
            
            if success:
                return R.success(message=message, data=data)
            else:
                return R.jenkins_error(message=message)
                
        except Exception as e:
            error_msg = f"获取节点IP配置失败: {str(e)}"
            error_trace = traceback.format_exc()
            logger.error(f"{error_msg}\n{error_trace}")
            return R.internal_error(
                message=error_msg,
                data={'traceback': error_trace}
            )


class JenkinsNodeUpdateIPView(APIView):
    """更新节点IP地址"""
    
    @extend_schema(
        tags=['Jenkins 节点管理'],
        summary='更新节点IP地址',
        description='''
        手动更新Jenkins节点的主机IP地址。
        
        功能说明:
        - 更新远程Jenkins服务器上的节点IP配置
        - 自动同步更新数据库中的节点IP记录
        - 支持SSH launcher和JNLP类型的节点
        - 可选更新SSH端口
        
        注意事项:
        - 仅支持SSH和JNLP启动器类型的节点
        - 更新后建议手动重启节点连接
        ''',
        parameters=[
            OpenApiParameter(
                name='node_name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description='节点名称',
                required=True,
                examples=[
                    OpenApiExample('示例', value='my-node')
                ]
            )
        ],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'new_ip': {
                        'type': 'string',
                        'description': '新的IP地址',
                        'example': '192.168.1.200'
                    },
                    'ssh_port': {
                        'type': 'integer',
                        'description': 'SSH端口(可选,默认保持不变)',
                        'example': 22
                    }
                },
                'required': ['new_ip']
            }
        },
        responses={
            200: {
                'description': '更新成功',
                'content': {
                    'application/json': {
                        'example': {
                            'code': 200,
                            'message': '成功更新节点IP地址',
                            'data': {
                                'node_name': 'my-node',
                                'old_ip': '192.168.1.100',
                                'new_ip': '192.168.1.200',
                                'updated': True,
                                'updated_in_db': True
                            }
                        }
                    }
                }
            },
            400: {'description': '请求参数错误'},
            500: {'description': '服务器内部错误'}
        }
    )
    def patch(self, request, node_name):
        """
        更新节点IP地址
        
        Args:
            node_name: 节点名称(URL路径参数)
            
        Request Body:
            new_ip: 新的IP地址(必需)
            ssh_port: SSH端口(可选)
            
        Returns:
            {
                "code": 200,
                "message": "成功更新节点IP地址",
                "data": {
                    "node_name": "my-node",
                    "old_ip": "192.168.1.100",
                    "new_ip": "192.168.1.200",
                    "updated": true,
                    "updated_in_db": true
                }
            }
        """
        try:
            from ..jenkins_client import update_node_ip
            from ..models import JenkinsNode
            
            # 获取请求参数
            new_ip = request.data.get('new_ip')
            ssh_port = request.data.get('ssh_port')
            
            if not new_ip:
                return R.bad_request(message='缺少必需参数: new_ip')
            
            logger.info(f"开始更新节点 [{node_name}] 的IP地址: {new_ip}")
            
            # 1. 更新Jenkins服务器上的配置
            success, message, data = update_node_ip(node_name, new_ip, ssh_port)
            
            if not success:
                return R.jenkins_error(message=message)
            
            # 2. 同步更新数据库中的节点记录
            updated_in_db = False
            try:
                # 查找数据库中的节点记录
                node = JenkinsNode.objects.filter(name=node_name).first()
                
                if node:
                    # 更新IP地址和手动标记
                    node.ip_address = new_ip
                    node.is_ip_manual = True  # 标记为手动修改
                    node.save()
                    
                    updated_in_db = True
                    logger.info(f"✓ 已同步更新数据库中节点 [{node_name}] 的IP: {new_ip}")
                else:
                    logger.warning(f"数据库中未找到节点 [{node_name}],跳过数据库更新")
                    
            except Exception as db_error:
                logger.error(f"更新数据库失败: {str(db_error)}")
                # 即使数据库更新失败,Jenkins配置已更新,仍然返回成功
                # 但在响应中标记数据库未更新
            
            # 3. 返回结果
            data['updated_in_db'] = updated_in_db
            
            return R.success(
                message='成功更新节点IP地址' + (' (数据库已同步)' if updated_in_db else ' (数据库未同步)'),
                data=data
            )
                
        except Exception as e:
            error_msg = f"更新节点IP失败: {str(e)}"
            error_trace = traceback.format_exc()
            logger.error(f"{error_msg}\n{error_trace}")
            return R.internal_error(
                message=error_msg,
                data={'traceback': error_trace}
            )
