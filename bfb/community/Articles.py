from django.db import models
from django.db import transaction


class User(models.Model):
    gender = (('male', "男"), ('female', "女"), ('undefined', "说不好"))
    name = models.CharField(max_length=128, unique=True, verbose_name="用户名")
    password = models.CharField(max_length=256, verbose_name="密码")
    email = models.EmailField(unique=True, verbose_name="邮箱")
    sex = models.CharField(max_length=24, choices=gender, default=gender[2][0], verbose_name="性别")
    cre_time = models.DateTimeField(auto_now_add=True, verbose_name="注册时间")
    last_login = models.CharField(max_length=24, default=None, null=True, verbose_name="上次登陆时间")
    is_superuser = models.IntegerField(default=0, choices=((0, '普通用户'), (1, '超级用户')), verbose_name="是否超级用户")
    has_confirmed = models.BooleanField(default=False)

    def publish(self, article):
        if article:
            article.user = self
            article.save()
            return 1
        else:
            return 0

    class Meta:
        verbose_name = '社区用户'
        verbose_name_plural = '社区用户'
        ordering = ["-cre_time"]

    def __str__(self):
        return self.name


class ConfirmString(models.Model):
    code = models.CharField(max_length=256)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    c_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '验证码'
        verbose_name_plural = '验证码'
        ordering = ['-c_time']

    def __str__(self):
        return self.user.name + ": " + self.code


class Article(models.Model):
    label_choices = (('section', '专栏'), ('thinking', '想法'))
    headline = models.TextField(max_length=128, verbose_name="标题")
    website = models.URLField(max_length=128, null=True, verbose_name="网页链接")
    pub_time = models.DateTimeField(auto_now_add=True, verbose_name="发布时间")
    label_tag = models.CharField(max_length=20, choices=label_choices, default=label_choices[1][0], verbose_name="标签")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    @classmethod
    def article_init(cls, headline, body, picture):
        if not headline or not body:
            return None
        else:
            with transaction.atomic():
                new_article = cls(headline=headline)
                new_article.save()
                Content(art=new_article, body=body, picture=picture).save()
            return new_article

    class Meta:
        verbose_name = "文章"
        verbose_name_plural = "文章"
        ordering = ["-pub_time"]

    def __str__(self):
        return self.headline


class Content(models.Model):
    body = models.TextField(blank=True, verbose_name="正文")
    picture = models.ImageField(upload_to="image/", null=True, verbose_name="配图")
    num_liked = models.PositiveSmallIntegerField(default=0, verbose_name="点赞数")
    num_comment = models.PositiveSmallIntegerField(default=0, verbose_name="评论数")
    num_visited = models.PositiveSmallIntegerField(default=0, verbose_name="浏览次数")
    art = models.OneToOneField(Article, on_delete=models.CASCADE)

    def viewed(self):
        self.num_visited += 1
        self.save(update_fields=['num_visited'])

    class Meta:
        verbose_name = "文章内容"
        verbose_name_plural = "文章内容"

    def __str__(self):
        return self.art.headline


class Comment(models.Model):
    content = models.CharField(max_length=512, verbose_name="内容")
    pub_time = models.DateTimeField(auto_now_add=True, verbose_name="评论时间")
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True)
    discusser = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "评论"
        verbose_name_plural = "评论"
        ordering = ["-pub_time"]

    def __str__(self):
        return self.article.headline


class ArticleUpDown(models.Model):
    is_up = models.BooleanField(default=False, verbose_name="点赞？")
    c_time = models.DateTimeField(auto_now_add=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name="文章")
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "点赞详情"
        verbose_name_plural = "点赞详情"

    def __str__(self):
        return self.article.headline + "|" + self.user.name + ":" + str(self.is_up)

