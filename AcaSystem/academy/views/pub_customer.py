from stark.service.v1 import StarkHandler, get_choice_text, get_m2m_text, StarkModelForm
from academy.models import Customer, ConsultRecord
from django.shortcuts import HttpResponse, render
from django.utils.safestring import mark_safe
from django.conf.urls import url
from stark.utils.convert import name2url
from django.db import transaction
from .base import PermissionHandler


class PublicCustomerModelForm(StarkModelForm):
    class Meta:
        model = Customer
        exclude = ['consultant', ]


class PubCustomerHandler(PermissionHandler, StarkHandler):

    def check_record(self, obj, is_header):
        if is_header:
            return '跟进记录'
        record_url = name2url(self.site.namespace, self.get_url_name('record'), pk=obj.pk)
        return mark_safe("<a href='%s'>跟进记录</a>" % record_url)

    list_display = [StarkHandler.display_checkbox, 'name', get_choice_text('性别', 'gender'),  'qq', get_m2m_text('课程', 'course'), get_choice_text('状态', 'status'),
                    check_record]

    def get_queryset(self, request, *args, **kwargs):
        return self.model_class.objects.filter(consultant__isnull=True)

    def multi_add_to_priv(self, request, *args, **kwargs):
        consult_id = request.session['user_info']['id']
        pk_list = request.POST.getlist('pk')

        private_customer_count = Customer.objects.filter(consultant_id=consult_id, status=2).count()

        # 私户个数限制
        if (private_customer_count + len(pk_list)) > Customer.MAX_PRIVATE_CUSTOMER_COUNT:
            return HttpResponse('做人不要太贪心，私户中已有%s个客户，最多只能申请%s' % (
                private_customer_count, Customer.MAX_PRIVATE_CUSTOMER_COUNT - private_customer_count))
        flag = False
        with transaction.atomic():  # 事务
            # 在数据库中加锁
            origin_queryset = Customer.objects.filter(id__in=pk_list, status=2,
                                                             consultant__isnull=True).select_for_update()
            if len(origin_queryset) == len(pk_list):
                Customer.objects.filter(id__in=pk_list, status=2,
                                               consultant__isnull=True).update(consultant_id=consult_id)
                flag = True
        if not flag:
            return HttpResponse('手速太慢了，选中的客户已被其他人申请，请重新选择')
    multi_add_to_priv.text = '批量加入私户'

    def get_record(self, request, pk):
        record_list = ConsultRecord.objects.filter(customer_id=pk)
        return render(request, 'record.html', {'record_list': record_list})

    def extra_urls(self):
        patterns = [
            url(r'^record/(?P<pk>\w+)', self.wrapper(self.get_record), name=self.get_url_name('record'))
        ]
        return patterns
    model_form_class = PublicCustomerModelForm
    action_list = [multi_add_to_priv]



