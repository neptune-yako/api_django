#!/bin/sh

# 执行数据库迁移
python manage.py makemigrations
python manage.py migrate
if [ $? -ne 0 ];then
    echo '数据库连接失败重启'
    exit 1
fi

# 启动supervisor服务
supervisord -c supervisord.conf
