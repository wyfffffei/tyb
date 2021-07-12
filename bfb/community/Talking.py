from django.shortcuts import HttpResponse, render
from django.shortcuts import redirect, get_object_or_404
from django.http import Http404, JsonResponse
from bfb import forms
from bfb.community import Articles
from bfb.contest import test_super as te
import datetime
import json
from django.views.decorators.csrf import csrf_exempt


def deadline(day2publish):
    if not isinstance(day2publish, int):
        return None
    now = datetime.datetime.now()
    delay = datetime.timedelta(days=day2publish)
    start = now + delay
    return start


def community(request):
    is_super = te(request)
    thinking_art = Articles.Article.objects.filter(label_tag='thinking')
    section_art = Articles.Article.objects.filter(label_tag='section')
    if not request.session.get('is_login', None):
        return render(request, "admin/community/社区.html/", locals())
    try:
        user = Articles.User.objects.get(name=request.session.get('user_name'))
    except Articles.User.DoesNotExist:
        raise Http404("用户信息错误！")
    else:
        num_up = Articles.ArticleUpDown.objects.filter(user=user, is_up=True).count()
        return render(request, "admin/community/社区.html/", locals())


def articles(request):
    pass


@csrf_exempt
def art_detail(request, art_id):
    """
    :flag: if obj exists?
    :is_me: who can do altering?
    :return: response{'state', 'msg', 'handled'}
    """
    is_super = te(request)
    try:
        article = Articles.Article.objects.get(id=art_id)
        comments = Articles.Comment.objects.filter(article=article)
    except Articles.Article.DoesNotExist:
        raise Http404("文章不存在！")
    else:
        article.content.viewed()
        visitor = request.session.get("user_name")
        online = True
        flag = True
        is_me = True if article.user.name == visitor else False
        user = obj = ""
        try:
            user = Articles.User.objects.get(name=visitor)
            obj = Articles.ArticleUpDown.objects.filter(user=user, article=article).first()
            if obj:
                is_up = obj.is_up
            else:
                flag = False
                is_up = False
        except Articles.User.DoesNotExist:
            online = False
            flag = False
        if request.method == 'POST':
            if online:
                up = request.POST.get('up')
                response = {'state': True, 'msg': None}
                if not flag:
                    ard = Articles.ArticleUpDown.objects.create(user=user, article=article, is_up=True)
                    article.content.num_liked += 1
                    article.content.save(update_fields=['num_liked'])
                    response['handled'] = True
                else:
                    up = True if up == "true" else False
                    obj.is_up = up
                    obj.save(update_fields=['is_up'])
                    if up:
                        article.content.num_liked += 1
                    else:
                        article.content.num_liked -= 1
                    article.content.save(update_fields=['num_liked'])
                    response['handled'] = obj.is_up
            else:
                response = {'state': False, 'msg': "请先登录！"}
            return JsonResponse(response)
        return render(request, "admin/community/文章页.html", locals())


def art_comment(request, art_id):
    try:
        article = Articles.Article.objects.get(id=art_id)
        comments = Articles.Comment.objects.filter(article=article)
    except Articles.Article.DoesNotExist:
        raise Http404("文章不存在！")
    if request.method == "POST":
        if request.session.get('is_login', None):
            user = Articles.User.objects.get(name=request.session['user_name'])
            if Articles.Comment.objects.filter(discusser=user, pub_time__gte=deadline(-1)).count() > 9:
                message = "每日最大评论数为十！"
                return render(request, "admin/community/文章页.html", locals())
            content = request.POST.get("comment")
            if content:
                Articles.Comment.objects.create(article=article, discusser=user, content=content)
                article.content.num_comment += 1
                article.content.save(update_fields=['num_comment'])
            else:
                message = "请提交完整表单！"
            return render(request, "admin/community/文章页.html", locals())
        else:
            return redirect("/bfb/community/login/")
    return redirect(f"/bfb/community/article/article_id%3F={art_id}/")


def art_alter(request, art_id):
    is_super = te(request)
    try:
        art = Articles.Article.objects.get(id=art_id)
    except Articles.Article.DoesNotExist:
        raise Http404("文章不存在！")
    else:
        if request.session.get('is_login', None):
            visitor = request.session.get('user_name')
            if visitor == art.user.name:
                if request.method == "POST":
                    publish_form = forms.PublishForm(request.POST)
                    message = "请检查您填写的内容！"
                    if publish_form.is_valid():
                        user = Articles.User.objects.get(name=visitor)
                        art.headline = publish_form.cleaned_data.get('headline')
                        if user.is_superuser == 1:
                            art.label_tag = publish_form.cleaned_data.get('label_tag')
                        art.save()
                        art.content.body = publish_form.cleaned_data.get('body')
                        if request.FILES.get("picture"):
                            art.content.picture = request.FILES.get("picture")
                        art.content.save()
                        return redirect('/bfb/community/')
                    return render(request, "admin/community/修改页.html", locals())
                publish_form = forms.PublishForm()
                return render(request, "admin/community/修改页.html", locals())
            else:
                return HttpResponse("权限不足！")
        else:
            return redirect('/bfb/community/login/')


def art_publish(request):
    is_super = te(request)
    if request.session.get('is_login', None):
        if request.method == 'POST':
            publish_form = forms.PublishForm(request.POST)
            message = '请检查您填写的内容！'
            if publish_form.is_valid():
                user = Articles.User.objects.get(name=request.session['user_name'])
                print(Articles.Article.objects.filter(user=user, pub_time__gte=deadline(-1)).count())
                if Articles.Article.objects.filter(user=user, pub_time__gte=deadline(-1)).count() > 2:
                    message = "每日最大发文数为三！"
                    return render(request, "admin/community/发布页面.html", locals())
                headline = publish_form.cleaned_data.get('headline')
                body = publish_form.cleaned_data.get('body')
                label_tag = publish_form.cleaned_data.get('label_tag')
                picture = request.FILES.get("picture")
                new_article = Articles.Article.article_init(headline, body, picture)
                if new_article:
                    if user.is_superuser == 1 and label_tag == Articles.Article.label_choices[0][0]:
                        new_article.label_tag = label_tag
                    new_article.website = f'/bfb/community/article/article_id%3F={new_article.id}/'
                    new_article.save()
                    if user.publish(new_article):
                        return redirect('/bfb/community/')
            return render(request, "admin/community/发布页面.html", locals())
        publish_form = forms.PublishForm()
        return render(request, "admin/community/发布页面.html", locals())
    else:
        return redirect('/bfb/community/login/')


def art_delete(request, art_id):
    try:
        article = Articles.Article.objects.get(id=art_id)
    except Articles.Article.DoesNotExist:
        raise Http404("文章不存在！")
    else:
        if request.session.get('is_login', None):
            if request.session['user_id'] == article.user.id:
                if request.session['user_name'] == article.user.name:
                    article.delete()
            return redirect("/bfb/community/")
        else:
            return redirect("/bfb/community/login/")
