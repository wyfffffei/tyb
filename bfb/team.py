"""
@ Author: wyfffffei
@ Project: tyb
@ File: team.py
@ Time: 2021/1/31 18:08
@ Function:  输出球队及相关数据
"""

from django.shortcuts import HttpResponse,render
from django.shortcuts import redirect,get_object_or_404
from django.http import Http404
from . import Match
from bfb.contest import test_super as te
from bfb.community import Articles


def team(request):
    is_super = te(request)
    matchs = Match.Match.objects.all().order_by("-id")
    return render(request,"admin/team/队伍总览-0.html", locals())


def teamall(request, mat_id):
    is_super = te(request)
    try:
        match = Match.Match.objects.get(pk=mat_id)
        teams = Match.Team.objects.filter(matcht_id=mat_id)
    except Match.Match.DoesNotExist:
        raise Http404("比赛不存在!")
    else:
        return render(request, 'admin/team/队伍总览-1.html', locals())


def teamdetail(request, mat_id, tea_id):
    is_super = te(request)
    try:
        match = Match.Match.objects.get(pk=mat_id)
        team = Match.Team.objects.get(pk=tea_id)
    except Match.Match.DoesNotExist:
        raise Http404("比赛不存在！")
    except Match.Team.DoesNotExist:
        raise Http404("队伍不存在！")
    else:
        cons = team.contest.all()
        if request.session.get("is_login", None):
            is_login = True
        leaders = Match.Team.objects.filter(matcht=match, team_group=team.team_group)
        leader = ""
        for mem in leaders:
            if int(mem.score.rank) == 1:
                leader = mem
                break
        if not leader:
            leader = leaders.first()
        if request.method == 'POST':
            try:
                user = Articles.User.objects.get(name=request.session.get("user_name"))
            except Articles.User.DoesNotExist:
                raise Http404("用户不存在！")
            note = request.POST.get("note")
            if note:
                try:
                    words = Match.TeamVoice.objects.get(author=user, team=team)
                except Match.TeamVoice.DoesNotExist:
                    words = Match.TeamVoice.objects.create(author=user, team=team)
                words.voice = note
                words.save(update_fields=['voice'])
        return render(request, 'admin/team/队伍总览-2.html', locals())


def athdetail(request, mat_id, tea_id, ath_id):
    is_super = te(request)
    try:
        match = Match.Match.objects.get(pk=mat_id)
        be_team = Match.Team.objects.get(pk=tea_id)
        ath = Match.Athlete.objects.get(pk=ath_id)
    except Match.Match.DoesNotExist:
        raise Http404("比赛不存在！")
    except Match.Team.DoesNotExist:
        raise Http404("队伍不存在！")
    except Match.Athlete.DoesNotExist:
        raise Http404("运动员不存在！")
    else:
        return render(request, 'admin/team/队伍总览-3.html', locals())


