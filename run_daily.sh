#!/bin/bash
# 切换到项目目录
cd /Users/zhenzhongzhang/project1 || exit

# 激活虚拟环境
source /Users/zhenzhongzhang/project1/.venv/bin/activate

# 执行 Python 脚本并记录日志
/Users/zhenzhongzhang/project1/.venv/bin/python /Users/zhenzhongzhang/project1/dataset_update.py >> /Users/zhenzhongzhang/project1/daily.log 2>&1