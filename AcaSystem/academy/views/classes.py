from stark.service.v1 import StarkHandler, StarkModelForm, get_datetime_text, get_m2m_text, Option
from academy.models import Classes, UserInfo
from stark.forms.widgets import DateTimePickerInput
from django.utils.safestring import mark_safe
from stark.utils.convert import name2url
from .base import PermissionHandler


class ClassesModelForm(StarkModelForm):
    class Meta:
        model = Classes
        fields = '__all__'
        widgets = {
            'start_date': DateTimePickerInput,
            'graduate_date': DateTimePickerInput,
        }


class ClassesHandler(PermissionHandler, StarkHandler):

    def display_classes(self, obj, is_header, *args, **kwargs):
        if is_header:
            return '班级'
        return str(obj)

    def display_course_record(self, obj, is_header, *args, **kwargs):
        if is_header:
            return '上课记录'
        class_course_record_url = name2url(self.site.namespace, 'academy_courserecord_list', classes_id=obj.pk)
        return mark_safe("<a target='_blank' href='%s'>上课记录</a>" % (class_course_record_url))

    def display_homework(self, obj, is_header, *args, **kwargs):
        if is_header:
            return '班级作业'
        new_url = name2url(self.site.namespace, 'academy_homework_list', classes_id=obj.pk)
        return mark_safe("<a target='_blank' href='%s'>班级作业</a>" % new_url)

    def get_queryset(self, request, *args, **kwargs):
        user_id = request.session['user_info']['id']
        id_queryset = UserInfo.objects.filter(id=user_id).first().roles.all().values_list('id')
        user_role_id_list = [item[0] for item in id_queryset]
        if 10 in user_role_id_list:  #该用户是老师
            return UserInfo.objects.filter(id=user_id).first().classes.all()
        return super().get_queryset(request, *args, **kwargs)


    model_form_class = ClassesModelForm
    list_display = ['school', display_classes, get_m2m_text('老师', 'teacher'), 'price', get_datetime_text('开班日期', 'start_date'),
                    display_course_record, display_homework]
    search_group = [Option('course')]

