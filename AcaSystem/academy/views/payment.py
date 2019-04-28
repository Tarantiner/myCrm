from django.conf.urls import url
from django.shortcuts import HttpResponse
from django import forms
from stark.service.v1 import StarkHandler, get_choice_text, StarkModelForm
from academy.models import PaymentRecord, Customer, Student, UserInfo
from .base import PermissionHandler
from stark.utils.md import to_md


class PaymentRecordModelForm(StarkModelForm):
    class Meta:
        model = PaymentRecord
        fields = ['pay_type', 'paid_fee', 'classes', 'note']


class StudentPaymentRecordModelForm(StarkModelForm):
    qq = forms.CharField(label='QQ号', max_length=32)
    mobile = forms.CharField(label='手机号', max_length=32)
    emergency_contract = forms.CharField(label='紧急联系人电话', max_length=32)

    class Meta:
        model = PaymentRecord
        fields = ['pay_type', 'paid_fee', 'classes', 'qq', 'mobile', 'emergency_contract', 'note']


class PaymentHandler(PermissionHandler, StarkHandler):
    list_display = [get_choice_text('缴费类型', 'pay_type'), 'paid_fee', 'classes', 'consultant',
                    get_choice_text('状态', 'confirm_status')]

    def get_urls(self):
        patterns = [
            url(r'^list/(?P<customer_id>\d+)/$', self.wrapper(self.changelist_view), name=self.get_list_url_name),
            url(r'^add/(?P<customer_id>\d+)/$', self.wrapper(self.add_view), name=self.get_add_url_name),
        ]
        patterns.extend(self.extra_urls())
        return patterns

    def get_queryset(self, request, *args, **kwargs):
        customer_id = kwargs.get('customer_id')
        consult_id = request.session['user_info']['id']
        return self.model_class.objects.filter(customer_id=customer_id, customer__consultant_id=consult_id)

    def get_model_form_class(self, is_add, request, *args, **kwargs):
        # 如果当前客户有学生信息，则使用PaymentRecordModelForm；否则StudentPaymentRecordModelForm
        customer_id = kwargs.get('customer_id')
        student_exists = Student.objects.filter(customer_id=customer_id).exists()
        if student_exists:
            return PaymentRecordModelForm
        return StudentPaymentRecordModelForm

    def save(self, form, is_update, request, *args, **kwargs):
        customer_id = kwargs.get('customer_id')
        consult_id = request.session['user_info']['id']
        object_exists = Customer.objects.filter(id=customer_id,
                                                       consultant_id=consult_id).exists()
        if not object_exists:
            return HttpResponse('非法操作')

        form.instance.customer_id = customer_id
        form.instance.consultant_id = consult_id
        # 创建缴费记录信息
        form.save()

        # 创建学员信息
        classes = form.cleaned_data['classes']
        fetch_student_object = Student.objects.filter(customer_id=customer_id).first()
        if not fetch_student_object:
            #先创建用户信息
            new_user_obj = Customer.objects.filter(id=customer_id).first()
            name, gender, phone = new_user_obj.name, new_user_obj.gender, request.POST.get('mobile')
            default_student_pwd = to_md('123')
            user_obj = UserInfo(name=name, password=default_student_pwd, gender=gender, phone=phone, depart_id=4)
            user_obj.save()
            user_obj.roles.add(12)  #具体指数据库中角色id,一般不会改变
            qq = form.cleaned_data['qq']
            mobile = form.cleaned_data['mobile']
            emergency_contract = form.cleaned_data['emergency_contract']
            student_object = Student.objects.create(user_id=user_obj.id, customer_id=customer_id, qq=qq, mobile=mobile,
                                                           emergency_contract=emergency_contract)
            student_object.classes.add(classes.id)
        else:
            fetch_student_object.classes.add(classes.id)
