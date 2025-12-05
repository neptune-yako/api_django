FROM nginx:1.27.1-alpine

# 复制前后端的静态文件
COPY ./static/ /usr/share/nginx/html/static/
COPY ./dist/ /usr/share/nginx/html/dist/
COPY ./default.conf /etc/nginx/conf.d/

# 挂在日志
VOLUME /var/log/
# 挂载端口
EXPOSE 80 81
