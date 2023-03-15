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
from django.shortcuts import render
import csv
from io import TextIOWrapper, StringIO

# Create your views here.

class PersonList(generic.ListView):
    model = Person
    template_name = "score/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        login_user_id = self.request.user.id
        personlist = Person.objects.filter(login_user=login_user_id)
        person_user = Person.objects.values_list('login_user', flat=True).filter(login_user=login_user_id)
        if person_user.exists() == False:
            player_add = "プレイヤーを追加してください"
            context["player_add"] = player_add 

        paginator = Paginator(personlist, 10)
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
        stats = Stat.objects.filter(player=pk).order_by("date")
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
        
        df.columns = ["id", "player_id", "date", "スコア", "OB数", "ペナルティ数", "FWキープ率", "パーオン率", "パット数", "stat_number"]
        
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

        if Stat.objects.filter(player__sex="男性").values().exists() == True:

            #男性平均
            male_score_avgs = round(df_male[["player_id","total_score"]].groupby("player_id").mean()["total_score"].mean(), 1)
            male_ob_avgs = round(df_male[["player_id","ob"]].groupby("player_id").mean()["ob"].mean(), 1)
            male_penalty_avgs = round(df_male[["player_id","penalty"]].groupby("player_id").mean()["penalty"].mean(), 1)
            male_fw_avgs = round(df_male[["player_id","fw"]].groupby("player_id").mean()["fw"].mean(), 1)
            male_par_on_avgs = round(df_male[["player_id","par_on"]].groupby("player_id").mean()["par_on"].mean(), 1)
            male_putt_avgs = round(df_male[["player_id","putt"]].groupby("player_id").mean()["putt"].mean(), 1)

            #男それぞれの平均
            allmale_score_avg = df_male[["player_id","total_score","ob","penalty","fw","par_on","putt"]].groupby("player_id").mean()
            male_60 = allmale_score_avg[allmale_score_avg["total_score"] < 70]
            male_70 = allmale_score_avg[(allmale_score_avg["total_score"] >= 70) & (allmale_score_avg["total_score"] < 80)]
            male_80 = allmale_score_avg[(allmale_score_avg["total_score"] >= 80) & (allmale_score_avg["total_score"] < 90)]
            male_90 = allmale_score_avg[(allmale_score_avg["total_score"] >= 90) & (allmale_score_avg["total_score"] <  100)]
            male_100 = allmale_score_avg[(allmale_score_avg["total_score"] >= 100) & (allmale_score_avg["total_score"] < 110)]
            male_110 = allmale_score_avg[(allmale_score_avg["total_score"] >= 110) & (allmale_score_avg["total_score"] < 120)]
            male_120 = allmale_score_avg[allmale_score_avg["total_score"] >= 120]

            #男性60平均
            male_score_60 = round(male_60.mean()["total_score"], 1)
            male_ob_60 = round(male_60.mean()["ob"], 1)
            male_penalty_60 = round(male_60.mean()["penalty"], 1)
            male_fw_60 = round(male_60.mean()["fw"], 1)
            male_par_on_60 = round(male_60.mean()["par_on"], 1)
            male_putt_60 = round(male_60.mean()["putt"], 1)

            #男性70平均
            male_score_70 = round(male_70.mean()["total_score"], 1)
            male_ob_70 = round(male_70.mean()["ob"], 1)
            male_penalty_70 = round(male_70.mean()["penalty"], 1)
            male_fw_70 = round(male_70.mean()["fw"], 1)
            male_par_on_70 = round(male_70.mean()["par_on"], 1)
            male_putt_70 = round(male_70.mean()["putt"], 1)

            #男性80平均
            male_score_80 = round(male_80.mean()["total_score"], 1)
            male_ob_80 = round(male_80.mean()["ob"], 1)
            male_penalty_80 = round(male_80.mean()["penalty"], 1)
            male_fw_80 = round(male_80.mean()["fw"], 1)
            male_par_on_80 = round(male_80.mean()["par_on"], 1)
            male_putt_80 = round(male_80.mean()["putt"], 1)
            
            #男性90平均
            male_score_90 = round(male_90.mean()["total_score"], 1)
            male_ob_90 = round(male_90.mean()["ob"], 1)
            male_penalty_90 = round(male_90.mean()["penalty"], 1)
            male_fw_90 = round(male_90.mean()["fw"], 1)
            male_par_on_90 = round(male_90.mean()["par_on"], 1)
            male_putt_90 = round(male_90.mean()["putt"], 1)

            #男性100平均
            male_score_100 = round(male_100.mean()["total_score"], 1)
            male_ob_100 = round(male_100.mean()["ob"], 1)
            male_penalty_100 = round(male_100.mean()["penalty"], 1)
            male_fw_100 = round(male_100.mean()["fw"], 1)
            male_par_on_100 = round(male_100.mean()["par_on"], 1)
            male_putt_100 = round(male_100.mean()["putt"], 1)

            #男性110平均
            male_score_110 = round(male_110.mean()["total_score"], 1)
            male_ob_110 = round(male_110.mean()["ob"], 1)
            male_penalty_110 = round(male_110.mean()["penalty"], 1)
            male_fw_110 = round(male_110.mean()["fw"], 1)
            male_par_on_110 = round(male_110.mean()["par_on"], 1)
            male_putt_110 = round(male_110.mean()["putt"], 1)

            #男性120平均
            male_score_120 = round(male_120.mean()["total_score"], 1)
            male_ob_120 = round(male_120.mean()["ob"], 1)
            male_penalty_120 = round(male_120.mean()["penalty"], 1)
            male_fw_120 = round(male_120.mean()["fw"], 1)
            male_par_on_120 = round(male_120.mean()["par_on"], 1)
            male_putt_120 = round(male_120.mean()["putt"], 1)

            #男性平均cxt
            if f'{male_score_avgs}' != "nan":
                context["male_score_avgs"] = f'{male_score_avgs}'
                context["male_ob_avgs"] = f'{male_ob_avgs}'+"回"
                context["male_penalty_avgs"] = f'{male_penalty_avgs}'+"回"
                context["male_fw_avgs"] = f'{male_fw_avgs}'+"%"
                context["male_par_on_avgs"] = f'{male_par_on_avgs}'+"%"
                context["male_putt_avgs"] = f'{male_putt_avgs}'
            
            #男性60平均cxtf'{}'+""
            if f'{male_score_60}' != "nan":
                context["male_score_60"] = male_score_60
                context["male_ob_60"] = f'{male_ob_60}'+"回"
                context["male_penalty_60"] = f'{male_penalty_60}'+"回"
                context["male_fw_60"] = f'{male_fw_60}'+"%"
                context["male_par_on_60"] = f'{male_par_on_60}'+"%"
                context["male_putt_60"] = f'{male_putt_60}'

            #男性70平均cxt
            if f'{male_score_70}' != "nan":
                context["male_score_70"] = male_score_70
                context["male_ob_70"] = f'{male_ob_70}'+"回"
                context["male_penalty_70"] = f'{male_penalty_70}'+"回"
                context["male_fw_70"] = f'{male_fw_70}'+"%"
                context["male_par_on_70"] = f'{male_par_on_70}'+"%"
                context["male_putt_70"] = f'{male_putt_70}'

            #男性80平均cxt
            if f'{male_score_80}' != "nan":
                context["male_score_80"] = male_score_80
                context["male_ob_80"] = f'{male_ob_80}'+"回"
                context["male_penalty_80"] = f'{male_penalty_80}'+"回"
                context["male_fw_80"] = f'{male_fw_80}'+"%"
                context["male_par_on_80"] = f'{male_par_on_80}'+"%"
                context["male_putt_80"] = f'{male_putt_80}'

            #男性90平均cxt
            if f'{male_score_90}' != "nan":
                context["male_score_90"] = male_score_90
                context["male_ob_90"] = f'{male_ob_90}'+"回"
                context["male_penalty_90"] = f'{male_penalty_90}'+"回"
                context["male_fw_90"] = f'{male_fw_90}'+"%"
                context["male_par_on_90"] = f'{male_par_on_90}'+"%"
                context["male_putt_90"] = f'{male_putt_90}'
                
            #男性100平均cxt
            if f'{male_score_100}' != "nan":
                context["male_score_100"] = male_score_100
                context["male_ob_100"] = f'{male_ob_100}'+"回"
                context["male_penalty_100"] = f'{male_penalty_100}'+"回"
                context["male_fw_100"] = f'{male_fw_100}'+"%"
                context["male_par_on_100"] = f'{male_par_on_100}'+"%"
                context["male_putt_100"] = f'{male_putt_100}'

            if f'{male_score_110}' != "nan":
                context["male_score_110"] = male_score_110
                context["male_ob_110"] = f'{male_ob_110}'+"回"
                context["male_penalty_110"] = f'{male_penalty_110}'+"回"
                context["male_fw_110"] = f'{male_fw_110}'+"%"
                context["male_par_on_110"] = f'{male_par_on_110}'+"%"
                context["male_putt_110"] = f'{male_putt_110}'

            if f'{male_score_120}' != "nan":
                context["male_score_120"] = male_score_120
                context["male_ob_120"] = f'{male_ob_120}'+"回"
                context["male_penalty_120"] = f'{male_penalty_120}'+"回"
                context["male_fw_120"] = f'{male_fw_120}'+"%"
                context["male_par_on_120"] = f'{male_par_on_120}'+"%"
                context["male_putt_120"] = f'{male_putt_120}'
                
        #女性↓

        if Stat.objects.filter(player__sex="女性").values().exists() == True:

            #女性平均
            female_score_avgs = round(df_female[["player_id","total_score"]].groupby("player_id").mean()["total_score"].mean(), 1)
            female_ob_avgs = round(df_female[["player_id","ob"]].groupby("player_id").mean()["ob"].mean(), 1)
            female_penalty_avgs = round(df_female[["player_id","penalty"]].groupby("player_id").mean()["penalty"].mean(), 1)
            female_fw_avgs = round(df_female[["player_id","fw"]].groupby("player_id").mean()["fw"].mean(), 1)
            female_par_on_avgs = round(df_female[["player_id","par_on"]].groupby("player_id").mean()["par_on"].mean(), 1)
            female_putt_avgs = round(df_female[["player_id","putt"]].groupby("player_id").mean()["putt"].mean(), 1)

            #女性それぞれの平均
            allfemale_score_avg = df_female[["player_id","total_score","ob","penalty","fw","par_on","putt"]].groupby("player_id").mean()
            female_60 = allfemale_score_avg[allfemale_score_avg["total_score"] < 70]
            female_70 = allfemale_score_avg[(allfemale_score_avg["total_score"] >= 70) & (allfemale_score_avg["total_score"] < 80)]
            female_80 = allfemale_score_avg[(allfemale_score_avg["total_score"] >= 80) & (allfemale_score_avg["total_score"] < 90)]
            female_90 = allfemale_score_avg[(allfemale_score_avg["total_score"] >= 90) & (allfemale_score_avg["total_score"] <  100)]
            female_100 = allfemale_score_avg[(allfemale_score_avg["total_score"] >= 100) & (allfemale_score_avg["total_score"] < 110)]
            female_110 = allfemale_score_avg[(allfemale_score_avg["total_score"] >= 110) & (allfemale_score_avg["total_score"] < 120)]
            female_120 = allfemale_score_avg[allfemale_score_avg["total_score"] >= 120]

            #女性60平均
            female_score_60 = round(female_60.mean()["total_score"], 1)
            female_ob_60 = round(female_60.mean()["ob"], 1)
            female_penalty_60 = round(female_60.mean()["penalty"], 1)
            female_fw_60 = round(female_60.mean()["fw"], 1)
            female_par_on_60 = round(female_60.mean()["par_on"], 1)
            female_putt_60 = round(female_60.mean()["putt"], 1)

            #女性70平均
            female_score_70 = round(female_70.mean()["total_score"], 1)
            female_ob_70 = round(female_70.mean()["ob"], 1)
            female_penalty_70 = round(female_70.mean()["penalty"], 1)
            female_fw_70 = round(female_70.mean()["fw"], 1)
            female_par_on_70 = round(female_70.mean()["par_on"], 1)
            female_putt_70 = round(female_70.mean()["putt"], 1)

            #女性80平均
            female_score_80 = round(female_80.mean()["total_score"], 1)
            female_ob_80 = round(female_80.mean()["ob"], 1)
            female_penalty_80 = round(female_80.mean()["penalty"], 1)
            female_fw_80 = round(female_80.mean()["fw"], 1)
            female_par_on_80 = round(female_80.mean()["par_on"], 1)
            female_putt_80 = round(female_80.mean()["putt"], 1)
            
            #女性90平均
            female_score_90 = round(female_90.mean()["total_score"], 1)
            female_ob_90 = round(female_90.mean()["ob"], 1)
            female_penalty_90 = round(female_90.mean()["penalty"], 1)
            female_fw_90 = round(female_90.mean()["fw"], 1)
            female_par_on_90 = round(female_90.mean()["par_on"], 1)
            female_putt_90 = round(female_90.mean()["putt"], 1)

            #女性100平均
            female_score_100 = round(female_100.mean()["total_score"], 1)
            female_ob_100 = round(female_100.mean()["ob"], 1)
            female_penalty_100 = round(female_100.mean()["penalty"], 1)
            female_fw_100 = round(female_100.mean()["fw"], 1)
            female_par_on_100 = round(female_100.mean()["par_on"], 1)
            female_putt_100 = round(female_100.mean()["putt"], 1)

            #女性110平均
            female_score_110 = round(female_110.mean()["total_score"], 1)
            female_ob_110 = round(female_110.mean()["ob"], 1)
            female_penalty_110 = round(female_110.mean()["penalty"], 1)
            female_fw_110 = round(female_110.mean()["fw"], 1)
            female_par_on_110 = round(female_110.mean()["par_on"], 1)
            female_putt_110 = round(female_110.mean()["putt"], 1)

            #女性120平均
            female_score_120 = round(female_120.mean()["total_score"], 1)
            female_ob_120 = round(female_120.mean()["ob"], 1)
            female_penalty_120 = round(female_120.mean()["penalty"], 1)
            female_fw_120 = round(female_120.mean()["fw"], 1)
            female_par_on_120 = round(female_120.mean()["par_on"], 1)
            female_putt_120 = round(female_120.mean()["putt"], 1)

            #女性平均cxt
            if f'{female_score_avgs}' != "nan":
                context["female_score_avgs"] = f'{female_score_avgs}'
                context["female_ob_avgs"] = f'{female_ob_avgs}'+"回"
                context["female_penalty_avgs"] = f'{female_penalty_avgs}'+"回"
                context["female_fw_avgs"] = f'{female_fw_avgs}'+"%"
                context["female_par_on_avgs"] = f'{female_par_on_avgs}'+"%"
                context["female_putt_avgs"] = f'{female_putt_avgs}'

            #女性60平均cxtf'{}'+""
            if f'{female_score_60}' != "nan":
                context["female_score_60"] = female_score_60
                context["female_ob_60"] = f'{female_ob_60}'+"回"
                context["female_penalty_60"] = f'{female_penalty_60}'+"回"
                context["female_fw_60"] = f'{female_fw_60}'+"%"
                context["female_par_on_60"] = f'{female_par_on_60}'+"%"
                context["female_putt_60"] = f'{female_putt_60}'

            #女性70平均cxt
            if f'{female_score_70}' != "nan":
                context["female_score_70"] = female_score_70
                context["female_ob_70"] = f'{female_ob_70}'+"回"
                context["female_penalty_70"] = f'{female_penalty_70}'+"回"
                context["female_fw_70"] = f'{female_fw_70}'+"%"
                context["female_par_on_70"] = f'{female_par_on_70}'+"%"
                context["female_putt_70"] = f'{female_putt_70}'

            #女性80平均cxt
            if f'{female_score_80}' != "nan":
                context["female_score_80"] = female_score_80
                context["female_ob_80"] = f'{female_ob_80}'+"回"
                context["female_penalty_80"] = f'{female_penalty_80}'+"回"
                context["female_fw_80"] = f'{female_fw_80}'+"%"
                context["female_par_on_80"] = f'{female_par_on_80}'+"%"
                context["female_putt_80"] = f'{female_putt_80}'

            #女性90平均cxt
            if f'{female_score_90}' != "nan":
                context["female_score_90"] = female_score_90
                context["female_ob_90"] = f'{female_ob_90}'+"回"
                context["female_penalty_90"] = f'{female_penalty_90}'+"回"
                context["female_fw_90"] = f'{female_fw_90}'+"%"
                context["female_par_on_90"] = f'{female_par_on_90}'+"%"
                context["female_putt_90"] = f'{female_putt_90}'
                
            #女性100平均cxt
            if f'{female_score_100}' != "nan":
                context["female_score_100"] = female_score_100
                context["female_ob_100"] = f'{female_ob_100}'+"回"
                context["female_penalty_100"] = f'{female_penalty_100}'+"回"
                context["female_fw_100"] = f'{female_fw_100}'+"%"
                context["female_par_on_100"] = f'{female_par_on_100}'+"%"
                context["female_putt_100"] = f'{female_putt_100}'

            if f'{female_score_110}' != "nan":
                context["female_score_110"] = female_score_110
                context["female_ob_110"] = f'{female_ob_110}'+"回"
                context["female_penalty_110"] = f'{female_penalty_110}'+"回"
                context["female_fw_110"] = f'{female_fw_110}'+"%"
                context["female_par_on_110"] = f'{female_par_on_110}'+"%"
                context["female_putt_110"] = f'{female_putt_110}'

            if f'{female_score_120}' != "nan":
                context["female_score_120"] = female_score_120
                context["female_ob_120"] = f'{female_ob_120}'+"回"
                context["female_penalty_120"] = f'{female_penalty_120}'+"回"
                context["female_fw_120"] = f'{female_fw_120}'+"%"
                context["female_par_on_120"] = f'{female_par_on_120}'+"%"
                context["female_putt_120"] = f'{female_putt_120}'



        return context
    
def upload(request):
    if 'csv' in request.FILES:
        form_data = TextIOWrapper(request.FILES['csv'].file, encoding='utf-8')
        csv_file = csv.reader(form_data)
        for line in csv_file:
            person, created = Person.objects.get_or_create(player_number=line[1])
            person.login_user = request.user.id
            person.name =line[0]
            person.age = line[2]
            person.sex = line[3]
            person.save()

            stat_number_check = Stat.objects.values("stat_number").all()
            if line[11] not in f'{stat_number_check}':
            
                Stat.objects.create(
                    player = Person.objects.get(player_number=line[1]),
                    stat_number = line[11],
                    date = line[4],
                    total_score = line[5],
                    ob = line[6],
                    penalty = line[7],
                    fw = line[8],
                    par_on = line[9],
                    putt = line[10],

                )
            

        return render(request, 'score/upload.html')

    else:
        return render(request, 'score/upload.html')
    