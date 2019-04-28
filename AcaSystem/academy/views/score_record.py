from django.conf.urls import url
from stark.service.v1 import StarkHandler, StarkModelForm
from academy.models import ScoreRecord
from .base import PermissionHandler


class ScoreModelForm(StarkModelForm):
    class Meta:
        model = ScoreRecord
        fields = ['content', 'score', ]


class ScoreHandler(PermissionHandler, StarkHandler):
    list_display = ['content', 'score', 'user']
    model_form_class = ScoreModelForm

    def get_urls(self):
        patterns = [
            url(r'^list/(?P<student_id>\d+)/$', self.wrapper(self.changelist_view), name=self.get_list_url_name),
            url(r'^add/(?P<student_id>\d+)/$', self.wrapper(self.add_view), name=self.get_add_url_name),
        ]
        patterns.extend(self.extra_urls())
        return patterns

    def get_queryset(self, request, *args, **kwargs):
        student_id = kwargs.get('student_id')
        return self.model_class.objects.filter(student_id=student_id)

    def save(self, form, is_update, request, *args, **kwargs):
        student_id = kwargs.get('student_id')
        current_user_id = request.session['user_info']['id']
        form.instance.student_id = student_id
        form.instance.user_id = current_user_id
        form.save()
        score = form.instance.score
        if score > 0:
            form.instance.student.score += abs(score)
        else:
            form.instance.student.score -= abs(score)
        form.instance.student.save()
