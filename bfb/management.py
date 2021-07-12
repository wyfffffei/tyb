"""
@ Author: wyfffffei
@ Project: tyb
@ File: management.py
@ Time: 2021/2/10 0:41
@ Function:  
"""

from django.db import transaction
from django.shortcuts import HttpResponse, render
from django.shortcuts import redirect, get_object_or_404
from django.http import Http404
from . import Match
from . import forms
from . import Rules
import json


# 验证访问用户合法性
# 直接调用重定向语句失效，暂时copy
def is_super(request):
    if request.session.get('is_login', None):
        if request.session.get("is_superuser") == 1:
            pass
        else:
            return redirect("/bfb/directory/")
    else:
        return redirect("/bfb/community/login/")


def management_main(request):
    if request.session.get('is_login', None):
        if request.session.get("is_superuser") == 1:
            match_list = Match.Match.objects.all().order_by("-id")
            if match_list:
                data = {"match_list": match_list, "is_super": True}
                return render(request, "admin/management/main.html", data)
            else:
                empty_message = "当前无比赛！"
                data = {"empty_message": empty_message, "is_super": True}
                return render(request, "admin/management/main.html", data)
        else:
            return redirect("/bfb/directory/")
    else:
        return redirect("/bfb/community/login/")


def create_game(request):
    if request.session.get('is_login', None):
        if request.session.get("is_superuser") == 1:
            is_super = True
            if request.method == 'POST':
                game_info_form = forms.GameInfoForm(request.POST)
                if game_info_form.is_valid():
                    msg = ""
                    cleaned_data = game_info_form.cleaned_data
                    m_name = cleaned_data.get('match_name')
                    same_match = Match.Match.objects.filter(match_name=m_name)
                    if same_match:
                        msg = "比赛已存在！"
                    team_num = cleaned_data.get('team_num')
                    if team_num < 2:
                        msg = msg + "球队数必须大于一！"
                    if msg:
                        return render(request, "admin/management/create_game.html", locals())
                    with transaction.atomic():
                        new_match = Match.Match.objects.create(
                            match_name=m_name,
                            match_season=cleaned_data.get('match_season'),
                            match_time=cleaned_data.get('match_time'),
                            match_location=cleaned_data.get('match_location'),
                            match_object=cleaned_data.get('match_object'),
                            group_num=int(cleaned_data.get('group_num')),
                            team_num=team_num,
                            match_rule=cleaned_data.get('match_rule')
                        )
                        if request.FILES.get("match_picture"):
                            new_match.match_picture = request.FILES.get("match_picture")
                            new_match.save(update_fields=['match_picture'])
                        Match.Match_state.objects.create(match=new_match)
                        Match.Result.objects.create(matchr=new_match)

                        rule = Rules.BaseRules(team_num=new_match.team_num,
                                               group_num=new_match.group_num,
                                               rule=new_match.match_rule)
                        if not rule.team_init(new_match):
                            msg = msg + "队伍初始化错误！"
                        if not rule.team_group_init(new_match.team_set.all()):
                            msg = msg + "队伍分组初始化错误！"
                        if not rule.contest_group_init(new_match):
                            msg = msg + "小组赛初始化错误！"
                        if msg:
                            return render(request, "admin/management/create_game.html", locals())
                    return redirect("/bfb/management/")
                else:
                    msg = "请填写完整信息！"
                    return render(request, "admin/management/create_game.html", locals())
            game_info_form = forms.GameInfoForm()
            return render(request, "admin/management/create_game.html", locals())
        else:
            return redirect("/bfb/directory/")
    else:
        return redirect("/bfb/community/login/")


def edit_game(request, match_id):
    if request.session.get('is_login', None):
        if request.session.get("is_superuser") == 1:
            try:
                e_match = Match.Match.objects.get(id=match_id)
            except Match.Match.DoesNotExist:
                raise Http404("比赛不存在！")
            else:
                if request.method == 'POST':
                    e_match.delete()
                    return redirect("/bfb/management/")
                error_message = ""
                base = Rules.BaseRules(e_match.team_num, e_match.group_num, e_match.match_rule)
                while True:
                    try:
                        this_state = e_match.match_state
                        team_all = Match.Team.objects.filter(matcht=e_match)
                        this_result = e_match.result
                        contest_all = Match.Contest.objects.filter(matchc=e_match)
                        break
                    except Match.Match_state.DoesNotExist:
                        Match.Match_state.object.create(match=e_match)
                    except Match.Team.DoesNotExist:
                        base.team_init(new_match=e_match)
                    except Match.Result.DoesNotExist:
                        Match.Result.objects.create(matchr=e_match)
                    except Match.Contest.DoesNotExist:
                        base.contest_group_init(e_match)

                check_result = base.state_check(e_match)
                if check_result.get("error_message"):
                    error_message = check_result
                contest_record = list()
                for val in contest_all.order_by('id'):
                    style = val.get_contest_style_display
                    state = val.get_contest_state_display
                    val_id = val.id
                    team1 = val.battle_teams.all()[0]
                    team2 = val.battle_teams.all()[1]
                    contest_record.append([team1.team_name, team2.team_name, style, state, val_id])
                data = {'e_match': e_match, 'contest_record': contest_record, 'is_super': True}
                if error_message:
                    data['error_message'] = error_message
                return render(request, "admin/management/edit_game.html", data)
        else:
            return redirect("/bfb/directory/")
    else:
        return redirect("/bfb/community/login/")


def edit_game_info(request, match_id):
    if request.session.get('is_login', None):
        if request.session.get("is_superuser") == 1:
            try:
                e_match = Match.Match.objects.get(id=match_id)
            except Match.Match.DoesNotExist:
                raise Http404("比赛不存在！")
            else:
                is_super = True
                if request.method == 'POST':
                    game_info_form = forms.GameAlterForm(request.POST)
                    if game_info_form.is_valid():
                        cleaned_data = game_info_form.cleaned_data
                        m_name = cleaned_data.get('match_name')
                        if m_name != e_match.match_name:
                            same_match = Match.Match.objects.filter(match_name=m_name)
                            if same_match:
                                msg = "比赛已存在！"
                                return render(request, "admin/management/edit_game_info.html", locals())
                        with transaction.atomic():
                            e_match.match_name = m_name
                            e_match.match_season = cleaned_data.get('match_season')
                            e_match.match_time = cleaned_data.get('match_time')
                            e_match.match_location = cleaned_data.get('match_location')
                            e_match.match_object = cleaned_data.get('match_object')
                            if request.FILES.get("match_picture"):
                                e_match.match_picture = request.FILES.get("match_picture")
                            e_match.save()
                            return redirect(f"/bfb/management/game_id%3F={e_match.id}/")
                    else:
                        msg = "请提交完整表单！"
                        return render(request, "admin/management/edit_game_info.html", locals())
                game_info_form = forms.GameAlterForm()
                return render(request, "admin/management/edit_game_info.html", locals())
        else:
            return redirect("/bfb/directory/")
    else:
        return redirect("/bfb/community/login/")


# *****
# Heart!
# *****
def edit_game_state(request, match_id):
    if request.session.get('is_login', None):
        if request.session.get("is_superuser") == 1:
            try:
                e_match = Match.Match.objects.get(id=match_id)
            except Match.Match.DoesNotExist:
                raise Http404("比赛不存在！")
            else:
                is_super = True
                if request.method == 'POST':
                    game_state_form = forms.GameStateForm(request.POST)
                    error_message = "请提交完整表单！"
                    if game_state_form.is_valid():
                        cleaned_data = game_state_form.cleaned_data
                        stage = cleaned_data.get("match_stage")
                        match_progress = cleaned_data.get("match_progress")
                        dieout_progress = cleaned_data.get("dieout_progress")
                        ispause = cleaned_data.get("isPause")
                        error_message = ""
                        try:
                            this_state = e_match.match_state
                        except Match.Match_state.DoesNotExist:
                            this_state = Match.Match_state.objects.create(match=e_match)

                        this_state.match_stage = stage
                        this_state.match_progress = match_progress
                        this_state.dieout_progress = dieout_progress
                        this_state.isPause = ispause
                        this_state.save()
                        # 切换必要条件：比赛阶段为进行中，暂停标记为False!!!
                        if stage == 'inprogress' and ispause is False:
                            rule = Rules.BaseRules(team_num=e_match.team_num, group_num=e_match.group_num,
                                                   rule=e_match.match_rule)
                            check_result = rule.state_check(e_match)
                            if check_result.get("error_message"):
                                error_message = check_result.get("error_message")
                            else:
                                team_all_update = Match.Team.objects.filter(matcht=e_match)
                                rule.dieout_contest_create(e_match, check_result.get("state"), team_all_update)

                        if stage == 'ended' and match_progress == 'end':
                            Rules.BaseRules.go2end(e_match)

                        if error_message:
                            return render(request, "admin/management/edit_game_state.html", locals())
                        else:
                            return redirect(f"/bfb/management/game_id%3F={e_match.id}/")
                    else:
                        return render(request, "admin/management/edit_game_state.html", locals())
                else:
                    game_state_form = forms.GameStateForm()
                    try:
                        e_match.match_state
                    except Match.Match_state.DoesNotExist:
                        msg = "状态未定义!"
                    return render(request, "admin/management/edit_game_state.html", locals())
        else:
            return redirect("/bfb/directory/")
    else:
        return redirect("/bfb/community/login/")


def edit_game_contest(request, match_id):
    if request.session.get('is_login', None):
        if request.session.get("is_superuser") == 1:
            try:
                e_match = Match.Match.objects.get(id=match_id)
            except Match.Match.DoesNotExist:
                raise Http404("比赛不存在！")
            else:
                is_super = True
                contests_g = Match.Contest.objects.filter(matchc=e_match, contest_style='group')
                contests_d = Match.Contest.objects.filter(matchc=e_match, contest_style='dieout')
                if request.method == 'POST':
                    cs1 = request.POST.get("cs1")
                    cs2 = request.POST.get("cs2")
                    c_state = request.POST.get("state")
                    c_date = request.POST.get("date")
                    c_time = request.POST.get("time")
                    c_id = request.POST.get("contest_id")
                    if cs1 and cs2 and c_state and c_date and c_time and c_id:
                        try:
                            contest_alter = Match.Contest.objects.get(id=c_id)
                        except (Match.Contest.DoesNotExist, ValueError):
                            raise Http404("赛事不存在！")
                        else:
                            contest_alter.contest_state = c_state
                            contest_alter.contest_date = c_date
                            contest_alter.contest_time = c_time
                            contest_alter.save(update_fields=['contest_state', 'contest_date', 'contest_time'])
                            if c_state == 'ended':
                                contest_alter.cs1 = cs1
                                contest_alter.cs2 = cs2
                                contest_alter.save(update_fields=['cs1', 'cs2'])
                                msg = "比赛已结束！"
                    else:
                        msg = "请提交完整表单！"
                return render(request, "admin/management/edit_game_contest.html", locals())
        else:
            return redirect("/bfb/directory/")
    else:
        return redirect("/bfb/community/login/")


def edit_game_result(request, match_id):
    if request.session.get('is_login', None):
        if request.session.get("is_superuser") == 1:
            try:
                e_match = Match.Match.objects.get(id=match_id)
            except Match.Match.DoesNotExist:
                raise Http404("比赛不存在！")
            else:
                is_super = True
                if request.method == 'POST':
                    game_result_form = forms.GameResultForm(request.POST)
                    if game_result_form.is_valid():
                        cleaned_data = game_result_form.cleaned_data
                        r_1 = cleaned_data.get("result_1st")
                        r_2 = cleaned_data.get("result_2nd")
                        r_3 = cleaned_data.get("result_3rd")
                        r_4 = cleaned_data.get("result_4th")
                        r_m = cleaned_data.get("result_mvp")
                        try:
                            e_match.result
                        except Match.Result.DoesNotExist:
                            Match.Result.objects.create(
                                matchr=e_match,
                                result_1st=r_1,
                                result_2nd=r_2,
                                result_3rd=r_3,
                                result_4th=r_4,
                                result_mvp=r_m)
                        else:
                            e_match.result.result_1st = r_1
                            e_match.result.result_2nd = r_2
                            e_match.result.result_3rd = r_3
                            e_match.result.result_4th = r_4
                            e_match.result.result_mvp = r_m
                            e_match.result.save()
                        return redirect(f"/bfb/management/game_id%3F={e_match.id}/")
                    else:
                        msg = "请填写完整信息！"
                        return render(request, "admin/management/edit_game_result.html", locals())
                else:
                    game_result_form = forms.GameResultForm()
                    msg = ""
                    try:
                        e_match.result
                    except Match.Result.DoesNotExist:
                        msg = "比赛结果未定义"
                    return render(request, "admin/management/edit_game_result.html", locals())
        else:
            return redirect("/bfb/directory/")
    else:
        return redirect("/bfb/community/login/")


def edit_game_team(request, match_id):
    if request.session.get('is_login', None):
        if request.session.get("is_superuser") == 1:
            try:
                editing_match = Match.Match.objects.get(id=match_id)
            except Match.Match.DoesNotExist:
                raise Http404("比赛不存在！")
            else:
                msg = ""
                if not editing_match.team_set.all():
                    msg = "当前比赛无球队"
                data = {"e_match": editing_match, "msg": msg, "is_super": True}
                return render(request, "admin/management/edit_game_team.html", data)
        else:
            return redirect("/bfb/directory/")
    else:
        return redirect("/bfb/community/login/")


def create_team(request, match_id):
    if request.session.get('is_login', None):
        if request.session.get("is_superuser") == 1:
            try:
                e_match = Match.Match.objects.get(id=match_id)
            except Match.Match.DoesNotExist:
                raise Http404("比赛不存在！")
            else:
                is_super = True
                if request.method == 'POST':
                    team_info_form = forms.TeamInfoForm(request.POST)
                    if team_info_form.is_valid():
                        cleaned_data = team_info_form.cleaned_data
                        t_name = cleaned_data.get("team_name")
                        t_num = cleaned_data.get("team_num")
                        t_group = cleaned_data.get("team_group")
                        t_isout = cleaned_data.get("team_isout")
                        t_intro = cleaned_data.get("team_introduction")
                        same_team = Match.Team.objects.filter(matcht=e_match, team_name=t_name)
                        if same_team:
                            msg = "队伍已存在！"
                            flag = False
                        else:
                            with transaction.atomic():
                                new_team = Match.Team.objects.create(
                                    matcht=e_match,
                                    team_name=t_name, team_introduction=t_intro,
                                    team_num=t_num, team_group=t_group, isOut=t_isout,
                                )
                                if request.FILES.get("team_picture"):
                                    new_team.team_picture=request.FILES.get("team_picture")
                                    new_team.save(update_fields=['team_picture'])
                                Match.Score.objects.create(belong_team=new_team)
                                flag = True
                    else:
                        msg = "请填写完整信息！"
                        flag = False
                    if flag:
                        return redirect(f"/bfb/management/game_id%3F={e_match.id}/team/")
                    else:
                        return render(request, "admin/management/create_team.html", locals())
                else:
                    team_info_form = forms.TeamInfoForm()
                    return render(request, "admin/management/create_team.html", locals())
        else:
            return redirect("/bfb/directory/")
    else:
        return redirect("/bfb/community/login/")


def alter_team(request, match_id, team_id):
    if request.session.get('is_login', None):
        if request.session.get("is_superuser") == 1:
            try:
                e_match = Match.Match.objects.get(id=match_id)
                a_team = Match.Team.objects.get(id=team_id)
            except Match.Match.DoesNotExist:
                raise Http404("比赛不存在！")
            except Match.Team.DoesNotExist:
                raise Http404("队伍不存在！")
            else:
                is_super = True
                if request.method == 'POST':
                    team_info_form = forms.TeamInfoForm(request.POST)
                    if team_info_form.is_valid():
                        cleaned_data = team_info_form.cleaned_data
                        t_name = cleaned_data.get("team_name")

                        flag = True
                        if t_name != a_team.team_name:
                            same_team = Match.Team.objects.filter(matcht=e_match, team_name=t_name)
                            if same_team:
                                flag = False
                        if flag:
                            with transaction.atomic():
                                a_team.team_name = t_name
                                a_team.team_introduction = cleaned_data.get("team_introduction")
                                a_team.team_num = cleaned_data.get("team_num")
                                a_team.team_group = cleaned_data.get("team_group")
                                a_team.isOut = cleaned_data.get("team_isout")
                                if request.FILES.get("team_picture"):
                                    a_team.team_picture = request.FILES.get("team_picture")
                                a_team.save()
                            return redirect(f"/bfb/management/game_id%3F={e_match.id}/team/")
                        else:
                            msg = "队伍已存在！"
                    else:
                        msg = "请填写完整信息！"
                    return render(request, "admin/management/alter_team.html", locals())
                else:
                    team_info_form = forms.TeamInfoForm()
                    return render(request, "admin/management/alter_team.html", locals())
        else:
            return redirect("/bfb/directory/")
    else:
        return redirect("/bfb/community/login/")


def delete_team(request, match_id, team_id):
    if request.session.get('is_login', None):
        if request.session.get("is_superuser") == 1:
            try:
                editing_match = Match.Match.objects.get(id=match_id)
                altering_team = Match.Team.objects.get(id=team_id)
            except Match.Match.DoesNotExist:
                raise Http404("比赛不存在！")
            except Match.Team.DoesNotExist:
                raise Http404("队伍不存在！")
            else:
                if request.method == 'POST':
                    altering_team.delete()
                return redirect(f"/bfb/management/game_id%3F={match_id}/team/")
        else:
            return redirect("/bfb/directory/")
    else:
        return redirect("/bfb/community/login/")


def create_athlete(request, match_id, team_id):
    if request.session.get('is_login', None):
        if request.session.get("is_superuser") == 1:
            try:
                e_match = Match.Match.objects.get(id=match_id)
                a_team = Match.Team.objects.get(id=team_id)
            except Match.Match.DoesNotExist:
                raise Http404("比赛不存在！")
            except Match.Team.DoesNotExist:
                raise Http404("队伍不存在！")
            else:
                is_super = True
                if request.method == 'POST':
                    ath_form = forms.AthleteForm(request.POST)
                    msg = "请提交完整表单！"
                    if ath_form.is_valid():
                        msg = ""
                        cleaned_data = ath_form.cleaned_data
                        number = cleaned_data.get("ath_number")
                        is_captain = cleaned_data.get("is_captain")
                        same_player = Match.Athlete.objects.filter(team=a_team, ath_number=number)
                        if same_player:
                            msg = "该球衣号码已被使用！"
                        one_captain = Match.Athlete.objects.filter(team=a_team, isCaptain=True)
                        if is_captain:
                            if one_captain:
                                msg = msg + "一个队伍只允许一个队长！"
                        else:
                            if not one_captain:
                                msg = msg + "请先添加队长！"
                        if msg:
                            return render(request, "admin/management/create_athlete.html", locals())
                        with transaction.atomic():
                            new_player = Match.Athlete.objects.create(
                                ath_name=cleaned_data.get("ath_name"),
                                ath_sno=cleaned_data.get("ath_sno"),
                                ath_bir=cleaned_data.get("ath_bir"),
                                ath_height=cleaned_data.get("ath_height"),
                                ath_weight=cleaned_data.get("ath_weight"),
                                ath_position=cleaned_data.get("ath_position"),
                                ath_number=number,
                                isCaptain=is_captain,
                                team=a_team
                            )
                            if request.FILES.get("ath_picture"):
                                new_player.ath_picture = request.FILES.get("ath_picture")
                                new_player.save(update_fields=['ath_picture'])
                    return render(request, "admin/management/create_athlete.html", locals())
                ath_form = forms.AthleteForm()
                return render(request, "admin/management/create_athlete.html", locals())
        else:
            return redirect("/bfb/directory/")
    else:
        return redirect("/bfb/community/login/")


def alter_athlete(request, match_id, team_id, ath_id):
    if request.session.get('is_login', None):
        if request.session.get("is_superuser") == 1:
            try:
                e_match = Match.Match.objects.get(id=match_id)
                a_team = Match.Team.objects.get(id=team_id)
                a_ath = Match.Athlete.objects.get(id=ath_id)
            except Match.Match.DoesNotExist:
                raise Http404("比赛不存在！")
            except Match.Team.DoesNotExist:
                raise Http404("队伍不存在！")
            except Match.Athlete.DoesNotExist:
                raise Http404("球员不存在！")
            else:
                if request.method == 'POST':
                    ath_form = forms.AthleteForm(request.POST)
                    msg = "请提交完整表单！"
                    if ath_form.is_valid():
                        msg = ""
                        cleaned_data = ath_form.cleaned_data
                        number = cleaned_data.get("ath_number")
                        is_captain = cleaned_data.get("is_captain")
                        if number != a_ath.ath_number:
                            same_player = Match.Athlete.objects.filter(team=a_team, ath_number=number)
                            if same_player:
                                msg = "该球衣号码已被使用！"
                        if is_captain != a_ath.isCaptain:
                            if is_captain:
                                msg = msg + "一个队伍只允许一个队长！"
                            else:
                                msg = msg + "您不能删除队长，请修改名字！"
                        if msg:
                            return render(request, "admin/management/alter_athlete.html", locals())
                        a_ath.ath_name = cleaned_data.get("ath_name")
                        a_ath.ath_sno = cleaned_data.get("ath_sno")
                        a_ath.ath_bir = cleaned_data.get("ath_bir")
                        a_ath.ath_height = cleaned_data.get("ath_height")
                        a_ath.ath_weight = cleaned_data.get("ath_weight")
                        a_ath.ath_position = cleaned_data.get("ath_position")
                        a_ath.ath_number = number
                        if request.FILES.get("ath_picture"):
                            a_ath.ath_picture = request.FILES.get("ath_picture")
                        a_ath.save()
                        return redirect(f"/bfb/management/game_id%3F={match_id}/team/alter_id%3F={team_id}/athlete/")
                    return render(request, "admin/management/alter_athlete.html", locals())
                ath_form = forms.AthleteForm()
                return render(request, "admin/management/alter_athlete.html", locals())
        else:
            return redirect("/bfb/directory/")
    else:
        return redirect("/bfb/community/login/")


def delete_athlete(request, match_id, team_id, ath_id):
    if request.session.get('is_login', None):
        if request.session.get("is_superuser") == 1:
            try:
                match = Match.Match.objects.get(id=match_id)
                team = Match.Team.objects.get(id=team_id)
                a_athlete = Match.Athlete.objects.get(id=ath_id)
            except Match.Match.DoesNotExist:
                raise Http404("比赛不存在！")
            except Match.Team.DoesNotExist:
                raise Http404("队伍不存在！")
            except Match.Athlete.DoesNotExist:
                raise Http404("队员不存在！")
            else:
                if request.method == 'POST':
                    a_athlete.delete()
                return redirect(f"/bfb/management/game_id%3F={match_id}/team/alter_id%3F={team_id}/athlete/")
        else:
            return redirect("/bfb/directory/")
    else:
        return redirect("/bfb/community/login/")


def contest_update(request, match_id):
    if request.session.get('is_login', None):
        if request.session.get("is_superuser") == 1:
            try:
                game = Match.Match.objects.get(id=match_id)
            except Match.Match.DoesNotExist:
                raise Http404("比赛不存在！")
            else:
                if game.match_state.match_progress == 'group':
                    Rules.default_score_calculate(game, -1)
                return redirect(f"/bfb/management/game_id%3F={game.id}/contest/")
        else:
            return redirect("/bfb/directory/")
    else:
        return redirect("/bfb/community/login/")
