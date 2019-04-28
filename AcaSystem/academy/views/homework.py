from stark.service.v1 import StarkHandler, StarkModelForm, get_datetime_text
from academy.models import Homework, HomeworkScore, Classes
from django.conf.urls import url
from django.utils.safestring import mark_safe
from stark.utils.convert import name2url
from django.forms.models import modelformset_factory
from django.shortcuts import render, HttpResponse
from .base import PermissionHandler


class HomeworkModelForm(StarkModelForm):
    class Meta:
        model = Homework
        exclude = ['classes']


class HomeworkScoreModelForm(StarkModelForm):
    class Meta:
        model = HomeworkScore
        fields = ['score']


class HomeworkHandler(PermissionHandler, StarkHandler):

    def display_edit_del(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '操作'
        classes_id = kwargs.get('classes_id')
        tpl = '<a href="%s">编辑</a> <a href="%s">删除</a>' % (
            self.reverse_change_url(pk=obj.pk, classes_id=classes_id),
            self.reverse_delete_url(pk=obj.pk, classes_id=classes_id))
        return mark_safe(tpl)

    def get_homeworkscore(self, obj, is_header, *args, **kwargs):
        if is_header:
            return '成绩'
        homework_score_url = name2url(self.site.namespace, self.get_url_name('homeworkscore'),
                                      classes_id=kwargs.get('classes_id'), homework_id=obj.pk)
        return mark_safe("<a target='_blank' href='%s'>成绩</a>" % homework_score_url)

    @property
    def get_homeworkscore_url_name(self):
        return self.get_url_name('homeworkscore')

    def multi_init_score_system(self, request, *args, **kwargs):
        homework_id_list = request.POST.getlist('pk')
        classes_id = kwargs.get('classes_id')
        classes_obj = Classes.objects.filter(id=classes_id).first()
        if not classes_id:
            return HttpResponse('班级不存在')
        student_queryset = classes_obj.student_set.all()
        for homework_id in homework_id_list:
            if not Homework.objects.filter(id=homework_id).exists():
                continue
            if HomeworkScore.objects.filter(homework_id=homework_id).exists():
                continue
            homeworkscore_list = [HomeworkScore(homework_id=homework_id, student_id=student.id, classes_id=classes_id) for student in student_queryset]
            HomeworkScore.objects.bulk_create(homeworkscore_list, batch_size=50)

    multi_init_score_system.text = '批量初始化作业成绩'

    def homeworkscore_view(self, request, *args, **kwargs):
        homework_id = kwargs.get('homework_id')
        classes_id = kwargs.get('classes_id')
        homeworkscore_list = HomeworkScore.objects.filter(homework_id=homework_id, classes_id=classes_id)
        form_class = modelformset_factory(model=HomeworkScore, form=HomeworkScoreModelForm, extra=0)
        if request.method == 'POST':
            formset = form_class(queryset=homeworkscore_list, data=request.POST)
            if formset.is_valid():
                formset.save()
                return render(request, 'homeworkscore.html', {'formset': formset})
        formset = form_class(queryset=homeworkscore_list)
        return render(request, 'homeworkscore.html', {'formset': formset})


    def get_urls(self):
        patterns = [
            url(r'^list/(?P<classes_id>\d+)$', self.wrapper(self.changelist_view), name=self.get_list_url_name),
            url(r'^add/(?P<classes_id>\d+)$', self.wrapper(self.add_view), name=self.get_add_url_name),
            url(r'^change/(?P<classes_id>\d+)/(?P<pk>\d+)/$', self.wrapper(self.change_view), name=self.get_change_url_name),
            url(r'^delete/(?P<classes_id>\d+)/(?P<pk>\d+)/$', self.wrapper(self.delete_view), name=self.get_delete_url_name),
            url(r'^score/(?P<classes_id>\d+)/(?P<homework_id>\d+)/$', self.wrapper(self.homeworkscore_view), name=self.get_homeworkscore_url_name),
        ]
        return patterns

    def get_queryset(self, request, *args, **kwargs):
        classes_id = kwargs.get('classes_id')
        return Homework.objects.filter(classes_id=classes_id)

    def save(self, form, is_update, *args, **kwargs):
        classes_id = kwargs.get('classes_id')
        form.instance.classes_id = classes_id
        form.save()

    model_form_class = HomeworkModelForm
    list_display = [StarkHandler.display_checkbox, 'classes', 'title', get_datetime_text('发布日期', 'publish_date'), get_homeworkscore]
    action_list = [multi_init_score_system]