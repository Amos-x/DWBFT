# -*- coding:utf-8 -*-
# __author__ = Amos
# Email = wangyangxu@amos-x.com
# Create_at = 2021/6/24 下午3:28
# FileName = conf

"""
配置分类：
1. Django自身的配置，写到settings中
2. 用户不需要更改的，或只有开发人员进行更改的程序相关配置写到settings中
3. 用户需要更改的，写默认值到本config中，提供给外层config.yaml文件修改
"""
import os
import errno
import yaml
from django.urls import reverse_lazy
from .const import BASE_DIR, PROJECT_DIR


class DoesNotExist(Exception):
    pass


class Config(dict):
    """
    配置类，用于将用户可以修改的配置，设置默认值，并将外层配置文件中用户设置的值，用于覆盖更新默认值。
    提供统一的用户配置结果类(字典)
    """
    defaults = {
        # Django Config, Must set before start
        'SECRET_KEY': '',
        'BOOTSTRAP_TOKEN': '',
        'DEBUG': False,
        'LOG_LEVEL': 'DEBUG',
        'LOG_DIR': os.path.join(PROJECT_DIR, 'logs'),
        'DB_ENGINE': 'mysql',
        'DB_NAME': 'jumpserver',
        'DB_HOST': '127.0.0.1',
        'DB_PORT': 3306,
        'DB_USER': 'root',
        'DB_PASSWORD': '',
        'REDIS_HOST': '127.0.0.1',
        'REDIS_PORT': 6379,
        'REDIS_PASSWORD': '',
        # Default value
        'REDIS_DB_CELERY': 3,
        'REDIS_DB_CACHE': 4,
        'REDIS_DB_SESSION': 5,
        'REDIS_DB_WS': 6,

        'GLOBAL_ORG_DISPLAY_NAME': '',
        'SITE_URL': 'http://localhost:8080',
        'CAPTCHA_TEST_MODE': None,
        'TOKEN_EXPIRATION': 3600 * 24,
        'DISPLAY_PER_PAGE': 25,
        'DEFAULT_EXPIRED_YEARS': 70,
        'SESSION_COOKIE_DOMAIN': None,
        'CSRF_COOKIE_DOMAIN': None,
        'SESSION_COOKIE_AGE': 3600 * 24,
        'SESSION_EXPIRE_AT_BROWSER_CLOSE': False,
        'LOGIN_URL': reverse_lazy('authentication:login'),

    }

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, dict.__repr__(self))

    def get_from_config(self, item):
        try:
            value = super().__getitem__(item)
        except KeyError:
            value = None
        return value

    def get(self, item):
        # 从配置文件中获取
        value = self.get_from_config(item)
        if value is not None:
            return value

        return self.defaults.get(item)

    def __getitem__(self, item):
        return self.get(item)

    def __getattr__(self, item):
        return self.get(item)


class ConfigManager:
    """
    配置管理器，用于讲外层的config配置从文件中读取出来，并兼容到默认的Config中，输出最终的配置结果

    主要方法：
        load_user_config： 返回一个Config配置字典类
    """
    config_class = Config

    def __init__(self, root_path=None):
        self.root_path = root_path
        self.config = self.config_class()

    def from_yaml(self, filename, silent=False):
        if self.root_path:
            filename = os.path.join(self.root_path, filename)
        try:
            with open(filename, 'rt', encoding='utf8') as f:
                obj = yaml.safe_load(f)
        except IOError as e:
            if silent and e.errno in (errno.ENOENT, errno.EISDIR):
                return False
            e.strerror = f'Unable to load configuration file ({e.strerror})'
            raise
        if obj:
            return self.from_mapping(obj)
        return True

    def from_mapping(self, *mapping, **kwargs):
        """
        Updates the config like :meth:`update` ignoring items with non-upper keys.

        .. versionadded:: 0.11
        """
        mappings = []
        if len(mapping) == 1:
            if hasattr(mapping[0], 'items'):
                mappings.append(mapping[0].items())
            else:
                mappings.append(mapping[0])
        elif len(mapping) > 1:
            raise TypeError(
                'expected at most 1 positional argument, got %d' % len(mapping)
            )
        mappings.append(kwargs.items())
        for mapping in mappings:
            for (key, value) in mapping:
                if key.isupper():
                    self.config[key] = value
        return True

    def load_from_yaml(self):
        for i in ['config.yml', 'config.yaml']:
            if not os.path.isfile(os.path.join(self.root_path, i)):
                continue
            loaded = self.from_yaml(i)
            if loaded:
                return True
        return False

    @classmethod
    def load_user_config(cls, root_path=None, config_class=None):
        root_path = root_path or PROJECT_DIR
        config_class = config_class or Config
        cls.config_class = config_class

        manager = cls(root_path=root_path)
        if manager.load_from_yaml():
            config = manager.config
        else:
            msg = """

            Error: No config file found.

            You can run `cp config_example.yaml config.yaml`, and edit it.
            """
            raise ImportError(msg)

        return config
