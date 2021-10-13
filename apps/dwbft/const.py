# -*- coding:utf-8 -*-
# __author__ = Amos
# Email = wangyangxu@amos-x.com
# Create_at = 2021/6/24 下午3:33
# FileName = const

import os
from .conf import ConfigManager

__all__ = ['BASE_DIR', 'PROJECT_DIR', 'VERSION', 'CONFIG']

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(BASE_DIR)
VERSION = '0.1'
CONFIG = ConfigManager.load_user_config()
