#!/bin/bash
# 激活虚拟环境的脚本

echo "🐍 激活Python虚拟环境..."
source agents_venv/bin/activate

echo "📦 已安装的包:"
pip list

echo ""
echo "✅ 虚拟环境已激活！"
echo "💡 现在可以运行:"
echo "   python3 agents/test_database_simple.py"
echo "   python3 agents/simple_database_demo.py"
echo ""
echo "🔧 要退出虚拟环境，运行: deactivate"
