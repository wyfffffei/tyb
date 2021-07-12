from django import forms
from captcha.fields import CaptchaField
from . import Match
from bfb.community import Articles


# 登录表单
class UserForm(forms.Form):
    username = forms.CharField(label="用户名", max_length=128, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': "用户名", 'autofocus': ''}))
    password = forms.CharField(label="密码", max_length=256,widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': "密码"}))
    captcha = CaptchaField(label="验证码")


# 注册表单
class RegisterForm(forms.Form):
    username = forms.CharField(label="用户名", max_length=128, widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    password1 = forms.CharField(label="密码", max_length=256, widget=forms.PasswordInput(
        attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="确认密码", max_length=256, widget=forms.PasswordInput(
        attrs={'class': 'form-control'}))
    email = forms.EmailField(label="邮箱地址", widget=forms.EmailInput(
        attrs={'class': 'form-control'}))
    sex = forms.ChoiceField(label="性别", choices=Articles.User.gender, widget=forms.Select(
        attrs={'class': 'form-control'}))
    captcha = CaptchaField(label="验证码")


# 文章
class PublishForm(forms.Form):
    headline = forms.CharField(label="标题", max_length=20, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '标题', 'autofocus': ''}))
    body = forms.CharField(label="内容", max_length=1024, widget=forms.Textarea(
        attrs={'class': 'form-control', 'placeholder': '正文', 'rows': '15'}))
    picture = forms.FileField(label="配图", required=False, widget=forms.FileInput(
        attrs={'class': 'form-control'}))
    label_tag = forms.ChoiceField(label="文章标签", choices=Articles.Article.label_choices, widget=forms.Select(
        attrs={'class': 'form-control'}))


# 比赛基本信息
class GameAlterForm(forms.Form):
    match_name = forms.CharField(label="比赛名称", max_length=15, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '例：2020年‘新生杯’篮球赛'}))
    match_season = forms.CharField(label="赛季", max_length=15, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '例：2019-20-1'}))
    match_time = forms.CharField(label="比赛时间", max_length=15, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '例：2020.09-2020.10'}))
    match_location = forms.CharField(label="比赛地点", max_length=15, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '例：东操or体育馆'}))
    match_object = forms.CharField(label="面向对象", max_length=15, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '例：大一新生'}))
    match_picture = forms.FileField(label="比赛简照", required=False, widget=forms.FileInput(
        attrs={'class': 'team_picture'}))


class GameInfoForm(GameAlterForm):
    group_num = forms.ChoiceField(label="小组数", choices=Match.Match.group_choices, widget=forms.Select(
        attrs={'class': 'form-control'}))
    team_num = forms.IntegerField(label="球队数", widget=forms.NumberInput(
        attrs={'class': 'form-control', 'placeholder': '例：2'}))
    match_rule = forms.ChoiceField(label="比赛规则", choices=Match.Match.rule_choices, widget=forms.Select(
        attrs={'class': 'form-control'}))


# 比赛状态
class GameStateForm(forms.Form):
    match_stage = forms.ChoiceField(label="比赛阶段", initial='unstarted', widget=forms.Select(
        attrs={'class': 'form-control'}), choices=Match.Match_state.stage_choices)
    match_progress = forms.ChoiceField(label="比赛进展", initial='group', widget=forms.Select(
        attrs={'class': 'form-control'}), choices=Match.Match_state.progress_choices)
    dieout_progress = forms.ChoiceField(label="淘汰赛阶段", widget=forms.Select(
        attrs={'class': 'form-control'}), choices=Match.Match_state.dieout_choices)
    isPause = forms.BooleanField(label="是否暂停", initial=True, widget=forms.CheckboxInput(
        attrs={'class': 'form-control'}), required=False)


# 比赛结果
class GameResultForm(forms.Form):
    result_1st = forms.CharField(label="冠军", max_length=15, widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    result_2nd = forms.CharField(label="亚军", max_length=15, widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    result_3rd = forms.CharField(label="季军", max_length=15, required=False, widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    result_4th = forms.CharField(label="殿军", max_length=15, required=False, widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    result_mvp = forms.CharField(label="最有价值球员", max_length=15, widget=forms.TextInput(
        attrs={'class': 'form-control'}))


# 球队信息
class TeamInfoForm(forms.Form):
    team_name = forms.CharField(label="球队名", max_length=15, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '例：洛杉矶湖人'}))
    team_num = forms.ChoiceField(label="班号", initial='-1', choices=Match.Team.team_num_choices,
                                 widget=forms.Select(attrs={'class': 'form-control'}))
    team_group = forms.ChoiceField(label="所属小组", initial='undefined', choices=Match.Team.team_group_choices,
                                   widget=forms.Select(attrs={'class': 'form-control'}))
    team_isout = forms.ChoiceField(label="所属阶段", initial='ready', choices=Match.Team.isOut_choices,
                                   widget=forms.Select(attrs={'class': 'form-control'}))
    team_introduction = forms.CharField(label="球队简介", max_length=450, widget=forms.Textarea(
        attrs={'class': 'form-control', 'rows': '3', 'placeholder': '介绍一下球队吧...'}))
    team_picture = forms.FileField(label="队标", required=False, widget=forms.FileInput(
        attrs={'class': 'team_picture'}))


# 球员信息
class AthleteForm(forms.Form):
    ath_name = forms.CharField(label="姓名", max_length=15, widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    ath_sno = forms.CharField(label="学号", max_length=20, required=False, widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    ath_bir = forms.CharField(label="出生年月", max_length=20, required=False, widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    ath_height = forms.FloatField(label="身高", required=False, widget=forms.NumberInput(
        attrs={'class': 'form-control'}))
    ath_weight = forms.FloatField(label="体重", required=False, widget=forms.NumberInput(
        attrs={'class': 'form-control'}))
    ath_position = forms.ChoiceField(label="司职", choices=Match.Athlete.ath_position_choices,
                                     widget=forms.Select(attrs={'class': 'form-control'}))
    ath_number = forms.IntegerField(label="球衣号", widget=forms.NumberInput(
        attrs={'class': 'form-control'}))
    is_captain = forms.BooleanField(label="队长", initial=False, widget=forms.CheckboxInput(
        attrs={'class': 'form-control'}), required=False)
    ath_picture = forms.FileField(label="头像", required=False, widget=forms.FileInput(
        attrs={'class': 'team_picture'}))
