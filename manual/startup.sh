#!/bin/sh
# 前端部署
/usr/local/nginx/sbin/nginx && echo 启动nginx部署前端

# 启动redis
cd /opt/redis-6.2.9/src && echo 切换到redis目录
./redis-server /opt/redis-6.2.9/redis.conf && echo 启动redis

# 删除gunicorn进程pid
rm -rf /opt/django/backend/logs/gunicorn.pid
echo 删除gunicorn.pid文件

#后端部署
cd /opt/django/backend && echo 切换到后端目录
supervisord -c supervisord.conf && echo 启动后端supervisord服务
