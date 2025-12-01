#!/bin/bash
# 快捷运行mock数据生成脚本

cd "$(dirname "$0")/.."
source venv/bin/activate
python test/generate_mock_data.py
