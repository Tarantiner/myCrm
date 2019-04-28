from stark.service.v1 import StarkHandler
from .base import PermissionHandler


class CourseHandler(PermissionHandler, StarkHandler):
    list_display = ['title',]

