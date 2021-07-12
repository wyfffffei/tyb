from django.urls import path, re_path

from . import contest, team, management
from bfb.community import Log, Talking


app_name = 'bfb'
urlpatterns = [
    path('directory/', contest.directory, name='directory'),
    path('confirm/',   Log.user_confirm,  name='user_confirm'),

    path('event/',          contest.event,  name='event'),
    path('event/rank/',     contest.rank,   name='rank'),
    path('event/dieout/',   contest.dieout, name='dieout'),
    path('event/table/',    contest.table,  name='table'),

    # TODO 文章页单独拎出
    path('community/',                                        Talking.community,    name='community'),
    path('community/article/',                                Talking.articles,     name='articles'),
    path('community/article/publish',                         Talking.art_publish,  name='art_publish'),
    path('community/article/article_id?=<int:art_id>/',       Talking.art_detail,   name='art_detail'),
    path('community/article/article_id?=<int:art_id>/alter',  Talking.art_alter,    name='art_alter'),
    path('community/article/article_id?=<int:art_id>/delete', Talking.art_delete,   name='art_delete'),
    path('community/article/article_id?=<int:art_id>/comment',Talking.art_comment,  name='art_comment'),

    path('community/login/',         Log.login,      name='login'),
    path('community/logout/',        Log.logout,     name='logout'),
    path('community/register/',      Log.register,   name='register'),

    path('team/',                           team.team,          name='team'),
    path('team/match_id?=<int:mat_id>/',    team.teamall,       name='teamall'),
    path('team/match_id?=<int:mat_id>/team_id?=<int:tea_id>/',  team.teamdetail, name='teamdetail'),
    path('team/match_id?=<int:mat_id>/team_id?=<int:tea_id>/athlete_id?=<int:ath_id>/',
         team.athdetail, name='athdetail'),

    path('management/',                                       management.management_main,     name='management_main'),
    path('management/create_game/',                           management.create_game,         name='create_game'),
    path('management/game_id?=<int:match_id>/',               management.edit_game,           name='edit_game'),
    path('management/game_id?=<int:match_id>/info/',          management.edit_game_info,      name='edit_game_info'),
    path('management/game_id?=<int:match_id>/state/',         management.edit_game_state,     name='edit_game_state'),
    path('management/game_id?=<int:match_id>/team/',          management.edit_game_team,      name='edit_game_team'),
    path('management/game_id?=<int:match_id>/contest/',       management.edit_game_contest,   name='edit_game_contest'),
    path('management/game_id?=<int:match_id>/contest/update', management.contest_update,      name='contest_update'),
    path('management/game_id?=<int:match_id>/result/',        management.edit_game_result,    name='edit_game_result'),
    path('management/game_id?=<int:match_id>/team/create/',   management.create_team,         name='create_team'),
    path('management/game_id?=<int:match_id>/team/alter_id?=<int:team_id>/',
         management.alter_team,     name='alter_team'),
    path('management/game_id?=<int:match_id>/team/alter_id?=<int:team_id>/delete',
         management.delete_team,    name='delete_team'),
    path('management/game_id?=<int:match_id>/team/alter_id?=<int:team_id>/athlete/',
         management.create_athlete, name='create_athlete'),
    path('management/game_id?=<int:match_id>/team/alter_id?=<int:team_id>/athlete/alter_id?=<int:ath_id>',
         management.alter_athlete, name='alter_athlete'),
    path('management/game_id?=<int:match_id>/team/alter_id?=<int:team_id>/athlete/delete_id?=<int:ath_id>',
         management.delete_athlete, name='delete_athlete'),

    path('directory/historyclass/',     contest.historyclass,   name='historyclass'),
    path('directory/historyothers/',    contest.historyothers,  name='historyothers'),
]
