import multiprocessing

# 工作进程
workers = multiprocessing.cpu_count() * 2 + 1
# 服务地址和端口
bind = '0.0.0.0:8000'
# 设置为True，开发时用，代码修改会自动重启
reload = False
# 关闭守护进程，将进程交给supervisor管理
daemon = False
# 设置最大并发量
worker_connections = 2000
# gunicorn进程文件名。不能放在容器里面，防止文件存在
pidfile = '/tmp/gunicorn.pid'
# gunicorn日志文件
accesslog = '/app/logs/gunicorn_access.log'
errorlog = '/app/logs/gunicorn_error.log'
# 设置日志记录水平
loglevel = 'info'
