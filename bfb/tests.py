import os
from django.core.mail import send_mail
os.environ['DJANGO_SETTINGS_MODULE'] = 'tyb.settings'

# def make_confirm_string(user):
#     now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     code = hash_code(user.name, now)
#     Articles.ConfirmString.objects.create(code=code, user=user)
#     return code

# def send_email(email, code):
#     from django.core.mail import EmailMultiAlternatives
#     subject = '来自sityb.com的注册确认邮件'
#     text_content = "感谢注册！您的确认码为'{}'，请妥善保存并在收到邮箱{}天内进行注册确认~".format(code, 7)
#     msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
#     msg.send()

# if __name__ == '__main__':
#     code = "xxxxxxxxxxxx"
#     send_email('xxx@qq.com', code)
