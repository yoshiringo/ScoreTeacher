from django.views import generic
from .models import Person, Stat
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from .forms import StatCreateForm, PersonCreateForm
import pandas as pd
import numpy as np
import random
from . import plugin_plotly
from django.http import HttpResponse
from django.core.paginator import Paginator
from .forms import PersonCreateForm
from django.db.models import Avg



# Create your views here.

class PersonList(generic.ListView):
    model = Person
    template_name = "score/index.html"
    paginate_by = 3

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        login_user_id = self.request.user.id
        personlist = Person.objects.filter(login_user=login_user_id)
        person_user = Person.objects.values_list('login_user', flat=True).filter(login_user=login_user_id)
        if person_user.exists() == False:
            player_add = "プレイヤーを追加してください"
            context["player_add"] = player_add 

        paginator = Paginator(personlist, 2)
        p = self.request.GET.get('p')
        persons = paginator.get_page(p)

        context["persons"] = persons
        context["person_user"] = person_user

        return context

class StatCreate(generic.CreateView):
    template_name = "score/detail.html"
    ordering = ('date')
    form_class = StatCreateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get("pk")
        person = get_object_or_404(Person, pk=pk)
        context["person"] = person
        stats = Stat.objects.filter(player=pk)
        context['breadcrumbs_list'] = [{'name': 'Stats',
                                         'url': ''}]
        stats_str = f'{stats}'
        check = any(map(str.isdigit, stats_str))
        context["check"] = check

        paginator = Paginator(stats, 5)
        p = self.request.GET.get('p')
        stat_p = paginator.get_page(p)
        context["stat_p"] = stat_p

        score_avg = Stat.objects.filter(player=pk).aggregate(Avg("total_score"))
        score_avg = f'{score_avg}'
        score_avg_check = any(map(str.isdigit, score_avg))
        if score_avg_check == True:
            score_avg = float(score_avg.replace("{'total_score__avg': ", "").replace("}", ""))
            score_avg = round(score_avg, 1)
            context["score_avg"] = score_avg
                    
        ob_avg = Stat.objects.filter(player=pk).aggregate(Avg("ob"))
        ob_avg = f'{ob_avg}'
        ob_avg_check = any(map(str.isdigit, ob_avg))
        if  ob_avg_check == True:
            ob_avg = float(ob_avg.replace("{'ob__avg': ", "").replace("}", ""))
            ob_avg = round(ob_avg, 1)
            context["ob_avg"] = ob_avg

        penalty_avg = Stat.objects.filter(player=pk).aggregate(Avg("penalty"))
        penalty_avg = f'{penalty_avg}'
        score_avg_check = any(map(str.isdigit, penalty_avg))
        if  score_avg_check == True:
            penalty_avg = float(penalty_avg.replace("{'penalty__avg': ", "").replace("}", ""))
            penalty_avg = round(penalty_avg, 1)
            context["penalty_avg"] = penalty_avg

        fw_avg = Stat.objects.filter(player=pk).aggregate(Avg("fw"))
        fw_avg = f'{fw_avg}'
        score_avg_check = any(map(str.isdigit, fw_avg))
        if  score_avg_check == True:
            fw_avg = float(fw_avg.replace("{'fw__avg': ", "").replace("}", ""))
            fw_avg = round(fw_avg, 1)
            context["fw_avg"] = fw_avg
        
        par_on_avg = Stat.objects.filter(player=pk).aggregate(Avg("par_on"))
        par_on_avg = f'{par_on_avg}'
        score_avg_check = any(map(str.isdigit, par_on_avg))
        if  score_avg_check == True:
            par_on_avg = float(par_on_avg.replace("{'par_on__avg': ", "").replace("}", ""))
            par_on_avg = round(par_on_avg, 1)
            context["par_on_avg"] = par_on_avg

        putt_avg = Stat.objects.filter(player=pk).aggregate(Avg("putt"))
        putt_avg = f'{putt_avg}'
        score_avg_check = any(map(str.isdigit, putt_avg))
        if  score_avg_check == True:
            putt_avg = float(putt_avg.replace("{'putt__avg': ", "").replace("}", ""))
            putt_avg = round(putt_avg, 1)
            context["putt_avg"] = putt_avg
        
        return context

    def form_valid(self, form):
        post = form.save(commit=False)
        post.player_id = self.kwargs.get("pk")
        post.save()

        return super().form_valid(form)

    def get_success_url(self):
        pk = self.kwargs.get("pk")

        return reverse_lazy("score:detail", kwargs={"pk": pk})

class PersonCreate(generic.CreateView):
    model = Person
    template_name = 'score/person_create.html'
    form_class = PersonCreateForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs_list'] = [{'name': 'プレイヤー追加',
                                        'url': ''}]
        context["persons"]   = Person.objects.all()

        context["sexs"] = [ p[0] for p in Person.sex.field.choices ]

        return context

    def form_valid(self, form):
        post = form.save(commit=False)
        post.login_user = self.request.user.id
        post.save()

        return super().form_valid(form)
    

    def get_success_url(self):
        pk = self.request.user.id

        return reverse_lazy('score:person_list')
    
class StatAnalyze(generic.DetailView):
    model = Person
    template_name = "score/stat_analyze.html"
    context_object_name = "person_stat"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get("pk")

        context['breadcrumbs_list'] = [
        {'name': 'Stats', 'url': f'/score/detail/{pk}/'},
        {'name': '分析結果','url': ''}
        ]

        df = pd.DataFrame(Stat.objects.filter(player_id=pk).values())
        
        df.columns = ["id", "player_id", "date", "スコア", "OB数", "ペナルティ数", "FWキープ率", "パーオン率", "パット数"]
        
        df_score = df.sort_values("スコア")
        data_count = df["スコア"].count()
        
        df_patt = df.sort_values(by=["パット数","スコア"])
        patt_count = [abs(df_patt.index.get_loc(i) - df_score.index.get_loc(i)) for i in range(data_count)]
        patt_score = sum(patt_count)
        
        df_fk = df.sort_values(by=["FWキープ率","スコア"], ascending=[False,True])
        fk_count = [abs(df_fk.index.get_loc(i) - df_score.index.get_loc(i)) for i in range(data_count)]
        fk_score = sum(fk_count)
        
        df_po = df.sort_values(by=["パーオン率","スコア"], ascending=[False,True])
        po_count = [abs(df_po.index.get_loc(i) - df_score.index.get_loc(i)) for i in range(data_count)]
        po_score = sum(po_count)
        
        df_ob = df.sort_values(by=["OB数","スコア"])
        ob_count = [abs(df_ob.index.get_loc(i) - df_score.index.get_loc(i)) for i in range(data_count)]
        ob_score = sum(ob_count)
        
        df_pn = df.sort_values(by=["ペナルティ数","スコア"])
        pn_count = [abs(df_pn.index.get_loc(i) - df_score.index.get_loc(i)) for i in range(data_count)]
        pn_score = sum(pn_count)
        
        calc_add = 1/(ob_score+1) + 1/(pn_score+1) + 1/(fk_score+1) + 1/(po_score+1) + 1/(patt_score+1)
        cf = 100 / calc_add

        result = {"OB": round(cf / (ob_score+1), 1), "ペナルティ": round(cf / (pn_score+1), 1), "FWキープ": round(cf / (fk_score+1), 1), "パーオン": round(cf / (po_score+1), 1), "パット": round(cf / (patt_score+1),1)}

        practice = sorted(result.items(), key=lambda i: i[1], reverse=True)
        result = practice[0][0],practice[1][0],practice[2][0],practice[3][0],practice[4][0]
        number = practice[0][1],practice[1][1],practice[2][1],practice[3][1],practice[4][1]

        result_a = f'{result}'
        result_b = result_a.translate(str.maketrans({"(": "", ")": "", "'": ""}))
        
        context["result"] = result
        context["practice"] = practice
        context["number"] = number
        context["result_b"] = result_b

        pie = [pie for pie in number]
        label = [label for label in result]
        chart = plugin_plotly.Plot_PieChart(pie, label)
        context["chart"] = chart

        return context

class StatDelete(generic.DeleteView):
    model = Stat
    template_name = 'score/person_create.html'
    def get_success_url(self):
        player_pk = self.object.player.pk
        return reverse_lazy('score:detail', kwargs={'pk': player_pk})

class PersonDelete(generic.DeleteView):
    model = Person

    def get_success_url(self):
        return reverse_lazy('score:person_list')

class Average(generic.ListView):
    model = Stat
    template_name = "score/average.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        df_male = pd.DataFrame(Stat.objects.filter(player__sex="男性").values())
        df_female = pd.DataFrame(Stat.objects.filter(player__sex="女性").values())
        male_score_avgs = round(df_male[["player_id","total_score"]].groupby("player_id").mean()["total_score"].mean(), 1)
        male_ob_avgs = round(df_male[["player_id","ob"]].groupby("player_id").mean()["ob"].mean(), 1)
        male_penalty_avgs = round(df_male[["player_id","penalty"]].groupby("player_id").mean()["penalty"].mean(), 1)
        male_fw_avgs = round(df_male[["player_id","fw"]].groupby("player_id").mean()["fw"].mean(), 1)
        male_par_on_avgs = round(df_male[["player_id","par_on"]].groupby("player_id").mean()["par_on"].mean(), 1)
        male_putt_avgs = round(df_male[["player_id","putt"]].groupby("player_id").mean()["putt"].mean(), 1)

        female_score_avgs = round(df_female[["player_id","total_score"]].groupby("player_id").mean()["total_score"].mean(), 1)
        female_ob_avgs = round(df_female[["player_id","ob"]].groupby("player_id").mean()["ob"].mean(), 1)
        female_penalty_avgs = round(df_female[["player_id","penalty"]].groupby("player_id").mean()["penalty"].mean(), 1)
        female_fw_avgs = round(df_female[["player_id","fw"]].groupby("player_id").mean()["fw"].mean(), 1)
        female_par_on_avgs = round(df_female[["player_id","par_on"]].groupby("player_id").mean()["par_on"].mean(), 1)
        female_putt_avgs = round(df_female[["player_id","putt"]].groupby("player_id").mean()["putt"].mean(), 1)

        context["male_score_avgs"] = male_score_avgs
        context["male_ob_avgs"] = male_ob_avgs
        context["male_penalty_avgs"] = male_penalty_avgs
        context["male_fw_avgs"] = male_fw_avgs
        context["male_par_on_avgs"] = male_par_on_avgs
        context["male_putt_avgs"] = male_putt_avgs

        context["female_score_avgs"] = female_score_avgs
        context["female_ob_avgs"] = female_ob_avgs
        context["female_penalty_avgs"] = female_penalty_avgs
        context["female_fw_avgs"] = female_fw_avgs
        context["female_par_on_avgs"] = female_par_on_avgs
        context["female_putt_avgs"] = female_putt_avgs

        return context