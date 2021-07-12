from django.db import models
from bfb.community import Articles


# 规则待改进
class Match(models.Model):
    rule_choices = (('group_dieout', '小组淘汰赛'), ('circle', '大循环'), ('onechance_dieout', '单轮淘汰'))
    group_choices = ((1, '无小组'), (2, 'AB组'), (3, 'ABC组'), (4, 'ABCD组'))

    match_name = models.CharField(max_length=20,default="New_Game", verbose_name='比赛名称')
    match_season = models.CharField(max_length=20, null=True, verbose_name='赛季')
    match_time = models.CharField(max_length=20, null=True, verbose_name='比赛时间')
    match_location = models.CharField(max_length=20, null=True, verbose_name='比赛地点')
    match_object = models.CharField(max_length=20, null=True, verbose_name='面向对象')
    group_num = models.PositiveIntegerField(choices=group_choices, default=1, verbose_name="小组数")
    team_num = models.PositiveIntegerField(default=2, verbose_name="球队数")
    match_rule = models.CharField(max_length=20, default=rule_choices[0][0], choices=rule_choices, verbose_name="赛制")
    match_picture = models.ImageField(default="image/default.png", upload_to="image/", verbose_name="比赛简照")

    class Meta:
        verbose_name = '比赛'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.match_name


class Match_state(models.Model):
    """
    # match_stage: 前端展示的依据
    # match_progress: 数据库判断依据
    # dieout_progress: 淘汰赛阶段
    # isPause: 终止按钮
    """
    stage_choices = (('unstarted', '未开始'), ('inprogress', '进行中'), ('ended', '已结束'))
    progress_choices = (('group', '小组赛'), ('dieout', '淘汰赛'), ('end', '结束'))
    dieout_choices = ((1, '阶段1'), (2, '阶段2'), (3, '阶段3'), (4, '阶段4'), (-1, '非淘汰赛'))

    match_stage = models.CharField(choices=stage_choices, max_length=10, default='unstarted', verbose_name='比赛阶段')
    match_progress = models.CharField(choices=progress_choices, max_length=10, default='group', verbose_name='比赛进展')
    dieout_progress = models.IntegerField(choices=dieout_choices, default=-1, verbose_name="淘汰赛阶段")
    isPause = models.BooleanField(default=True, verbose_name='是否暂停')
    match = models.OneToOneField(Match, on_delete=models.CASCADE, null=True, verbose_name='对应赛事')

    class Meta:
        verbose_name = '比赛状态'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.match_stage


class Team(models.Model):
    team_num_choices = (('1', '一班'), ('2', '二班'), ('3', '三班'), ('4', '四班'), ('5', '五班'),
                        ('6', '六班'), ('7', '七班'), ('8', '八班'), ('9', '九班'), ('10', '十班'),
                        ('11', '十一班'), ('12', '十二班'), ('13', '十三班'), ('14', '十四班'), ('15', '十五班'),
                        ('16', '十六班'), ('-1', '其他'))
    team_group_choices = (('groupA', 'A组'), ('groupB', 'B组'), ('groupC', 'C组'), ('groupD', 'D组'), ('undefined', '未定义'))
    isOut_choices = (('ready', '准备中'), ('group', '小组赛'), ('dieout', '淘汰赛'), ('out', '已结束'))

    team_name = models.CharField(max_length=20, verbose_name='球队名称')
    team_num = models.CharField(max_length=10, choices=team_num_choices, default='-1', verbose_name='班号')
    team_introduction = models.CharField(max_length=100, null=True, verbose_name='球队简介')
    team_group = models.CharField(choices=team_group_choices, max_length=10, default='undefined', verbose_name='所属小组')
    isOut = models.CharField(choices=isOut_choices, max_length=10, default='ready', verbose_name='所属阶段')
    team_picture = models.ImageField(default="image/laker.jpg", upload_to="image/", verbose_name="队标")
    matcht = models.ForeignKey(Match, on_delete=models.CASCADE, null=True, verbose_name='对应比赛')

    class Meta:
        verbose_name = '球队信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.team_name


class TeamVoice(models.Model):
    voice = models.CharField(max_length=256, verbose_name="留言板")
    c_time = models.DateTimeField(auto_now_add=True)
    author = models.OneToOneField(Articles.User, on_delete=models.CASCADE, verbose_name="留言者")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, verbose_name="对应球队")

    class Meta:
        verbose_name = "球队留言板"
        verbose_name_plural = "球队留言板"

    def __str__(self):
        return self.author.name + " ==> " + self.team.team_name


class Score(models.Model):
    score = models.IntegerField(default=0, verbose_name='得分')
    netscore = models.IntegerField(default=0, verbose_name='净胜分')
    rank = models.IntegerField(default=0, verbose_name='排名')
    num_win = models.IntegerField(default=0, verbose_name='胜场数')
    num_lose = models.IntegerField(default=0, verbose_name='负场数')
    belong_team = models.OneToOneField(Team, on_delete=models.CASCADE, verbose_name='球队')

    class Meta:
        verbose_name = '得分情况'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.belong_team.team_name


class Athlete(models.Model):
    ath_position_choices = (('pg', '组织后卫'), ('sg', '得分后卫'), ('sf', '小前锋'),
                            ('pf', '大前锋'), ('c', '中锋'), ('undefined', '未定义'))

    ath_name = models.CharField(max_length=20, verbose_name='姓名')
    ath_picture = models.ImageField(default="image/head_default.png", upload_to="image/", verbose_name="头像")
    ath_sno = models.CharField(max_length=20, null=True, verbose_name='学号')
    ath_bir = models.CharField(max_length=20, null=True, verbose_name='出生年月')
    ath_height = models.FloatField(default=0, null=True, verbose_name='身高')
    ath_weight = models.FloatField(default=0, null=True, verbose_name='体重')
    ath_position = models.CharField(choices=ath_position_choices, max_length=20, default='undefined',verbose_name='司职')
    ath_number = models.IntegerField(default=-1, verbose_name='号码')
    isCaptain = models.BooleanField(default=False, verbose_name='队长')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, verbose_name='所属球队')

    class Meta:
        verbose_name = '运动员信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.ath_name


class Contest(models.Model):
    contest_style_choices = (('group', '小组赛'), ('dieout', '淘汰赛'))
    contest_state_choices = (('unstarted', '未开始'), ('ready', '准备中'), ('ended', '已结束'))
    progress_choices = ((1, '阶段1'), (2, '阶段2'), (3, '阶段3'), (4, '阶段4'), (-1, '非淘汰赛'))

    contest_style = models.CharField(choices=contest_style_choices, max_length=20, default='group', verbose_name='竞赛类型')
    contest_state = models.CharField(choices=contest_state_choices, max_length=20, default='unstarted', verbose_name='竞赛状态')
    dieout_progress = models.IntegerField(choices=progress_choices, default=-1, verbose_name='淘汰赛阶段')
    cs1 = models.CharField(max_length=20, verbose_name='1队得分', default=0, null=True, blank=True)
    cs2 = models.CharField(max_length=20, verbose_name='2队得分', default=0, null=True, blank=True)
    contest_date = models.CharField(max_length=50, default="01-01", null=True, verbose_name='对阵日期')
    contest_time = models.CharField(max_length=50, default="00:00", null=True, verbose_name='对阵时间')
    pub_time = models.DateTimeField(verbose_name='发布时间', auto_now_add=True)
    contest_content = models.CharField(max_length=500, null=True, blank=True, verbose_name='对阵详情')
    matchc = models.ForeignKey(Match, on_delete=models.CASCADE, null=True, verbose_name='对应赛事')
    battle_teams = models.ManyToManyField(Team, related_name='contest', verbose_name='对应球队')

    class Meta:
        verbose_name = '竞赛内容'
        verbose_name_plural = verbose_name
        ordering = ["-pub_time"]

    def __str__(self):
        return str(self.cs1) + ':' + str(self.cs2)


class Result(models.Model):
    result_1st = models.CharField(max_length=20, null=True, default='无', verbose_name='冠军')
    result_2nd = models.CharField(max_length=20, null=True, default='无', verbose_name='亚军')
    result_3rd = models.CharField(max_length=20, null=True, default='无', verbose_name='季军')
    result_4th = models.CharField(max_length=20, null=True, default='无', verbose_name='殿军')
    result_mvp = models.CharField(max_length=20, null=True, default='无', verbose_name='最有价值球员')
    matchr = models.OneToOneField(Match, on_delete=models.CASCADE, null=True, verbose_name='对应赛事')

    class Meta:
        verbose_name = '比赛结果'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.result_1st

