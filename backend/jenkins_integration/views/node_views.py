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
            ),

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
                    },
                    'credential_id': {
                        'type': 'string',
                        'description': 'SSH凭证ID(可选,留空则保持不变)',
                        'example': 'my-ssh-key'
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
            credential_id = request.data.get('credential_id')  # 新增：获取凭证ID
            
            if not new_ip:
                return R.bad_request(message='缺少必需参数: new_ip')
            
            logger.info(f"开始更新节点 [{node_name}] 的IP地址: {new_ip}" + 
                       (f", 凭证: {credential_id}" if credential_id else ""))
            
            # 1. 更新Jenkins服务器上的配置
            success, message, data = update_node_ip(node_name, new_ip, ssh_port, credential_id)
            
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


class JenkinsNodeCreateView(APIView):
    """创建 SSH 类型的 Jenkins 节点"""
    
    @extend_schema(
        tags=['Jenkins 节点管理'],
        summary='创建 SSH 节点',
        description='''
        创建新的 SSH 连接类型的 Jenkins 节点。
        
        功能说明:
        - 支持创建 SSH launcher 类型的节点
        - 自动配置 SSH 连接参数
        - 可选配置凭证 ID、端口、标签等
        - 创建成功后自动同步到数据库
        
        注意事项:
        - 节点名称必须唯一
        - 需要预先在 Jenkins 中配置 SSH 凭证
        - 确保目标主机已安装 Java 运行环境
        ''',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'name': {
                        'type': 'string',
                        'description': '节点名称 (必需)',
                        'example': 'build-node-01'
                    },
                    'host': {
                        'type': 'string',
                        'description': '主机 IP 或域名 (必需)',
                        'example': '192.168.1.100'
                    },
                    'credential_id': {
                        'type': 'string',
                        'description': 'SSH 凭证 ID',
                        'example': 'ssh-key-id'
                    },
                    'port': {
                        'type': 'integer',
                        'description': 'SSH 端口',
                        'example': 22
                    },
                    'remote_fs': {
                        'type': 'string',
                        'description': '远程工作目录',
                        'example': '/home/jenkins'
                    },
                    'labels': {
                        'type': 'string',
                        'description': '节点标签 (空格分隔)',
                        'example': 'linux docker'
                    },
                    'num_executors': {
                        'type': 'integer',
                        'description': '执行器数量',
                        'example': 2
                    },
                    'description': {
                        'type': 'string',
                        'description': '节点描述',
                        'example': 'Build server for production'
                    }
                },
                'required': ['name', 'host']
            }
        },
        responses={
            200: {
                'description': '创建成功',
                'content': {
                    'application/json': {
                        'example': {
                            'code': 200,
                            'message': '成功创建节点 [build-node-01]',
                            'data': {
                                'node_name': 'build-node-01',
                                'host': '192.168.1.100',
                                'port': 22,
                                'labels': 'linux docker',
                                'num_executors': 2,
                                'remote_fs': '/home/jenkins',
                                'credential_id': 'ssh-key-id'
                            }
                        }
                    }
                }
            },
            400: {'description': '请求参数错误'},
            500: {'description': '服务器内部错误'}
        }
    )
    def post(self, request):
        """
        创建 SSH 类型的节点
        
        Request Body:
            name: 节点名称 (必需)
            host: 主机 IP 或域名 (必需)
            credential_id: SSH 凭证 ID (可选)
            port: SSH 端口 (可选,默认 22)
            remote_fs: 远程工作目录 (可选,默认 /home/jenkins)
            labels: 节点标签 (可选)
            num_executors: 执行器数量 (可选,默认 2)
            description: 节点描述 (可选)
        """
        try:
            from ..jenkins_client import create_ssh_node
            
            # 获取请求参数
            name = request.data.get('name')
            host = request.data.get('host')
            credential_id = request.data.get('credential_id', '')
            port = request.data.get('port', 22)
            remote_fs = request.data.get('remote_fs', '/home/jenkins')
            labels = request.data.get('labels', '')
            num_executors = request.data.get('num_executors', 2)
            description = request.data.get('description', '')
            
            # 参数校验
            if not name:
                return R.bad_request(message='缺少必需参数: name')
            if not host:
                return R.bad_request(message='缺少必需参数: host')
            
            logger.info(f"创建 SSH 节点: {name} @ {host}")
            
            # 调用 jenkins_client 创建节点
            success, message, data = create_ssh_node(
                name=name,
                host=host,
                credential_id=credential_id,
                port=port,
                remote_fs=remote_fs,
                labels=labels,
                num_executors=num_executors,
                description=description
            )
            
            if success:
                # 创建成功后，快速记录基本信息到数据库（不调用耗时的 get_node_info）
                try:
                    from ..models import JenkinsNode, JenkinsServer
                    
                    # 获取默认的 Jenkins 服务器
                    server = JenkinsServer.objects.filter(is_active=True).first()
                    
                    if server:
                        # 只存储创建时的基本参数，避免耗时的 API 调用
                        JenkinsNode.objects.update_or_create(
                            server=server,
                            name=name,
                            defaults={
                                'display_name': name,
                                'description': description,
                                'num_executors': num_executors,
                                'labels': labels,
                                'ip_address': host,  # 使用创建时提供的 host 作为 IP
                                'is_ip_manual': True,  # 标记为手动设置
                                'is_online': False,  # 初始标记为离线，等待同步任务更新
                                'is_idle': True,
                                'offline_cause': '等待同步',
                            }
                        )
                        logger.info(f"✓ 节点 [{name}] 基本信息已记录到数据库，详细信息将通过同步任务更新")
                    else:
                        logger.warning(f"未找到活跃的 Jenkins 服务器，跳过数据库同步")
                        
                except Exception as db_error:
                    logger.error(f"同步节点到数据库失败: {str(db_error)}")
                    # 即使数据库同步失败，仍然返回创建成功（因为 Jenkins 上已创建）
                
                return R.success(message=message, data=data)
            else:
                return R.jenkins_error(message=message)
                
        except Exception as e:
            error_msg = f"创建节点失败: {str(e)}"
            error_trace = traceback.format_exc()
            logger.error(f"{error_msg}\n{error_trace}")
            return R.internal_error(
                message=error_msg,
                data={'traceback': error_trace}
            )


class JenkinsNodeDeleteView(APIView):
    """删除 Jenkins 节点"""
    
    @extend_schema(
        tags=['Jenkins 节点管理'],
        summary='删除节点',
        description='''
        删除指定的 Jenkins 节点。
        
        功能说明:
        - 从 Jenkins 服务器删除节点
        - 自动同步删除数据库中的节点记录
        - 支持强制删除
        
        注意事项:
        - 删除操作不可逆
        - 如果节点正在运行构建任务,建议先禁用节点
        - master 节点无法删除
        ''',
        parameters=[
            OpenApiParameter(
                name='node_name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description='节点名称',
                required=True,
                examples=[
                    OpenApiExample('示例', value='build-node-01')
                ]
            )
        ],
        responses={
            200: {
                'description': '删除成功',
                'content': {
                    'application/json': {
                        'example': {
                            'code': 200,
                            'message': '成功删除节点 [build-node-01]',
                            'data': {
                                'node_name': 'build-node-01',
                                'deleted': True
                            }
                        }
                    }
                }
            },
            400: {'description': '请求参数错误'},
            500: {'description': '服务器内部错误'}
        }
    )
    def delete(self, request, node_name):
        """
        删除指定节点
        
        Args:
            node_name: 节点名称 (URL路径参数)
        """
        try:
            from ..jenkins_client import delete_node
            from ..models import JenkinsNode
            
            logger.info(f"删除节点: {node_name}")
            
            # 1. 从 Jenkins 服务器删除
            success, message, data = delete_node(node_name)
            
            if not success:
                return R.jenkins_error(message=message)
            
            # 2. 同步删除数据库记录
            try:
                deleted_count = JenkinsNode.objects.filter(name=node_name).delete()[0]
                if deleted_count > 0:
                    logger.info(f"✓ 已同步删除数据库中的节点记录: {node_name}")
            except Exception as db_error:
                logger.error(f"删除数据库记录失败: {str(db_error)}")
            
            return R.success(message=message, data=data)
                
        except Exception as e:
            error_msg = f"删除节点失败: {str(e)}"
            error_trace = traceback.format_exc()
            logger.error(f"{error_msg}\n{error_trace}")
            return R.internal_error(
                message=error_msg,
                data={'traceback': error_trace}
            )


class JenkinsNodeInfoView(APIView):
    """获取节点详细信息"""
    
    @extend_schema(
        tags=['Jenkins 节点管理'],
        summary='获取节点详细信息',
        description='''
        获取指定 Jenkins 节点的详细信息。
        
        功能说明:
        - 从 Jenkins 服务器获取实时节点状态
        - 包含执行器、标签、在线状态等详细信息
        - 包含监控数据 (CPU、内存等)
        ''',
        parameters=[
            OpenApiParameter(
                name='node_name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description='节点名称',
                required=True,
                examples=[
                    OpenApiExample('示例', value='build-node-01')
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
                            'message': '成功获取节点 [build-node-01] 信息',
                            'data': {
                                'name': 'build-node-01',
                                'displayName': 'build-node-01',
                                'description': 'Build server',
                                'numExecutors': 2,
                                'labels': 'linux,docker',
                                'offline': False,
                                'temporarilyOffline': False,
                                'idle': True,
                                'offlineCauseReason': ''
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
        获取节点详细信息
        
        Args:
            node_name: 节点名称 (URL路径参数)
        """
        try:
            from ..jenkins_client import get_node_info
            
            logger.info(f"获取节点详细信息: {node_name}")
            
            success, message, data = get_node_info(node_name)
            
            if success:
                return R.success(message=message, data=data)
            else:
                return R.jenkins_error(message=message)
                
        except Exception as e:
            error_msg = f"获取节点信息失败: {str(e)}"
            error_trace = traceback.format_exc()
            logger.error(f"{error_msg}\n{error_trace}")
            return R.internal_error(
                message=error_msg,
                data={'traceback': error_trace}
            )


class JenkinsNodeToggleView(APIView):
    """启用/禁用节点"""
    
    @extend_schema(
        tags=['Jenkins 节点管理'],
        summary='启用/禁用节点',
        description='''
        启用或禁用指定的 Jenkins 节点。
        
        功能说明:
        - 支持启用 (enable) 和禁用 (disable) 操作
        - 禁用时可选提供禁用原因
        - 不影响正在运行的构建任务
        ''',
        parameters=[
            OpenApiParameter(
                name='node_name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description='节点名称',
                required=True,
                examples=[
                    OpenApiExample('示例', value='build-node-01')
                ]
            )
        ],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'action': {
                        'type': 'string',
                        'description': '操作类型: enable (启用) 或 disable (禁用)',
                        'enum': ['enable', 'disable'],
                        'example': 'disable'
                    },
                    'message': {
                        'type': 'string',
                        'description': '禁用原因 (仅在 action=disable 时有效)',
                        'example': 'Maintenance in progress'
                    }
                },
                'required': ['action']
            }
        },
        responses={
            200: {
                'description': '操作成功',
                'content': {
                    'application/json': {
                        'example': {
                            'code': 200,
                            'message': '成功禁用节点 [build-node-01]',
                            'data': {
                                'node_name': 'build-node-01',
                                'disabled': True,
                                'message': 'Maintenance in progress'
                            }
                        }
                    }
                }
            },
            400: {'description': '请求参数错误'},
            500: {'description': '服务器内部错误'}
        }
    )
    def post(self, request, node_name):
        """
        启用/禁用节点
        
        Args:
            node_name: 节点名称 (URL路径参数)
            
        Request Body:
            action: 操作类型 (enable/disable)
            message: 禁用原因 (可选,仅在 disable 时使用)
        """
        try:
            from ..jenkins_client import enable_node, disable_node
            
            action = request.data.get('action')
            message = request.data.get('message', '')
            
            if not action:
                return R.bad_request(message='缺少必需参数: action')
            
            if action not in ['enable', 'disable']:
                return R.bad_request(message='参数 action 必须是 enable 或 disable')
            
            logger.info(f"{action} 节点: {node_name}")
            
            if action == 'enable':
                success, msg, data = enable_node(node_name)
            else:  # disable
                success, msg, data = disable_node(node_name, message)
            
            if success:
                # 同步更新数据库中的节点状态
                try:
                    from ..models import JenkinsNode
                    node = JenkinsNode.objects.filter(name=node_name).first()
                    if node:
                        # 更新节点在线状态
                        if action == 'enable':
                            node.is_online = True
                            node.offline_cause = ''
                        else:  # disable
                            node.is_online = False
                            node.offline_cause = message or '手动禁用'
                        node.save()
                        logger.info(f"✓ 已同步更新数据库中节点 [{node_name}] 的状态")
                    else:
                        logger.warning(f"数据库中未找到节点 [{node_name}]，跳过数据库更新")
                except Exception as db_error:
                    logger.error(f"更新数据库失败: {str(db_error)}")
                    # 即使数据库更新失败，Jenkins操作已成功，仍然返回成功
                
                return R.success(message=msg, data=data)
            else:
                return R.jenkins_error(message=msg)
                
        except Exception as e:
            error_msg = f"操作节点失败: {str(e)}"
            error_trace = traceback.format_exc()
            logger.error(f"{error_msg}\n{error_trace}")
            return R.internal_error(
                message=error_msg,
                data={'traceback': error_trace}
            )


class JenkinsNodeReconnectView(APIView):
    """重新连接节点"""
    
    @extend_schema(
        tags=['Jenkins 节点管理'],
        summary='重新连接节点',
        description='''
        重新连接离线的 Jenkins 节点。
        
        功能说明:
        - 先禁用节点,再重新启用
        - 触发节点重新建立连接
        - 自动检查连接状态
        
        注意事项:
        - 适用于网络暂时中断等情况
        - 可能需要等待几秒钟才能完成重连
        ''',
        parameters=[
            OpenApiParameter(
                name='node_name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description='节点名称',
                required=True,
                examples=[
                    OpenApiExample('示例', value='build-node-01')
                ]
            )
        ],
        responses={
            200: {
                'description': '重连成功',
                'content': {
                    'application/json': {
                        'example': {
                            'code': 200,
                            'message': '节点 [build-node-01] 重新连接成功',
                            'data': {
                                'node_name': 'build-node-01',
                                'is_online': True,
                                'reconnected': True
                            }
                        }
                    }
                }
            },
            400: {'description': '请求参数错误'},
            500: {'description': '服务器内部错误'}
        }
    )
    def post(self, request, node_name):
        """
        重新连接节点
        
        Args:
            node_name: 节点名称 (URL路径参数)
        """
        try:
            from ..jenkins_client import reconnect_node
            
            logger.info(f"重新连接节点: {node_name}")
            
            success, message, data = reconnect_node(node_name)
            
            if success:
                # 同步更新数据库中的节点状态
                try:
                    from ..models import JenkinsNode
                    node = JenkinsNode.objects.filter(name=node_name).first()
                    if node and data:
                        # 更新节点在线状态
                        node.is_online = data.get('is_online', False)
                        if not node.is_online:
                            node.offline_cause = data.get('offline_cause', '')
                        else:
                            node.offline_cause = ''
                        node.save()
                        logger.info(f"✓ 已同步更新数据库中节点 [{node_name}] 的状态")
                    else:
                        logger.warning(f"数据库中未找到节点 [{node_name}]，跳过数据库更新")
                except Exception as db_error:
                    logger.error(f"更新数据库失败: {str(db_error)}")
                    # 即使数据库更新失败，Jenkins操作已成功，仍然返回成功
                
                return R.success(message=message, data=data)
            else:
                return R.jenkins_error(message=message)
                
        except Exception as e:
            error_msg = f"重新连接节点失败: {str(e)}"
            error_trace = traceback.format_exc()
            logger.error(f"{error_msg}\n{error_trace}")
            return R.internal_error(
                message=error_msg,
                data={'traceback': error_trace}
            )


class JenkinsNodeLabelsView(APIView):
    """更新节点标签"""
    
    @extend_schema(
        tags=['Jenkins 节点管理'],
        summary='更新节点标签',
        description='''
        更新指定 Jenkins 节点的标签。
        
        功能说明:
        - 支持批量设置标签
        - 标签用空格分隔
        - 自动覆盖原有标签
        
        使用场景:
        - 动态调整节点能力标识
        - 用于 Job 的节点选择策略
        ''',
        parameters=[
            OpenApiParameter(
                name='node_name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description='节点名称',
                required=True,
                examples=[
                    OpenApiExample('示例', value='build-node-01')
                ]
            )
        ],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'labels': {
                        'type': 'string',
                        'description': '节点标签 (空格分隔)',
                        'example': 'linux docker java11'
                    }
                },
                'required': ['labels']
            }
        },
        responses={
            200: {
                'description': '更新成功',
                'content': {
                    'application/json': {
                        'example': {
                            'code': 200,
                            'message': '成功更新节点 [build-node-01] 标签',
                            'data': {
                                'node_name': 'build-node-01',
                                'old_labels': 'linux docker',
                                'new_labels': 'linux docker java11',
                                'updated': True
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
        更新节点标签
        
        Args:
            node_name: 节点名称 (URL路径参数)
            
        Request Body:
            labels: 节点标签 (空格分隔)
        """
        try:
            from ..jenkins_client import update_node_labels
            
            labels = request.data.get('labels')
            
            if labels is None:
                return R.bad_request(message='缺少必需参数: labels')
            
            logger.info(f"更新节点 [{node_name}] 标签: {labels}")
            
            success, message, data = update_node_labels(node_name, labels)
            
            if success:
                return R.success(message=message, data=data)
            else:
                return R.jenkins_error(message=message)
                
        except Exception as e:
            error_msg = f"更新节点标签失败: {str(e)}"
            error_trace = traceback.format_exc()
            logger.error(f"{error_msg}\n{error_trace}")
            return R.internal_error(
                message=error_msg,
                data={'traceback': error_trace}
            )


class JenkinsCredentialsListView(APIView):
    """获取 Jenkins 凭证列表"""
    
    @extend_schema(
        tags=['Jenkins 节点管理'],
        summary='获取凭证列表',
        description='''
        获取 Jenkins 中配置的所有凭证列表，用于创建节点时选择SSH凭证。
        
        功能说明:
        - 获取系统域中的所有凭证
        - 支持多种凭证类型（SSH、Username/Password等）
        - 自动识别凭证类型
        
        注意事项:
        - 需要有查看凭证的权限
        - 返回的凭证不包含密钥内容，只包含ID和描述
        ''',
        responses={
            200: {
                'description': '获取成功',
                'content': {
                    'application/json': {
                        'example': {
                            'code': 200,
                            'message': '成功获取 5 个凭证',
                            'data': [
                                {
                                    'id': 'aliyun-ssh-key',
                                    'description': 'Aliyun server SSH key',
                                    'displayName': '',
                                    'typeName': 'SSH Username with private key',
                                    'className': 'com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey',
                                    'scope': 'GLOBAL'
                                },
                                {
                                    'id': 'github-token',
                                    'description': 'GitHub Personal Access Token',
                                    'displayName': '',
                                    'typeName': 'Secret text',
                                    'className': 'org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl',
                                    'scope': 'GLOBAL'
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
        获取Jenkins凭证列表
        """
        try:
            from ..jenkins_client import get_credentials_list
            
            logger.info("获取 Jenkins 凭证列表")
            
            success, message, data = get_credentials_list()
            
            if success:
                return R.success(message=message, data=data)
            else:
                return R.jenkins_error(message=message)

        except Exception as e:
            error_msg = f"获取凭证列表失败: {str(e)}"
            error_trace = traceback.format_exc()
            logger.error(f"{error_msg}\n{error_trace}")
            return R.internal_error(
                message=error_msg,
                data={'traceback': error_trace}
            )


class JenkinsNodeSyncView(APIView):
    """同步 Jenkins 节点到项目环境"""

    @extend_schema(
        tags=['Jenkins 节点管理'],
        summary='同步节点到项目环境',
        description='''
        将 Jenkins 节点同步到指定项目的环境列表中。

        功能说明:
        - 从 Jenkins 获取所有节点信息
        - 将节点 IP 地址映射为项目的环境 host
        - 自动创建或更新环境记录(不删除已有记录)
        - 跳过没有 IP 地址的节点
        - 标记环境来源为 'jenkins'

        处理逻辑:
        - 如果环境名称不存在: 创建新环境
        - 如果环境名称已存在: 更新 host 地址

        注意事项:
        - 不会删除任何现有的手动创建环境
        - 同步的环境 source 标记为 'jenkins'
        - 需要提供有效的 project_id
        ''',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'project_id': {
                        'type': 'integer',
                        'description': '项目 ID (必需)',
                        'example': 1
                    }
                },
                'required': ['project_id']
            }
        },
        responses={
            200: {
                'description': '同步成功',
                'content': {
                    'application/json': {
                        'example': {
                            'code': 200,
                            'message': '成功同步 3 个环境',
                            'data': {
                                'total': 5,
                                'created': 2,
                                'updated': 1,
                                'skipped': 2,
                                'nodes': [
                                    {
                                        'name': 'build-node-01',
                                        'ip': '192.168.1.100',
                                        'action': 'created',
                                        'is_online': True
                                    }
                                ]
                            }
                        }
                    }
                }
            },
            400: {'description': '请求参数错误'},
            404: {'description': '项目不存在'},
            500: {'description': '服务器内部错误'}
        }
    )
    def post(self, request):
        """
        同步 Jenkins 节点到项目环境

        Request Body:
            project_id: 项目 ID (必需)

        Returns:
            {
                "code": 200,
                "message": "成功同步 3 个环境",
                "data": {
                    "total": 5,
                    "created": 2,
                    "updated": 1,
                    "skipped": 2,
                    "nodes": [...]
                }
            }
        """
        try:
            from ..services.jenkins_sync import JenkinsSyncService
            from project.models import Project

            # 获取请求参数
            project_id = request.data.get('project_id')

            if not project_id:
                return R.bad_request(message='缺少必需参数: project_id')

            # 验证项目存在
            try:
                project = Project.objects.get(id=project_id)
            except Project.DoesNotExist:
                return R.not_found(message=f'项目 [{project_id}] 不存在')

            # 获取当前登录用户名
            username = request.user.username if request.user.is_authenticated else 'jenkins_sync'

            logger.info(f"开始同步 Jenkins 节点到项目 [{project.name}]")

            # 调用同步服务
            success, message, data = JenkinsSyncService.sync_nodes(project_id, username)

            if success:
                return R.success(message=message, data=data)
            else:
                return R.jenkins_error(message=message)

        except Exception as e:
            error_msg = f"同步节点到环境失败: {str(e)}"
            error_trace = traceback.format_exc()
            logger.error(f"{error_msg}\n{error_trace}")
            return R.internal_error(
                message=error_msg,
                data={'traceback': error_trace}
            )


# ==================== 从 Jenkins 同步所有节点到数据库 ====================

class JenkinsNodesSyncFromJenkinsView(APIView):
    """从 Jenkins 服务器同步所有节点到本地数据库"""
    
    @extend_schema(
        tags=['Jenkins 节点管理'],
        summary='从 Jenkins 同步节点',
        description='''
        从 Jenkins 服务器获取所有节点并同步到本地数据库。
        
        功能说明:
        - 从 Jenkins 服务器获取所有节点信息
        - 创建或更新本地数据库中的节点记录
        - 不会删除本地已有的节点记录
        - 适用于首次同步或手动刷新节点列表
        ''',
        responses={
            200: {
                'description': '同步成功',
                'content': {
                    'application/json': {
                        'example': {
                            'code': 200,
                            'message': '成功同步 5 个节点',
                            'data': {
                                'total': 5,
                                'created': 2,
                                'updated': 3
                            }
                        }
                    }
                }
            },
            500: {'description': '服务器内部错误'}
        }
    )
    def post(self, request):
        """
        从 Jenkins 同步节点到数据库
        
        Returns:
            {
                "code": 200,
                "message": "成功同步 5 个节点",
                "data": {
                    "total": 5,
                    "created": 2,
                    "updated": 3
                }
            }
        """
        try:
            from ..models import JenkinsNode, JenkinsServer
            from ..jenkins_client import get_all_nodes
            
            logger.info("开始从 Jenkins 服务器同步节点")
            
            # 获取活跃的 Jenkins 服务器
            server = JenkinsServer.objects.filter(is_active=True).first()
            
            if not server:
                return R.bad_request(message='未找到活跃的 Jenkins 服务器配置')
            
            # 从 Jenkins 获取所有节点
            success, message, nodes_data = get_all_nodes()
            
            if not success:
                return R.jenkins_error(message=f'从 Jenkins 获取节点失败: {message}')
            
            if not nodes_data:
                return R.success(message='Jenkins 上没有节点', data={'total': 0, 'created': 0, 'updated': 0})
            
            # 同步到数据库
            created_count = 0
            updated_count = 0
            
            for node_data in nodes_data:
                node_name = node_data.get('name')
                
                if not node_name:
                    continue
                
                # 使用 update_or_create 创建或更新节点
                node, created = JenkinsNode.objects.update_or_create(
                    server=server,
                    name=node_name,
                    defaults={
                        'display_name': node_data.get('displayName', node_name),
                        'description': node_data.get('description', ''),
                        'num_executors': node_data.get('numExecutors', 1),
                        'labels': node_data.get('labels', ''),
                        'ip_address': node_data.get('ip_address', ''),
                        'is_online': not node_data.get('offline', False),
                        'is_idle': node_data.get('idle', True),
                        'offline_cause': node_data.get('offlineCauseReason', ''),
                    }
                )
                
                if created:
                    created_count += 1
                    logger.info(f"✓ 创建节点: {node_name}")
                else:
                    updated_count += 1
                    logger.info(f"✓ 更新节点: {node_name}")
            
            
            total_count = created_count + updated_count
            result_message = f'成功同步 {total_count} 个节点 (新增 {created_count}, 更新 {updated_count})'
            
            logger.info(result_message)
            
            # 同步完成后，自动清理失效节点
            try:
                from ..services.jenkins_sync import JenkinsSyncService
                cleanup_success, cleanup_msg, cleanup_stats = JenkinsSyncService.cleanup_nodes(server_id=server.id)
                
                deleted_count = 0
                envs_deleted_count = 0
                
                if cleanup_success and cleanup_stats:
                    deleted_count = cleanup_stats.get('nodes_deleted', 0)
                    envs_deleted_count = cleanup_stats.get('envs_deleted', 0)
                    if deleted_count > 0 or envs_deleted_count > 0:
                        logger.info(f"自动清理失效节点: 删除 {deleted_count} 个节点, {envs_deleted_count} 个环境")
                        result_message += f', 清理 {deleted_count} 个失效节点'
                else:
                    if not cleanup_success:
                        logger.warning(f"自动清理节点失败: {cleanup_msg}")
            except Exception as cleanup_error:
                logger.error(f"执行节点清理时出错: {str(cleanup_error)}")
                deleted_count = 0
                envs_deleted_count = 0
            
            return R.success(
                message=result_message,
                data={
                    'total': total_count,
                    'created': created_count,
                    'updated': updated_count,
                    'deleted': deleted_count,
                    'envs_deleted': envs_deleted_count
                }
            )
            
        except Exception as e:
            error_msg = f"同步节点失败: {str(e)}"
            error_trace = traceback.format_exc()
            logger.error(f"{error_msg}\n{error_trace}")
            return R.internal_error(
                message=error_msg,
                data={'traceback': error_trace}
            )


