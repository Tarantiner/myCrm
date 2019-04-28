from stark.service.v1 import StarkHandler
from django.conf.urls import url
from .base import PermissionHandler


class DepartHandler(PermissionHandler, StarkHandler):

    list_display = ['title', ]

    def get_urls(self):
        patterns = [
            url(r'^list/$', self.wrapper(self.changelist_view), name=self.get_list_url_name),
            url(r'^add/$', self.wrapper(self.add_view), name=self.get_add_url_name),
            url(r'^change/(?P<pk>\d+)/$', self.wrapper(self.change_view), name=self.get_change_url_name),
        ]

        return patterns

