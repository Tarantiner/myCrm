from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from rbac.service.init_permission import init_permission
from django.conf import settings
from stark.utils.md import to_md
from django.utils.module_loading import import_string


COUNT = 0


def get_valid_code(request):
    """
    获取验证码
    """
    from PIL import Image, ImageDraw, ImageFont
    from io import BytesIO
    import random
    import string
    # 先生成一张颜色随机的图片

    def get_num(x, y, n):
        return random.sample(list(range(x, y)), n)

    image = Image.new('RGB', (250, 40), tuple(get_num(0, 256, 3)))    # 颜色随机的图片
    # 给图片加上验证字符
    draw = ImageDraw.Draw(image)   # 可对图片操作的draw对象
    font = ImageFont.truetype('rbac\static\\fonts\\nyctophobia.ttf', size=32)    #字体
    choices = string.digits + string.ascii_letters     # 生成验证码筛选范围
    code = random.sample(choices, 5)  # 验证码内容
    for i, v in enumerate(code):
        draw.text((24 + i * 30, 0), v, tuple(get_num(0, 256, 3)), font=font)   # 坐标位置，验证码内容，颜色，字体
    # 存到内存中
    f = BytesIO()
    image.save(f, 'png')
    data = f.getvalue()
    f.close()
    s_code = ''.join(code)
    request.session['valid_str'] = s_code
    return HttpResponse(data)


def login(request):
    global COUNT
    if request.is_ajax():
        res = {'state': False, 'msg': None}
        if COUNT < settings.MAX_PASS_TRY:
            valid_code = request.POST.get('valid_code')
            right_code = request.session.get('valid_str')
            if valid_code.upper() == right_code.upper():
                name = request.POST.get('name')
                pwd = request.POST.get('pwd')
                md_pwd = to_md(pwd)
                UserInfoModel = import_string(settings.RBAC_USER_MODLE_CLASS)
                user = UserInfoModel.objects.filter(name=name, password=md_pwd).first()
                if not user:     # 用户名或密码错误
                    COUNT += 1
                    res['msg'] = '用户名或密码错误'
                    return JsonResponse(res)
                COUNT = 0     # 输入都正确，计数清零
                init_permission(user, request)
                request.session['user_info'] = {'id': user.id}
                res['state'], res['msg'] = True, '登录成功'
                return JsonResponse(res)
            COUNT += 1     # 验证码有误
            res['msg'] = '验证码错误'
            return JsonResponse(res)
        res['msg'] = 'too much try'
        return JsonResponse(res)

    return render(request, 'login.html')


def logout(request):
    request.session.delete()
    return redirect('/login/')


def index(request):
    return render(request, 'index.html')


def person_information(request):
    user_id = request.session['user_info']['id']
    UserInfoModel = import_string(settings.RBAC_USER_MODLE_CLASS)
    user_obj = UserInfoModel.objects.filter(id=user_id).first()
    return render(request, 'userinfo.html', {'user': user_obj})
