from stark.service.v1 import StarkHandler, get_choice_text, get_m2m_text, StarkModelForm
from academy.models import Customer, ConsultRecord
from django.utils.safestring import mark_safe
from stark.utils.convert import name2url
from .base import PermissionHandler


class PublicCustomerModelForm(StarkModelForm):
    class Meta:
        model = Customer
        exclude = ['consultant', ]


class PriCustomerHandler(PermissionHandler, StarkHandler):

    def contact(self, obj, is_header):
        if is_header:
            return '跟进'
        contact_url = name2url(self.site.namespace, "academy_consultrecord_list", customer_id=obj.pk)
        return mark_safe("<a target='_blank' href='%s'>跟进</a>" % contact_url)

    def pay_record(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '缴费'
        record_url = name2url(self.site.namespace,'academy_paymentrecord_list', customer_id=obj.pk)
        return mark_safe('<a target="_blank" href="%s">缴费</a>' % record_url)

    def multi_remove_to_pub(self, request, *args, **kwargs):
        consult_id = request.session['user_info']['id']
        customer_id_list = request.POST.getlist('pk')
        Customer.objects.filter(id__in=customer_id_list, consultant_id=consult_id).update(consultant_id=None)

    multi_remove_to_pub.text = "移除到公户"
    list_display = [StarkHandler.display_checkbox, 'name',get_choice_text('性别', 'gender'), 'qq', get_m2m_text('咨询课程', 'course'),
                    get_choice_text('状态', 'status'), contact, pay_record]

    def get_queryset(self, request, *args, **kwargs):
        consult_id = request.session['user_info']['id']
        return Customer.objects.filter(consultant_id=consult_id)

    action_list = [multi_remove_to_pub]