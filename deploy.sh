#!/bin/bash
# 介绍参数作为项目的名字，默认是py
project=${1:-py}
echo $project
# 部署函数
deploy(){
	echo "部署项目"
	echo "注意部署项目会强制构建镜像"
	docker-compose -p $project up -d --build && echo "部署成功"
}

# 重启函数
restart(){
	echo "重启项目"
	docker-compose -p $project restart && echo "重启成功"
}

# 暂停函数
close(){
	echo "暂停项目"
	docker-compose -p $project stop && echo "暂停成功"
}

# 删除函数
delete(){
	echo "删除项目"
	echo "为了数据安全删除项目只会删除容器，不会删除数据卷，要删除卷请手动操作"
	docker-compose -p $project down && echo "删除成功"
}

# 删除函数
clear(){
  echo "删除镜像"
  echo "build过程中会出现虚悬镜像，虚悬镜像不会自动删除而占用存储空间，为此删除空的镜像"
      empty_images=$(docker images -qf dangling=true)
      if [ -n "$empty_images" ]; then
          docker rmi $empty_images
          echo "已删除镜像名称为空的镜像"
      else
          echo "没有发现镜像名称为空的镜像"
      fi
}

# 开始函数
start(){
	while true
	do
		select name in "部署项目" "重启项目" "暂停项目" "删除项目" "删除镜像" "退出菜单"
		do
			case $name in
				"部署项目")
					deploy
					break
					;;
				"重启项目")
					restart
					break
					;;
				"暂停项目")
					close
					break
					;;
				"删除项目")
					delete
					break
					;;
			  "删除镜像")
					clear
					break
					;;
				"退出菜单")
					echo "退出菜单"
					break
					;;
			esac
		done
		if [ $name = "退出菜单" ]; then
			break
		fi
	done
}

start
