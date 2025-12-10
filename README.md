## 🌈 项目开发环境部署

### 后端技术
- 基于 python3.10 + django5 + mysql8 + redis6 + celery

- 使用软件版本
- python 3.11.5
- mysql 8.0.23
- redis 6.2.9

### 前端技术
- 基于 vue3 + element-plus + vite7 + pinia + axios + echarts

- 使用软件版本
- node 22.20.0

- 模板网站：https://gitee.com/HalseySpicy/Geeker-Admin

### 🚧 Linux启动前置软件环境mysql、redis、nginx
```bash
# 启动mysql数据库服务
systemctl start mysqld
# 配置开机自启动
systemctl enable mysqld

# 配置Nginx，重新加载配置文件
/usr/local/nginx/sbin/nginx -s reload
# 启动Nginx的命令
/usr/local/nginx/sbin/nginx

# 启动Redis
cd /opt/redis-6.2.9/src
./redis-server /opt/redis-6.2.9/redis.conf
```

### 🚧 项目启动初始化-后端
```bash
# 修改对应的数据库、redis
backend/settings.py

# backend目录下，安装依赖
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 新建数据库django，迁移数据库表
python manage.py makemigrations
python manage.py migrate

# 创建超级用户，并按提示输入相应用户名、密码、邮箱
python manage.py createsuperuser

# 运行后端项目
python manage.py runserver

# 使用测试计划和定时任务需要启动celery-beat和celery-worker
# 启动celery-beat
celery -A backend beat -l info
# 启动celery-worker，Windows下命令增加参数-p threads/eventlet
celery -A backend worker -l info -P threads
celery -A backend worker -l info -P eventlet

# 启动任务监控celery
celery -A backend flower --port=5555

# 后端静态文件打包
python manage.py collectstatic

# 接口文档访问地址
http://localhost:8000/swagger
http://localhost:8000/redoc

# linux激活虚拟环境
source /home/virtualenv/django/bin/activate
# 退出虚拟环境
deactivate
```

### 🚧 项目启动初始化-前端
```bash
# 设置国内源
npm config set registry http://mirrors.cloud.tencent.com/npm/

# 全局安装yarn
npm install -g yarn

# 进入项目frontend，安装项目依赖
yarn

# 运行前端项目
yarn dev

# 前端打包发布
yarn build
```

### 🚧 访问项目地址
#### 后端
http://localhost:8000/admin

#### 前端
http://localhost:8080

### 🚧 部署、使用帮助文档
### 帮助文档
http://120.26.11.168:30

帮助文档的源码地址：https://gitee.com/pytests/docs



#### 后端django启动命令
```bash
python manage.py runserver
```

#### 后端异步任务启动命令
```bash
# 启动celery-beat
celery -A backend beat -l info
# 启动celery-worker，Windows下命令增加参数-p threads/eventlet
celery -A backend worker -l info -P threads
celery -A backend worker -l info -P eventlet
```

#### 前端vue启动命令
```bash
yarn dev
```
