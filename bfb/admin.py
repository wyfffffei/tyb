from django.contrib import admin

from .Match import Team, Athlete, Score, Contest, Match, Match_state, Result
from bfb.community.Articles import User, Article, ArticleUpDown, Content, Comment


# 赛事版块
class MatchAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,         {'fields': ['match_name']}),
        ('比赛详情',     {'fields': ['match_season', 'match_time', 'match_location', 'match_object',
                                 'group_num', 'team_num', 'match_rule', 'match_picture']}),
    ]
    search_fields = ['match_name']


class MatchStateAdmin(admin.ModelAdmin):
    fieldsets = [
        ('基本信息',     {'fields': ['match_stage', 'match_progress', 'dieout_progress', 'isPause']}),
        ('对应赛事',     {'fields': ['match']}),
    ]
    list_display = ('match', 'match_progress', 'match_stage')


class ResultAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,        {'fields': ['matchr']}),
        ('排名情况',    {'fields': ['result_1st', 'result_2nd', 'result_3rd', 'result_4th']}),
        ('最有价值球员', {'fields': ['result_mvp']}),
    ]
    list_display = ('matchr', 'result_1st', 'result_mvp')


class ContestAdmin(admin.ModelAdmin):
    fieldsets = [
        ('对应双方（必选）',      {'fields': ['battle_teams'], 'classes':['collapse']}),
        ('比分数据',            {'fields': ['cs1', 'cs2']}),
        ('时间信息',            {'fields': ['contest_date', 'contest_time']}),
        ('比赛属性',            {'fields': ['contest_style', 'contest_state', 'dieout_progress']}),
        ('比赛内容',            {'fields': ['contest_content']}),
        ('所处赛事',            {'fields': ['matchc']}),
    ]
    list_display = ('matchc', 'cs1', 'cs2', 'contest_state', 'contest_style', 'pub_time')
    search_fields = ['matchc__match_name']
    filter_horizontal = ('battle_teams',)
    list_filter = ['matchc', 'contest_state', 'contest_style']


class AthleteInline(admin.TabularInline):
    model = Athlete
    extra = 2


class TeamAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,         {'fields': ['team_name']}),
        ('基本信息',     {'fields': ['team_num', 'team_group', 'team_introduction', 'team_picture'], 'classes':['collapse']}),
        ('当前状态',     {'fields': ['isOut']}),
        ('所处赛事',     {'fields': ['matcht']}),
    ]
    search_fields = ['matcht__match_name', 'team_name']
    list_display = ('team_name', 'matcht')
    list_filter = ['matcht', 'isOut']
    inlines = [AthleteInline]


class ScoreAdmin(admin.ModelAdmin):
    fieldsets = [
        ('比分情况',  {'fields': ['score', 'netscore', 'rank', 'num_win', 'num_lose']}),
        ('队名',     {'fields': ['belong_team']}),
    ]
    list_display = ('belong_team', 'score', 'rank')


# 社区版块
class UserAdmin(admin.ModelAdmin):
    fieldsets = [
        ('基本', {'fields': ['name', 'password', 'sex', 'email']}),
        ('详细',    {'fields': ['is_superuser', 'has_confirmed']})
    ]
    list_display = ('name', 'cre_time')
    search_fields = ['name']


class ArticleAdmin(admin.ModelAdmin):
    fieldsets = [
        ('标题',       {'fields': ['headline']}),
        ('基本信息',    {'fields': ['website', 'label_tag']}),
        ('发布者',     {'fields': ['user']})
    ]
    list_display = ('headline', 'user', 'pub_time')
    search_fields = ['headline', 'user__name']


class ContentAdmin(admin.ModelAdmin):
    fieldsets = [
        ('标题', {'fields': ['art']}),
        ('详细信息', {'fields': ['body', 'picture', 'num_liked', 'num_comment', 'num_visited']}),
    ]
    list_display = ('art',)
    search_fields = ['art__headline']


class CommentAdmin(admin.ModelAdmin):
    fieldsets = [
        ('评论文章', {'fields': ['article']}),
        ('详细信息', {'fields': ['content']}),
        ('发布人', {'fields': ['discusser']})
    ]
    list_display = ('article', 'discusser', 'pub_time')
    search_fields = ['article__headline', 'discusser__name']


class ArticleUpDownAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,     {'fields': ['is_up']}),
        ('对应文章', {'fields': ['article']}),
        ('对应用户', {'fields': ['user']})
    ]
    list_display = ('article', 'is_up', 'c_time')


admin.site.register(Team, TeamAdmin)
admin.site.register(Contest, ContestAdmin)
admin.site.register(Match, MatchAdmin)
admin.site.register(Match_state, MatchStateAdmin)
admin.site.register(Result, ResultAdmin)
admin.site.register(Score, ScoreAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(ArticleUpDown, ArticleUpDownAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Content, ContentAdmin)

