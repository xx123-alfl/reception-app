#!/bin/bash
# 接待流程管理系统 - 一键启动脚本

cd "$(dirname "$0")"

# Kill existing processes
pkill -f "python3 server.py" 2>/dev/null
pkill -f "cloudflared tunnel" 2>/dev/null
sleep 1

echo "============================================"
echo "  🏢 接待流程管理系统"
echo "============================================"
echo ""

# 1. Start Python server
echo "📡 启动本地服务器..."
python3 server.py &
sleep 2

# 2. Start Cloudflare Tunnel
echo "🌐 启动公网隧道..."
cloudflared tunnel --url http://localhost:8080 2>&1 | while read line; do
  echo "$line"
  if echo "$line" | grep -q "trycloudflare.com"; then
    URL=$(echo "$line" | grep -o 'https://[^ ]*trycloudflare.com')
    echo "$URL" > ./tunnel_url.txt
    echo ""
    echo "============================================"
    echo "  ✅ 公网链接已生成！"
    echo "  🔗 $URL"
    echo "  📋 链接已保存到 tunnel_url.txt"
    echo "============================================"
  fi
done &

echo "按 Ctrl+C 停止所有服务"
wait
