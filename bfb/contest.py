"""
@ Author: wyfffffei
@ Project: tyb
@ File: contest.py
@ Time: 2021/1/31 22.05
@ Function:  输出赛事数据
"""

from django.shortcuts import HttpResponse,render
from django.shortcuts import redirect,get_object_or_404
from django.http import Http404
from . import Match
from . import Rules

PerContestError = ["小组赛尚未完全结束!", "淘汰赛尚未完全结束!", ]

def test_super(request):
    is_super = False
    if request.session.get("is_login", None):
        if request.session.get("is_superuser") == 1:
            is_super = True
    return is_super


def directory(request):
    is_super = test_super(request)
    team1 = Match.Team.objects.get(team_name="洛杉矶湖人")
    team2 = Match.Team.objects.get(team_name="洛杉矶快船")
    data = {"is_super": is_super, "team1": team1, "team2": team2}
    return render(request, "admin/目录.html", data)


def rank(request):
    is_super = test_super(request)
    this_state = Match.Match_state.objects.filter(match_stage='inprogress').first()
    if not this_state:
        try:
            this_state = Match.Match_state.objects.last()
        except Match.Match_state.DoesNotExist:
            raise Http404("当前无赛事！")
    game = this_state.match
    check_result = Rules.default_match_state_check(game, this_state.match_progress, this_state.dieout_progress,
                                                   game.team_num, game.group_num)
    if check_result.get("error_message"):
        if check_result.get("error_message") not in PerContestError:
            raise Http404("比赛还未准备好")
    contest_group = []
    for i in range(4):
        teams = Match.Team.objects.filter(matcht=game, team_group=Match.Team.team_group_choices[i][0]).order_by('id')
        if not teams:
            break
        contest_group.append(list())
        for team in teams:
            data = list()
            for contest in team.contest.filter(contest_style="group").order_by('id'):
                if contest.battle_teams.all()[0] == team:
                    data.append([team.team_name, contest.cs1, contest.battle_teams.all()[1].team_name, contest.cs2])
                else:
                    data.append([team.team_name, contest.cs2, contest.battle_teams.all()[0].team_name, contest.cs1])
            team.info = data
            contest_group[i].append(team)
    return render(request, "admin/contest/小组赛.html", locals())


def dieout(request):
    is_super = test_super(request)
    this_state = Match.Match_state.objects.filter(match_stage='inprogress').first()
    if not this_state:
        try:
            this_state = Match.Match_state.objects.last()
        except Match.Match_state.DoesNotExist:
            raise Http404("当前无赛事！")
    game = this_state.match
    check_result = Rules.default_match_state_check(game, this_state.match_progress, this_state.dieout_progress,
                                                   game.team_num, game.group_num)
    if check_result.get("error_message"):
        if check_result.get("error_message") not in PerContestError:
            raise Http404("比赛还未准备好")
    if this_state.match_progress == "group":
        error_message = "当前为小组赛阶段"
    else:
        d_teams = list()
        for i in range(4):
            contests = Match.Contest.objects.filter(matchc=game, contest_style='dieout', dieout_progress=i+1)
            if not contests:
                break
            d_teams.append(list())
            for contest in contests:
                for team in contest.battle_teams.all():
                    d_teams[i].append(team.team_name)
            if len(contests) == 1:
                final = contests.first()
                cham = ""
                if final.contest_state == "ended":
                    teams = final.battle_teams.all()
                    cham = teams[0] if int(final.cs1) > int(final.cs2) else teams[1]
                d_teams.append([cham])
                break
    return render(request, "admin/contest/淘汰赛.html", locals())


def table(request):
    is_super = test_super(request)
    this_state = Match.Match_state.objects.filter(match_stage='inprogress').first()
    if not this_state:
        try:
            this_state = Match.Match_state.objects.last()
        except Match.Match_state.DoesNotExist:
            raise Http404("当前无赛事！")
    game = this_state.match
    check_result = Rules.default_match_state_check(game, this_state.match_progress, this_state.dieout_progress,
                                                   game.team_num, game.group_num)
    if check_result.get("error_message"):
        if check_result.get("error_message") not in PerContestError:
            raise Http404("比赛还未准备好")
    rank_list = []
    for i in range(4):
        teams = Match.Team.objects.filter(matcht=game, team_group=Match.Team.team_group_choices[i][0])
        if not teams:
            break
        rank_list.append([j for j in range(len(teams))])
        for team in teams:
            rank_list[i][int(team.score.rank)-1] = team
    return render(request, "admin/contest/排名表.html", locals())


def event(request):
    is_super = test_super(request)
    this_state = Match.Match_state.objects.filter(match_stage='inprogress').first()
    if not this_state:
        try:
            this_state = Match.Match_state.objects.last()
        except Match.Match_state.DoesNotExist:
            raise Http404("当前无赛事！")
    game = this_state.match
    check_result = Rules.default_match_state_check(game, this_state.match_progress, this_state.dieout_progress,
                                                   game.team_num, game.group_num)
    if check_result.get("error_message"):
        if check_result.get("error_message") not in PerContestError:
            raise Http404("比赛还未准备好")
    contest_all = game.contest_set.order_by('-contest_date')
    return render(request, "admin/contest/赛事详情.html", locals())


def historyclass(request):
    is_super = test_super(request)
    matchs = Match.Match.objects.all()
    data = {'matchs': matchs, 'is_super': is_super}
    return render(request, "bfb/历史班赛.html", data)


def historyothers(request):
    return render(request, "bfb/其他赛事.html")
