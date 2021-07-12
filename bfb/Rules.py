"""
@ Author: wyfffffei
@ Project: tyb
@ File: Rules.py
@ Time: 2021/3/11 16:38
@ Function:  match_rules
"""
from django.db import transaction
from . import Match
import random

# rule_choices = Match.Match.rule_choices
# Rules must be in rule_choices !!


class BaseRules:
    rule_choices = Match.Match.rule_choices
    group_choices = Match.Team.team_group_choices

    def __init__(self, team_num=None, group_num=None, rule=None):
        if isinstance(team_num, int) and team_num > 0:
            self.team_num = team_num
        else:
            self.team_num = 0

        if isinstance(group_num, int) and 0 < group_num < 5:
            self.group_num = group_num
        else:
            self.group_num = 0

        if rule in self.rule_choices:
            self.rule = rule
        else:
            self.rule = self.rule_choices[0]

    def team_init(self, new_match):
        """
        :param new_match: team->match
        :return: true/false
        """
        if not isinstance(self.team_num, int):
            return False
        if self.team_num <= 0:
            return False

        with transaction.atomic():
            for i in range(self.team_num):
                new_team = Match.Team.objects.create(matcht=new_match, team_name="temp"+str(i))
                Match.Score.objects.create(belong_team=new_team)
        return True

    def team_group_init(self, teams):
        if not isinstance(self.group_num, int):
            return False
        if self.group_num <= 0:
            return False
        teams = teams if teams else []
        if len(teams) < self.group_num:
            return False

        # 队伍按组平分，多的按序平摊
        group_head = head = int(len(teams) / self.group_num)
        tail = len(teams) % self.group_num

        i = 0
        for team in teams:
            if head == 0:
                i += 1
                head = group_head
                if tail != 0:
                    team.team_group = self.group_choices[i-1][0]
                    team.save(update_fields=['team_group'])
                    tail -= 1
                    continue
            team.team_group = self.group_choices[i][0]
            team.save(update_fields=['team_group'])
            head -= 1
        return True

    def contest_group_init(self, new_match):
        if not isinstance(self.team_num, int):
            return False
        if self.team_num <= 0:
            return False

        with transaction.atomic():
            for num in range(4):
                teams = Match.Team.objects.filter(matcht=new_match, team_group=self.group_choices[num][0])
                if not teams:
                    break
                for i in range(len(teams)):
                    for j in range(i+1, len(teams)):
                        contest = teams[i].contest.create(matchc=new_match)
                        teams[j].contest.add(contest)
        return True

    def state_check(self, match):
        return default_match_state_check(match, match.match_state.match_progress, match.match_state.dieout_progress,
                                         self.team_num, self.group_num)

    @classmethod
    def score_calculate(cls, match, state):
        default_score_calculate(match, state)

    def dieout_contest_create(self, e_match, state, team_all_update):
        promoted_teams = list()
        if state == -1:
            # 每场比赛分数加入，计算rank
            self.score_calculate(e_match, state)
            e_match.match_state.match_progress = 'dieout'
            e_match.match_state.dieout_progress = 1
            e_match.match_state.save(update_fields=['dieout_progress', 'match_progress'])

            # 队伍晋级逻辑
            num_promotion = 2 if int(self.team_num / self.group_num) > 2 else 1

            # 晋级队伍状态切换
            # 晋级队伍列表：promoted_teams
            for i in range(self.group_num):
                promoted_teams.append(list())
            tem = 0
            for team in team_all_update:
                team.isOut = "out"
                if num_promotion == 1:
                    if team.score.rank == 1:
                        team.isOut = 'dieout'
                        promoted_teams[tem].append(team)
                        tem += 1
                if num_promotion == 2:
                    for i in range(len(self.group_choices)):
                        if team.team_group == self.group_choices[i][0]:
                            if team.score.rank == 1:
                                team.isOut = 'dieout'
                                promoted_teams[i].append(team)
                                break
                            if team.score.rank == 2:
                                team.isOut = 'dieout'
                                promoted_teams[i].insert(0, team)
                                break
                team.save()
            if self.group_num == 1:
                if len(promoted_teams[0]) == 1:
                    self.go2end(e_match, promoted_teams[0][0].team_name)
            else:
                # 创建第一阶段淘汰赛
                contests_exist = Match.Contest.objects.filter(matchc=e_match, dieout_progress=1)
                if contests_exist:
                    for contest in contests_exist:
                        try:
                            Match.Contest.objects.get(id=contest.id).delete()
                        except:
                            pass
                while promoted_teams:
                    team1 = random.choice(promoted_teams)
                    promoted_teams.remove(team1)
                    if promoted_teams:
                        team2 = random.choice(promoted_teams)
                        promoted_teams.remove(team2)
                    else:
                        break

                    if num_promotion == 1:
                        contest = team1[0].contest.create(matchc=e_match, contest_style='dieout', dieout_progress=1)
                        team2[0].contest.add(contest)
                    if num_promotion == 2:
                        contest = team1[0].contest.create(matchc=e_match, contest_style='dieout', dieout_progress=1)
                        team2[1].contest.add(contest)
                        contest = team1[1].contest.create(matchc=e_match, contest_style='dieout', dieout_progress=1)
                        team2[0].contest.add(contest)

        elif state in {1, 2, 3}:
            e_match.match_state.dieout_progress = state + 1
            e_match.match_state.save(update_fields=['dieout_progress'])

            # 结束上阶段的比赛，筛去已淘汰的队伍，创建下一阶段的比赛，切换比赛的状态（判断）
            ended_contests = Match.Contest.objects.filter(matchc=e_match, contest_style='dieout', dieout_progress=state)
            for contest in ended_contests:
                team1 = contest.battle_teams.all()[0]
                team2 = contest.battle_teams.all()[1]
                contest.cs1 = int(contest.cs1)
                contest.cs2 = int(contest.cs2)
                if contest.cs2 > contest.cs1:
                    team1.isOut = 'out'
                    team1.save()
                    promoted_teams.append(team2)
                else:
                    team2.isOut = 'out'
                    team2.save()
                    promoted_teams.append(team1)
                contest.contest_state = 'ended'
                contest.save()
            if len(promoted_teams) == 1:
                self.go2end(e_match, promoted_teams[0].team_name)
            else:
                contests_exist = Match.Contest.objects.filter(matchc=e_match, dieout_progress=state+1)
                if contests_exist:
                    for contest in contests_exist:
                        try:
                            Match.Contest.objects.get(id=contest.id).delete()
                        except:
                            pass
                while promoted_teams:
                    team1 = random.choice(promoted_teams)
                    promoted_teams.remove(team1)
                    if promoted_teams:
                        team2 = random.choice(promoted_teams)
                        promoted_teams.remove(team2)
                    else:
                        break
                    contest = team1.contest.create(matchc=e_match, contest_style='dieout', dieout_progress=state+1)
                    team2.contest.add(contest)

        else:
            # 比赛已结束
            self.go2end(e_match)

    @classmethod
    def start(cls, match):
        match.match_state.match_stage = 'inprogress'
        match.match_state.save()

    @classmethod
    def go2end(cls, match, champion=None, sec=None, thi=None, fou=None):
        champion = "待定" if champion is None else champion
        sec = "待定" if sec is None else sec
        thi = "待定" if thi is None else thi
        fou = "待定" if fou is None else fou

        result = match.result
        result.result_1st = champion
        result.result_2nd = sec
        result.result_3rd = thi
        result.result_4th = fou
        result.save()

        state = match.match_state
        state.match_stage = 'ended'
        state.match_progress = 'end'
        state.save()


# Important!!!
def default_match_state_check(match, match_progress, dieout_progress, team_num, group_num):
    """
    :param match: 核对的赛事
    :param match_progress: 切换后赛事的状态
    :function: 核对队伍数量，分组校验；赛事数量（小组赛，淘汰赛）；比分合法性
    :return: {"error_message":"...", "state":-1,1,2,3,4,100} -> 有问题返回问题，没问题返回比赛阶段
    :state.options: {"-1":小组赛阶段, "1,2,3,4":淘汰赛阶段, "100":结束}
    """
    result = {}
    rules_list = list()
    for choice in Match.Match.rule_choices:
        rules_list.append(choice[0])
    if match.match_rule in rules_list:
        team_all = Match.Team.objects.filter(matcht=match)
        if len(team_all) != team_num:
            result['error_message'] = "球队数量错误！"
            return result

        group_head = int(team_num / group_num)
        tail = team_num % group_num
        for i in range(group_num):
            teams = Match.Team.objects.filter(matcht=match, team_group=Match.Team.team_group_choices[i][0])
            if tail != 0:
                head = group_head + 1
                tail -= 1
            else:
                head = group_head
            if len(teams) != head:
                result['error_message'] = "分组数量错误！"
                break

        if match_progress == 'group':
            try:
                contest_group = Match.Contest.objects.filter(matchc=match, contest_style='group')
            except Match.Contest.DoesNotExist:
                result['error_message'] = "小组赛未初始化！"
            else:
                # 小组赛数量计算
                group_head = int(team_num / group_num)
                tail = team_num % group_num
                right_contest_num = int(group_num * group_head * (group_head - 1) * 0.5 + tail * group_head)

                if len(contest_group) != right_contest_num:
                    result['error_message'] = f"小组赛数量应为{right_contest_num}，实为{len(contest_group)}！"
                else:
                    for game in contest_group:
                        game.cs1 = int(game.cs1)
                        game.cs2 = int(game.cs2)
                        if game.cs1 == game.cs2 or game.cs1 < 0 or game.cs2 < 0:
                            result['error_message'] = "小组赛尚未完全结束!"
                    if not result:
                        result['state'] = -1

        elif match_progress == 'dieout':
            try:
                contest_dieout = Match.Contest.objects.filter(matchc=match, contest_style='dieout')
            except Match.Contest.DoesNotExist:
                result['state'] = -1
            else:
                if int(dieout_progress) == -1:
                    result['error_message'] = "比赛阶段与淘汰赛状态不符！"
                    return result
                for game in contest_dieout:
                    game.cs1 = int(game.cs1)
                    game.cs2 = int(game.cs2)
                    if game.cs1 == game.cs2 or game.cs1 < 0 or game.cs2 < 0:
                        result['error_message'] = "淘汰赛尚未完全结束!"
                        return result

                dieout_progress_list = list()
                for choice in Match.Contest.progress_choices:
                    dieout_progress_list.append(choice[0])
                if int(dieout_progress) in dieout_progress_list:
                    contest_index = dieout_progress_list.index(int(dieout_progress))
                    contests = Match.Contest.objects.filter(matchc=match, dieout_progress=contest_index+1)
                    for i in range(contest_index+1):
                        group_num = group_num / 2
                    if group_num != len(contests) and group_num * 2 != len(contests):
                        result['error_message'] = f"阶段{contest_index+1}淘汰赛数量错误！"
                        return result
                    result['state'] = contest_index + 1
                else:
                    result['error_message'] = "淘汰赛阶段不合法！"
        else:
            result['state'] = 100
    else:
        result['error_message'] = "规则不合法！"
    return result


# Check, and then calculate!!
# Match_progress should be group!
def default_score_calculate(match, state):
    if state == -1:
        contest_group = Match.Contest.objects.filter(matchc=match, contest_style='group')
        team_all = Match.Team.objects.filter(matcht=match)

        # 小组赛数据初始化
        for team in team_all:
            team.score.score = 0
            team.score.netscore = 0
            team.score.num_win = 0
            team.score.num_lose = 0
            team.score.rank = 0
            team.score.save()

        # 小组赛得分计算
        for game in contest_group:
            ended = False
            team1 = game.battle_teams.all()[0]
            team2 = game.battle_teams.all()[1]
            game.cs1 = int(game.cs1)
            game.cs2 = int(game.cs2)
            if game.cs1 > game.cs2:
                team1.score.score += 2
                team1.score.netscore += (game.cs1 - game.cs2)
                team1.score.num_win += 1
                team2.score.netscore -= (game.cs1 - game.cs2)
                team2.score.num_lose += 1
                ended = True
            if game.cs1 < game.cs2:
                team2.score.score += 2
                team2.score.netscore += (game.cs2 - game.cs1)
                team2.score.num_win += 1
                team1.score.netscore -= (game.cs2 - game.cs1)
                team1.score.num_lose += 1
                ended = True
            team1.score.save()
            team2.score.save()
            if ended:
                game.contest_state = 'ended'
            game.save()

        # 根据得分计算排名
        score_all = Match.Score.objects.filter().order_by('-score', '-netscore')
        rank_list = [1, 1, 1, 1]
        group_list = list()
        for choice in Match.Team.team_group_choices:
            group_list.append(choice[0])
        for i in range(len(score_all)):
            if score_all[i].belong_team.matcht != match:
                continue
            if score_all[i].belong_team.team_group in group_list:
                score_all[i].rank = rank_list[group_list.index(score_all[i].belong_team.team_group)]
                score_all[i].save(update_fields=['rank'])
                rank_list[group_list.index(score_all[i].belong_team.team_group)] += 1
        return True
    else:
        return False
