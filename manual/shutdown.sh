#!/bin/bash
# 查找python进程的pid并排除ps指令的pid
py=$(ps -ef | grep python | grep -v grep | awk '{print $2}')
echo "需要杀掉的进程号："
echo "${py}"

# 循环判断pid，并杀掉进程
for pid in $py
do
kill -9 "$pid"
echo "终止进程号：$pid"
done

# 查找redis进程的pid并排除ps指令的pid
re=$(ps -ef | grep redis | grep -v grep | awk '{print $2}')
echo "需要杀掉的进程号：${re}"

# 循环判断pid，并杀掉进程
for rid in $re
do
kill -9 "$rid"
echo "终止进程号：$rid"
done

# 查找nginx进程的pid并排除ps指令的pid
re=$(ps -ef | grep nginx | grep -v grep | awk '{print $2}')
echo "需要杀掉的进程号：${re}"

# 循环判断pid，并杀掉进程
for rid in $re
do
kill -9 "$rid"
echo "终止进程号：$rid"
done
