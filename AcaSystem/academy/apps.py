from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules


class AcademyConfig(AppConfig):
    name = 'academy'
    
    def ready(self):
        """
        钩子函数，在django启动自动执行每个注册app里的stark.py模块
        :return:
        """
        autodiscover_modules('stark')
