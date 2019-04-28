from stark.service.v1 import StarkHandler, StarkModelForm, get_choice_text, Option
from academy.models import UserInfo
from django import forms
from django.core.exceptions import ValidationError
from stark.utils.md import to_md
from django.utils.safestring import mark_safe
from django.conf.urls import url
from django.shortcuts import render, redirect, HttpResponse
from .base import PermissionHandler


class UserInfoAddModelForm(StarkModelForm):
    confirm_pwd = forms.CharField(label='确认密码')
    email = forms.CharField(required=False)

    class Meta:
        model = UserInfo
        fields = ['name', 'password', 'confirm_pwd', 'gender', 'phone', 'depart', 'roles', 'email' ]

    def clean_confirm_pwd(self):
        if self.cleaned_data['password'] != self.cleaned_data['confirm_pwd']:
            raise ValidationError('两次密码不一致')
        return self.cleaned_data['confirm_pwd']

    def clean(self):
        password = self.cleaned_data.get('password')
        if password:
            self.cleaned_data['password'] = to_md(password)
        return self.cleaned_data


class UserInfoEditModelForm(StarkModelForm):
    email = forms.CharField(required=False)

    class Meta:
        model = UserInfo
        fields = ['name', 'gender', 'phone', 'depart', 'roles', 'email']


class ResetPwdModelForm(StarkModelForm):
    confirm_pwd = forms.CharField(label='确认密码')
    class Meta:
        model = UserInfo
        fields = ['password']

    def clean_confirm_pwd(self):
        if self.cleaned_data['password'] != self.cleaned_data['confirm_pwd']:
            raise ValidationError('两次密码不一致')
        return self.cleaned_data['confirm_pwd']

    def clean(self):
        password = self.cleaned_data.get('password')
        if password:
            self.cleaned_data['password'] = to_md(password)
        return self.cleaned_data


class UserInfolHandler(PermissionHandler, StarkHandler):
    order_list = ['depart_id',]
    search_list = ['name__contains']
    search_group = [
        Option(field='gender', is_multi=True),
        Option(field='depart'),
    ]

    def reset_user_pwd(title):
        from stark.utils.convert import name2url
        def inner(self, obj=None, is_header=None, *args, **kwargs):
            if is_header:
                return title
            return mark_safe("<a href='%s'>%s</a>" % (name2url(self.site.namespace, self.get_url_name('reset_pwd'), pk=obj.pk), title))
        return inner

    list_display = ['name',get_choice_text('性别', 'gender'), 'phone', 'depart', reset_user_pwd('重置密码'),]

    def get_model_form_class(self, is_add, request, *args, **kwargs):
        if is_add:
            return UserInfoAddModelForm
        else:
            return UserInfoEditModelForm

    def reset_pwd(self, request, pk, *args, **kwargs):
        user_obj = UserInfo.objects.filter(id=pk).first()
        if not user_obj:
            return HttpResponse('user does not exist!')
        form = ResetPwdModelForm()
        if request.method == 'GET':
            return render(request, 'stark/change.html', {'form': form})
        form = ResetPwdModelForm(data=request.POST)
        if form.is_valid():
            pwd = form.cleaned_data['password']
            user_obj.password = pwd
            user_obj.save()
            # 在数据库保存成功后，跳转回列表页面(携带原来的参数)。
            return redirect(self.reverse_list_url())
        return render(request, 'stark/change.html', {'form': form})

    def extra_urls(self):
        patterns = [
            url(r'^resetpwd/(?P<pk>\w+)/$', self.wrapper(self.reset_pwd), name=self.get_url_name('reset_pwd')),
        ]
        return patterns


