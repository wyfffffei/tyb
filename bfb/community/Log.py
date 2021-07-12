from django.shortcuts import HttpResponse,render
from django.shortcuts import redirect,get_object_or_404
from django.conf import settings
from django.http import Http404
from bfb import forms
from bfb.community import Articles
import datetime
import hashlib


# 定义哈希算法加密
def hash_code(s, salt='key'):
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())
    return h.hexdigest()


# 邮箱验证码
def make_confirm_string(user):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = hash_code(user.name, now)
    Articles.ConfirmString.objects.create(code=code, user=user)
    return code


def send_email(email, code):
    from django.core.mail import EmailMultiAlternatives
    subject = '来自sityb.cm的注册确认邮件'
    text_content = "感谢注册！您的确认码为'{}'，请妥善保存并在收到邮箱{}天内进行注册确认~".format(code, settings.CONFIRM_DAYS)
    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.send()


def login(request):
    if request.session.get('is_login', None):    # 不允许重复登录
        return redirect('/bfb/community/')
    if request.method == "POST":
        login_form = forms.UserForm(request.POST)
        message = '用户名或密码错误！'
        if login_form.is_valid():
            # 用户名字符合法性验证
            # 密码长度验证
            # 更多的其它验证.....（几乎全部包括）
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            try:
                user = Articles.User.objects.get(name=username)
            except Articles.User.DoesNotExist:
                return render(request, "admin/community/登录.html", locals())
            if user.password == hash_code(password):
                if not user.has_confirmed:
                    message = '该用户信息未经邮件确认！'
                    return render(request, "admin/community/登录.html", locals())
                request.session.flush()
                request.session['is_login'] = True
                request.session['user_id'] = user.id
                request.session['user_name'] = user.name
                request.session['last_login'] = user.last_login
                request.session['is_superuser'] = user.is_superuser
                if user.is_superuser == 1:
                    return redirect("/bfb/management/")
                else:
                    return redirect('/bfb/community/')
            else:
                return render(request, "admin/community/登录.html", locals())
        else:
            return render(request, "admin/community/登录.html", locals())
    login_form = forms.UserForm()
    return render(request, "admin/community/登录.html", locals())


def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect('/bfb/community/login/')
    user = Articles.User.objects.get(name=request.session['user_name'])
    now_time = datetime.datetime.today().strftime('%Y-%m-%d %H:%M')
    user.last_login = now_time
    user.save()
    request.session.flush()             # 清空所有session内容
    # 或者使用下面的方法
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']...
    return redirect('/bfb/community/login/')


def register(request):
    if request.session.get('is_login', None):
        return redirect('/bfb/community/')
    if request.method == 'POST':
        register_form = forms.RegisterForm(request.POST)
        message = '请检查您填写的内容！'
        if register_form.is_valid():
            username = register_form.cleaned_data.get('username')
            password1 = register_form.cleaned_data.get('password1')
            password2 = register_form.cleaned_data.get('password2')
            email = register_form.cleaned_data.get('email')
            sex = register_form.cleaned_data.get('sex')

            if password1 != password2:
                message = '两次输入的密码不一致！'
                return render(request, "admin/community/注册.html", locals())
            else:
                same_name_user = Articles.User.objects.filter(name=username)
                if same_name_user:
                    message = '该用户名已经存在！'
                    return render(request, "admin/community/注册.html", locals())
                same_email_user = Articles.User.objects.filter(email=email)
                if same_email_user:
                    message = '该邮箱已经被注册！'
                    return render(request, "admin/community/注册.html",locals())
                # 用户注册信息存入数据库
                new_user = Articles.User()
                new_user.name = username
                new_user.password = hash_code(password1)
                new_user.email = email
                new_user.sex = sex
                now_time = datetime.datetime.today().strftime('%Y-%m-%d %H:%M')
                new_user.cre_time = now_time
                new_user.save()
                code = make_confirm_string(new_user)
                send_email(email, code)
                return redirect('/bfb/confirm/')
        else:
            return render(request, "admin/community/注册.html", locals())
    register_form = forms.RegisterForm()
    return render(request, "admin/community/注册.html", locals())


def user_confirm(request):
    if request.method == 'POST':
        code = request.POST.get("code")
        try:
            confirm = Articles.ConfirmString.objects.get(code=code)
        except Articles.ConfirmString.DoesNotExist:
            message = "无效的确认请求！"
            return render(request, "admin/community/user_confirm.html", locals())
        else:
            c_time = confirm.c_time
            now = datetime.datetime.now()
            if now > c_time + datetime.timedelta(settings.CONFIRM_DAYS):
                confirm.user.delete()
                message = '您的邮件已经过期！请重新注册！'
                return render(request, 'admin/community/注册.html', locals())
            else:
                confirm.user.has_confirmed = True
                confirm.user.save()
                confirm.delete()
                return redirect('/bfb/community/login/')
    return render(request, "admin/community/user_confirm.html", locals())
