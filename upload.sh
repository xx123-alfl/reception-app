#!/bin/bash
# ================================================
# 上传项目文件到云服务器
# 用法：bash upload.sh <服务器IP>
# 示例：bash upload.sh 123.456.789.0
# ================================================

if [ -z "$1" ]; then
    echo "用法: bash upload.sh <服务器IP>"
    echo "示例: bash upload.sh 123.456.789.0"
    exit 1
fi

SERVER_IP=$1
SERVER_USER="root"

echo "📤 上传文件到 ${SERVER_USER}@${SERVER_IP}..."
echo "   密码输入时不会显示，输完按回车即可"
echo ""

cd "$(dirname "$0")"

# 上传所有需要的文件（排除不需要的）
scp -r \
    server.py \
    index.html \
    data.json \
    deploy.sh \
    ${SERVER_USER}@${SERVER_IP}:/opt/reception-app/

echo ""
echo "✅ 文件上传完成！"
echo ""
echo "下一步：SSH 登录服务器执行部署"
echo "  ssh ${SERVER_USER}@${SERVER_IP}"
echo "  cd /opt/reception-app"
echo "  bash deploy.sh"
