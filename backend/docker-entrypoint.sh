#!/bin/bash
set -e

# 等待数据库准备就绪（如果使用外部数据库）
echo "等待数据库准备就绪..."

# 运行数据库迁移
echo "运行数据库迁移..."
if [ -d "alembic" ]; then
    alembic upgrade head
else
    echo "警告: 未找到 alembic 目录，跳过数据库迁移"
fi

# 创建初始数据（如果需要）
echo "检查初始数据..."
python -c "
try:
    from app.core.database import engine, Base
    Base.metadata.create_all(bind=engine)
    print('数据库表创建成功')
except Exception as e:
    print(f'数据库初始化失败: {e}')
    exit(1)
"

echo "启动应用..."

# 执行传入的命令
exec "$@"