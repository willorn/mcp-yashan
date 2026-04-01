# -*- coding: utf-8 -*-
"""测试模块导入"""

from core import get_executor, TOOLS

print('Core module imported successfully')
print(f'Tools: {[t["name"] for t in TOOLS]}')
