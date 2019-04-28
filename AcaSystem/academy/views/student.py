from django.conf.urls import url
from django.utils.safestring import mark_safe
from stark.service.v1 import StarkHandler, get_choice_text, get_m2m_text, StarkModelForm, Option
from academy.models import Student, UserInfo, HomeworkScore
from stark.utils.convert import name2url
from .base import PermissionHandler
from django.shortcuts import render


class StudentModelForm(StarkModelForm):
    class Meta:
        model = Student
        fields = ['qq', 'mobile', 'emergency_contract', 'memo']


class StudentHandler(PermissionHandler, StarkHandler):

    model_form_class = StudentModelForm

    @property
    def current_user(self):
        user_id = self.request.session['user_info']['id']
        user_obj = UserInfo.objects.filter(id=user_id).first()
        return user_obj

    @property
    def get_myclasses_url_name(self):
        return self.get_url_name('myclasses')

    @property
    def get_myhomeworkscore_url_name(self):
        return self.get_url_name('homeworkscore')

    def display_score(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '积分管理'
        if self.current_user.depart_id == 4:
            return f'{obj.score}'
        record_url = name2url(self.site.namespace, "academy_scorerecord_list", student_id=obj.pk)
        return mark_safe('<a target="_blank" href="%s">%s</a>' % (record_url, obj.score))

    def get_myclasses_view(self, request, *args, **kwargs):
        student_id = kwargs.get('student_id')
        classes = Student.objects.filter(id=student_id).first().classes.all()
        return render(request, 'myclasses.html', {'classes': classes, 'student_id': student_id})

    def get_homeworkscore_view(self, request, *args, **kwargs):
        student_id = kwargs.get('student_id')
        classes_id = kwargs.get('classes_id')
        homeworkscore_queryset = HomeworkScore.objects.filter(classes_id=classes_id, student_id=student_id).all()
        return render(request, 'check_homeworkscore.html', {'score_queryset': homeworkscore_queryset})

    def display_myclasses(self, obj, is_header, *args, **kwargs):
        if is_header:
            return '我的课程'
        myclasses_url = name2url(self.site.namespace, self.get_myclasses_url_name, student_id=obj.pk)
        return mark_safe('<a href="%s">我的课程</a>' % (myclasses_url))

    list_display = ['customer', 'qq', 'mobile', 'emergency_contract', get_m2m_text('已报班级', 'classes'),
                    display_score, get_choice_text('状态', 'student_status'),]
    has_add_btn = False

    def get_urls(self):
        patterns = [
            url(r'^list/$', self.wrapper(self.changelist_view), name=self.get_list_url_name),
            url(r'^change/(?P<pk>\d+)/$', self.wrapper(self.change_view), name=self.get_change_url_name),
            url(r'^myclasses/(?P<student_id>\d+)/$', self.wrapper(self.get_myclasses_view), name=self.get_myclasses_url_name),
            url(r'^myclasses/homeworkscore/(?P<student_id>\d+)/(?P<classes_id>\d+)/$', self.wrapper(self.get_homeworkscore_view), name=self.get_myhomeworkscore_url_name)
        ]
        return patterns

    search_list = ['customer__name', 'qq', 'mobile', ]

    search_group = [
        Option('classes', text_func=lambda x: '%s-%s' % (x.school.title, str(x)))
    ]

    def get_queryset(self, request, *args, **kwargs):
        if self.current_user.depart_id == 4:
            student_id = Student.objects.filter(user_id=self.current_user.id)
            return Student.objects.filter(id=student_id)
        return super().get_queryset(request, *args, **kwargs)

    def get_search_group(self):
        if self.current_user.depart_id == 4:
            return []
        return self.search_group

    def get_search_list(self):
        if self.current_user.depart_id == 4:
            return []
        return self.search_list

    def get_list_display(self, request, *args, **kwargs):
        if self.current_user.depart_id == 4:
            self.list_display[4]=type(self).display_myclasses
        return self.list_display