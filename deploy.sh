#!/bin/bash
# ================================================
# 接待流程管理系统 - 云服务器一键部署脚本
# 适用：阿里云 / 腾讯云 Ubuntu 20.04+
# 用法：bash deploy.sh
# ================================================

set -e

APP_DIR="/opt/reception-app"
SERVICE_NAME="reception-app"
PORT=80

echo "============================================"
echo "  🏢 接待流程管理系统 - 部署开始"
echo "============================================"

# 1. 创建目录
mkdir -p $APP_DIR
cd $APP_DIR

# 2. 上传文件（通过环境变量或直接写入）
# 这里文件已经通过 git/scp 放在当前目录

# 3. 开放防火墙端口
echo "🔓 配置防火墙..."
if command -v ufw &>/dev/null; then
    ufw allow $PORT/tcp 2>/dev/null || true
elif command -v firewall-cmd &>/dev/null; then
    firewall-cmd --add-port=$PORT/tcp --permanent 2>/dev/null || true
    firewall-cmd --reload 2>/dev/null || true
fi
echo "   ✅ 端口 $PORT 已开放（云服务器还需在控制台安全组中放行）"

# 4. 创建 systemd 服务（开机自启 + 进程守护）
echo "⚙️  配置 systemd 服务..."
cat > /etc/systemd/system/${SERVICE_NAME}.service << SYSTEMD
[Unit]
Description=接待流程管理系统
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$APP_DIR
ExecStart=python3 server.py
Restart=always
RestartSec=3
Environment=PORT=$PORT

[Install]
WantedBy=multi-user.target
SYSTEMD

systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl restart $SERVICE_NAME

echo ""
echo "============================================"
echo "  ✅ 部署完成！"
echo "============================================"
echo ""
echo "  📌 访问地址: http://$(curl -s ifconfig.me 2>/dev/null || echo '你的服务器IP')"
echo ""
echo "  常用命令："
echo "    systemctl status reception-app   # 查看状态"
echo "    systemctl restart reception-app  # 重启服务"
echo "    systemctl stop reception-app     # 停止服务"
echo "    journalctl -u reception-app -f   # 查看日志"
echo ""
