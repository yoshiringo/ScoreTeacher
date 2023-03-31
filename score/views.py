from django.views import generic
from .models import Person, Stat
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from .forms import StatCreateForm, PersonCreateForm, CSVUploadForm
import pandas as pd
from . import plugin_plotly
from django.core.paginator import Paginator
from .forms import PersonCreateForm
from django.db.models import Avg
from django.shortcuts import redirect
import csv
import io
from django.contrib import messages
from sklearn.linear_model import LinearRegression
import numpy as np
from django.http import HttpResponse
import csv,urllib

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
            context["player_add"] = "プレイヤーを追加してください" 

        persons = Paginator(personlist, 10).get_page(self.request.GET.get('p'))

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
        context["person"] = get_object_or_404(Person, pk=pk)
        stats = Stat.objects.filter(player=pk).order_by("date")
        context['breadcrumbs_list'] = [{'name': 'Stats',
                                         'url': ''}]
        stats_str = f'{stats}'
        context["check"] = any(map(str.isdigit, stats_str))
        context["stat_p"] = Paginator(stats, 10).get_page(self.request.GET.get('p'))

        if Stat.objects.filter(player=pk).all().exists() == True:

            score_avg = Stat.objects.filter(player=pk).aggregate(Avg("total_score"))
            score_avg = f'{score_avg}'
            context["score_avg"] = round(float(score_avg.replace("{'total_score__avg': ", "").replace("}", "")),1)

            putt_avg = Stat.objects.filter(player=pk).aggregate(Avg("putt"))
            putt_avg = f'{putt_avg}'
            context["putt_avg"] = round(float(putt_avg.replace("{'putt__avg': ", "").replace("}", "")), 1)

            fw_avg = Stat.objects.filter(player=pk).aggregate(Avg("fw"))
            fw_avg = f'{fw_avg}'
            context["fw_avg"] = round(float(fw_avg.replace("{'fw__avg': ", "").replace("}", "")), 1)

            par_on_avg = Stat.objects.filter(player=pk).aggregate(Avg("par_on"))
            par_on_avg = f'{par_on_avg}'
            context["par_on_avg"] = round(float(par_on_avg.replace("{'par_on__avg': ", "").replace("}", "")), 1)

            ob_avg = Stat.objects.filter(player=pk).aggregate(Avg("ob"))
            ob_avg = f'{ob_avg}'
            context["ob_avg"] = round(float(ob_avg.replace("{'ob__avg': ", "").replace("}", "")), 1)

            bunker_avg = Stat.objects.filter(player=pk).aggregate(Avg("bunker"))
            bunker_avg = f'{bunker_avg}'
            context["bunker_avg"] = round(float(bunker_avg.replace("{'bunker__avg': ", "").replace("}", "")), 1)

            penalty_avg = Stat.objects.filter(player=pk).aggregate(Avg("penalty"))
            penalty_avg = f'{penalty_avg}'
            context["penalty_avg"] = round(float(penalty_avg.replace("{'penalty__avg': ", "").replace("}", "")), 1)

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
        df.columns = ["id", "player_id", "date", "スコア", "パット", "FWキープ", "パーオン", "OB", "バンカー", "ペナルティ", "stat_number"]

        if len(df) > 7:
            #全stat
            z = df.drop(['id','player_id','date','stat_number'], axis=1)

            
            score_count = len(z)-1

            putt_true_count = f'{z.duplicated("パット")}'.count("True")
            if putt_true_count == score_count:
                z.iat[1,1] = 101

            fw_true_count = f'{z.duplicated("FWキープ")}'.count("True")
            if fw_true_count == score_count:
                z.iat[1,2] = 101

            par_true_count = f'{z.duplicated("パーオン")}'.count("True")
            if par_true_count == score_count:
                z.iat[1,3] = 101
            
            ob_true_count = f'{z.duplicated("OB")}'.count("True")
            if ob_true_count == score_count:
                z.iat[1,4] = 101

            bunker_true_count = f'{z.duplicated("バンカー")}'.count("True")
            if bunker_true_count == score_count:
                z.iat[1,5] = 101

            penalty_true_count = f'{z.duplicated("ペナルティ")}'.count("True")
            if penalty_true_count == score_count:
                z.iat[1,6] = 101            

            #statを標準化
            df_std = z.apply(lambda x: (x-x.mean())/x.std(), axis=0)
            #statのスコア以外
            x = df_std.drop(['スコア'], axis=1)
            #スコア
            y = df_std['スコア']

            reg = LinearRegression()
            results = reg.fit(x,y)
            coef = reg.coef_.round(4)
            n = x.shape[0]
            p = x.shape[1]

            y_hat = reg.predict(x)
            sse = np.sum((y - y_hat) **2, axis=0)
            sse = sse / (n - p - 1)
            s = np.linalg.inv(np.dot(x.T, x))
            std_err = np.sqrt(np.diagonal(sse * s)).round(4)

            t_values = (coef / std_err).round(4)
            t_values_abs = np.abs(t_values)
            col = ["パット", "FWキープ", "パーオン", "OB", "バンカー", "ペナルティ"]
            t_col = dict(zip(col, t_values_abs))
            practice = sorted(t_col.items(), key=lambda x:x[1], reverse=True)
        
        else:
            df_score = df.sort_values("スコア")
            data_count = df["スコア"].count()
            
            df_patt = df.sort_values(by=["パット","スコア"])
            patt_count = [abs(df_patt.index.get_loc(i) - df_score.index.get_loc(i)) for i in range(data_count)]
            patt_score = sum(patt_count)
            
            df_fk = df.sort_values(by=["FWキープ","スコア"], ascending=[False,True])
            fk_count = [abs(df_fk.index.get_loc(i) - df_score.index.get_loc(i)) for i in range(data_count)]
            fk_score = sum(fk_count)
            
            df_po = df.sort_values(by=["パーオン","スコア"], ascending=[False,True])
            po_count = [abs(df_po.index.get_loc(i) - df_score.index.get_loc(i)) for i in range(data_count)]
            po_score = sum(po_count)
            
            df_OB = df.sort_values(by=["OB","スコア"])
            OB_count = [abs(df_OB.index.get_loc(i) - df_score.index.get_loc(i)) for i in range(data_count)]
            OB_score = sum(OB_count)

            df_バンカー = df.sort_values(by=["バンカー","スコア"])
            バンカー_count = [abs(df_バンカー.index.get_loc(i) - df_score.index.get_loc(i)) for i in range(data_count)]
            バンカー_score = sum(バンカー_count)
            
            df_pn = df.sort_values(by=["ペナルティ","スコア"])
            pn_count = [abs(df_pn.index.get_loc(i) - df_score.index.get_loc(i)) for i in range(data_count)]
            pn_score = sum(pn_count)

            calc_add = 1/(OB_score+1) + 1/(pn_score+1) + 1/(fk_score+1) + 1/(po_score+1) + 1/(patt_score+1) + 1/(バンカー_score+1)
            cf = 100 / calc_add

            result = {"パット": round(cf / (patt_score+1),1), 
                      "FWキープ": round(cf / (fk_score+1), 1), 
                      "パーオン": round(cf / (po_score+1), 1), 
                      "OB": round(cf / (OB_score+1), 1), 
                      "バンカー": round(cf / (バンカー_score+1),1), 
                      "ペナルティ": round(cf / (pn_score+1), 1)}

            practice = sorted(result.items(), key=lambda i: i[1], reverse=True)
                
        result = practice[0][0],practice[1][0],practice[2][0],practice[3][0],practice[4][0],practice[5][0]
        number = practice[0][1],practice[1][1],practice[2][1],practice[3][1],practice[4][1],practice[5][1]

        result_a = f'{result}'.translate(str.maketrans({"(": "", ")": "", "'": ""}))

        context["chart"] = plugin_plotly.Plot_PieChart([pie for pie in number], [label for label in result])
        context["result_a"] = result_a        

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
            male_putt_avgs = round(df_male[["player_id","putt"]].groupby("player_id").mean()["putt"].mean(), 1)
            male_fw_avgs = round(df_male[["player_id","fw"]].groupby("player_id").mean()["fw"].mean(), 1)
            male_par_on_avgs = round(df_male[["player_id","par_on"]].groupby("player_id").mean()["par_on"].mean(), 1)
            male_ob_avgs = round(df_male[["player_id","ob"]].groupby("player_id").mean()["ob"].mean(), 1)
            male_bunker_avgs = round(df_male[["player_id","bunker"]].groupby("player_id").mean()["bunker"].mean(), 1)
            male_penalty_avgs = round(df_male[["player_id","penalty"]].groupby("player_id").mean()["penalty"].mean(), 1)

            #男それぞれの平均
            allmale_score_avg = df_male[["player_id","total_score","ob","penalty","fw","par_on","putt", "bunker"]].groupby("player_id").mean()
            male_60 = allmale_score_avg[allmale_score_avg["total_score"] < 70]
            male_70 = allmale_score_avg[(allmale_score_avg["total_score"] >= 70) & (allmale_score_avg["total_score"] < 80)]
            male_80 = allmale_score_avg[(allmale_score_avg["total_score"] >= 80) & (allmale_score_avg["total_score"] < 90)]
            male_90 = allmale_score_avg[(allmale_score_avg["total_score"] >= 90) & (allmale_score_avg["total_score"] <  100)]
            male_100 = allmale_score_avg[(allmale_score_avg["total_score"] >= 100) & (allmale_score_avg["total_score"] < 110)]
            male_110 = allmale_score_avg[(allmale_score_avg["total_score"] >= 110) & (allmale_score_avg["total_score"] < 120)]
            male_120 = allmale_score_avg[allmale_score_avg["total_score"] >= 120]

            #男性60平均
            male_score_60 = round(male_60.mean()["total_score"], 1)
            male_putt_60 = round(male_60.mean()["putt"], 1)
            male_fw_60 = round(male_60.mean()["fw"], 1)
            male_par_on_60 = round(male_60.mean()["par_on"], 1)
            male_ob_60 = round(male_60.mean()["ob"], 1)
            male_bunker_60 = round(male_60.mean()["bunker"], 1)
            male_penalty_60 = round(male_60.mean()["penalty"], 1)

            #男性70平均
            male_score_70 = round(male_70.mean()["total_score"], 1)
            male_putt_70 = round(male_70.mean()["putt"], 1)
            male_fw_70 = round(male_70.mean()["fw"], 1)
            male_par_on_70 = round(male_70.mean()["par_on"], 1)
            male_ob_70 = round(male_70.mean()["ob"], 1)
            male_bunker_70 = round(male_70.mean()["bunker"], 1)
            male_penalty_70 = round(male_70.mean()["penalty"], 1)

            #男性80平均
            male_score_80 = round(male_80.mean()["total_score"], 1)
            male_putt_80 = round(male_80.mean()["putt"], 1)
            male_fw_80 = round(male_80.mean()["fw"], 1)
            male_par_on_80 = round(male_80.mean()["par_on"], 1)
            male_ob_80 = round(male_80.mean()["ob"], 1)
            male_bunker_80 = round(male_80.mean()["bunker"], 1)
            male_penalty_80 = round(male_80.mean()["penalty"], 1)
            
            #男性90平均
            male_score_90 = round(male_90.mean()["total_score"], 1)
            male_putt_90 = round(male_90.mean()["putt"], 1)
            male_fw_90 = round(male_90.mean()["fw"], 1)
            male_par_on_90 = round(male_90.mean()["par_on"], 1)
            male_ob_90 = round(male_90.mean()["ob"], 1)
            male_bunker_90 = round(male_90.mean()["bunker"], 1)
            male_penalty_90 = round(male_90.mean()["penalty"], 1)

            #男性100平均
            male_score_100 = round(male_100.mean()["total_score"], 1)
            male_putt_100 = round(male_100.mean()["putt"], 1)
            male_fw_100 = round(male_100.mean()["fw"], 1)
            male_par_on_100 = round(male_100.mean()["par_on"], 1)
            male_ob_100 = round(male_100.mean()["ob"], 1)
            male_bunker_100 = round(male_100.mean()["bunker"], 1)
            male_penalty_100 = round(male_100.mean()["penalty"], 1)

            #男性110平均
            male_score_110 = round(male_110.mean()["total_score"], 1)
            male_putt_110 = round(male_110.mean()["putt"], 1)
            male_fw_110 = round(male_110.mean()["fw"], 1)
            male_par_on_110 = round(male_110.mean()["par_on"], 1)
            male_ob_110 = round(male_110.mean()["ob"], 1)
            male_bunker_110 = round(male_110.mean()["bunker"], 1)
            male_penalty_110 = round(male_110.mean()["penalty"], 1)

            #男性120平均
            male_score_120 = round(male_120.mean()["total_score"], 1)
            male_putt_120 = round(male_120.mean()["putt"], 1)
            male_fw_120 = round(male_120.mean()["fw"], 1)
            male_par_on_120 = round(male_120.mean()["par_on"], 1)
            male_ob_120 = round(male_120.mean()["ob"], 1)
            male_bunker_120 = round(male_120.mean()["bunker"], 1)
            male_penalty_120 = round(male_120.mean()["penalty"], 1)


            #男性平均cxt
            if f'{male_score_avgs}' != "nan":
                context["male_score_avgs"] = f'{male_score_avgs}'
                context["male_putt_avgs"] = f'{male_putt_avgs}'
                context["male_fw_avgs"] = f'{male_fw_avgs}'+"%"
                context["male_par_on_avgs"] = f'{male_par_on_avgs}'+"%"
                context["male_ob_avgs"] = f'{male_ob_avgs}'+"回"
                context["male_bunker_avgs"] = f'{male_bunker_avgs}'
                context["male_penalty_avgs"] = f'{male_penalty_avgs}'+"回"
            
            #男性60平均cxtf'{}'+""
            if f'{male_score_60}' != "nan":
                context["male_score_60"] = male_score_60
                context["male_putt_60"] = f'{male_putt_60}'
                context["male_fw_60"] = f'{male_fw_60}'+"%"
                context["male_par_on_60"] = f'{male_par_on_60}'+"%"
                context["male_ob_60"] = f'{male_ob_60}'+"回"
                context["male_bunker_60"] = f'{male_bunker_60}'
                context["male_penalty_60"] = f'{male_penalty_60}'+"回"

            #男性70平均cxt
            if f'{male_score_70}' != "nan":
                context["male_score_70"] = male_score_70
                context["male_putt_70"] = f'{male_putt_70}'
                context["male_fw_70"] = f'{male_fw_70}'+"%"
                context["male_par_on_70"] = f'{male_par_on_70}'+"%"
                context["male_ob_70"] = f'{male_ob_70}'+"回"
                context["male_bunker_70"] = f'{male_bunker_70}'
                context["male_penalty_70"] = f'{male_penalty_70}'+"回"

            #男性80平均cxt
            if f'{male_score_80}' != "nan":
                context["male_score_80"] = male_score_80
                context["male_putt_80"] = f'{male_putt_80}'
                context["male_fw_80"] = f'{male_fw_80}'+"%"
                context["male_par_on_80"] = f'{male_par_on_80}'+"%"
                context["male_ob_80"] = f'{male_ob_80}'+"回"
                context["male_bunker_80"] = f'{male_bunker_80}'
                context["male_penalty_80"] = f'{male_penalty_80}'+"回"

            #男性90平均cxt
            if f'{male_score_90}' != "nan":
                context["male_score_90"] = male_score_90
                context["male_putt_90"] = f'{male_putt_90}'
                context["male_fw_90"] = f'{male_fw_90}'+"%"
                context["male_par_on_90"] = f'{male_par_on_90}'+"%"
                context["male_ob_90"] = f'{male_ob_90}'+"回"
                context["male_bunker_90"] = f'{male_bunker_90}'
                context["male_penalty_90"] = f'{male_penalty_90}'+"回"
                
            #男性100平均cxt
            if f'{male_score_100}' != "nan":
                context["male_score_100"] = male_score_100
                context["male_putt_100"] = f'{male_putt_100}'
                context["male_fw_100"] = f'{male_fw_100}'+"%"
                context["male_par_on_100"] = f'{male_par_on_100}'+"%"
                context["male_ob_100"] = f'{male_ob_100}'+"回"
                context["male_bunker_100"] = f'{male_bunker_100}'
                context["male_penalty_100"] = f'{male_penalty_100}'+"回"

            #男性110平均cxt
            if f'{male_score_110}' != "nan":
                context["male_score_110"] = male_score_110
                context["male_putt_110"] = f'{male_putt_110}'
                context["male_fw_110"] = f'{male_fw_110}'+"%"
                context["male_par_on_110"] = f'{male_par_on_110}'+"%"
                context["male_ob_110"] = f'{male_ob_110}'+"回"
                context["male_bunker_110"] = f'{male_bunker_110}'
                context["male_penalty_110"] = f'{male_penalty_110}'+"回"

            #男性120平均cxt
            if f'{male_score_120}' != "nan":
                context["male_score_120"] = male_score_120
                context["male_putt_120"] = f'{male_putt_120}'
                context["male_fw_120"] = f'{male_fw_120}'+"%"
                context["male_par_on_120"] = f'{male_par_on_120}'+"%"
                context["male_ob_120"] = f'{male_ob_120}'+"回"
                context["male_bunker_120"] = f'{male_bunker_120}'
                context["male_penalty_120"] = f'{male_penalty_120}'+"回"
                
        #女性↓

        if Stat.objects.filter(player__sex="女性").values().exists() == True:

            #女性平均
            female_score_avgs = round(df_female[["player_id","total_score"]].groupby("player_id").mean()["total_score"].mean(), 1)
            female_putt_avgs = round(df_female[["player_id","putt"]].groupby("player_id").mean()["putt"].mean(), 1)
            female_fw_avgs = round(df_female[["player_id","fw"]].groupby("player_id").mean()["fw"].mean(), 1)
            female_par_on_avgs = round(df_female[["player_id","par_on"]].groupby("player_id").mean()["par_on"].mean(), 1)
            female_ob_avgs = round(df_female[["player_id","ob"]].groupby("player_id").mean()["ob"].mean(), 1)
            female_bunker_avgs = round(df_female[["player_id","bunker"]].groupby("player_id").mean()["bunker"].mean(), 1)
            female_penalty_avgs = round(df_female[["player_id","penalty"]].groupby("player_id").mean()["penalty"].mean(), 1)

            #女性それぞれの平均
            allfemale_score_avg = df_female[["player_id","total_score","ob","penalty","fw","par_on","putt", "bunker"]].groupby("player_id").mean()
            female_60 = allfemale_score_avg[allfemale_score_avg["total_score"] < 70]
            female_70 = allfemale_score_avg[(allfemale_score_avg["total_score"] >= 70) & (allfemale_score_avg["total_score"] < 80)]
            female_80 = allfemale_score_avg[(allfemale_score_avg["total_score"] >= 80) & (allfemale_score_avg["total_score"] < 90)]
            female_90 = allfemale_score_avg[(allfemale_score_avg["total_score"] >= 90) & (allfemale_score_avg["total_score"] <  100)]
            female_100 = allfemale_score_avg[(allfemale_score_avg["total_score"] >= 100) & (allfemale_score_avg["total_score"] < 110)]
            female_110 = allfemale_score_avg[(allfemale_score_avg["total_score"] >= 110) & (allfemale_score_avg["total_score"] < 120)]
            female_120 = allfemale_score_avg[allfemale_score_avg["total_score"] >= 120]

            #女性60平均
            female_score_60 = round(female_60.mean()["total_score"], 1)
            female_putt_60 = round(female_60.mean()["putt"], 1)
            female_fw_60 = round(female_60.mean()["fw"], 1)
            female_par_on_60 = round(female_60.mean()["par_on"], 1)
            female_ob_60 = round(female_60.mean()["ob"], 1)
            female_bunker_60 = round(female_60.mean()["bunker"], 1)
            female_penalty_60 = round(female_60.mean()["penalty"], 1)

            #女性70平均
            female_score_70 = round(female_70.mean()["total_score"], 1)
            female_putt_70 = round(female_70.mean()["putt"], 1)
            female_fw_70 = round(female_70.mean()["fw"], 1)
            female_par_on_70 = round(female_70.mean()["par_on"], 1)
            female_ob_70 = round(female_70.mean()["ob"], 1)
            female_bunker_70 = round(female_70.mean()["bunker"], 1)
            female_penalty_70 = round(female_70.mean()["penalty"], 1)

            #女性80平均
            female_score_80 = round(female_80.mean()["total_score"], 1)
            female_putt_80 = round(female_80.mean()["putt"], 1)
            female_fw_80 = round(female_80.mean()["fw"], 1)
            female_par_on_80 = round(female_80.mean()["par_on"], 1)
            female_ob_80 = round(female_80.mean()["ob"], 1)
            female_bunker_80 = round(female_80.mean()["bunker"], 1)
            female_penalty_80 = round(female_80.mean()["penalty"], 1)
            
            #女性90平均
            female_score_90 = round(female_90.mean()["total_score"], 1)
            female_putt_90 = round(female_90.mean()["putt"], 1)
            female_fw_90 = round(female_90.mean()["fw"], 1)
            female_par_on_90 = round(female_90.mean()["par_on"], 1)
            female_ob_90 = round(female_90.mean()["ob"], 1)
            female_bunker_90 = round(female_90.mean()["bunker"], 1)
            female_penalty_90 = round(female_90.mean()["penalty"], 1)

            #女性100平均
            female_score_100 = round(female_100.mean()["total_score"], 1)
            female_putt_100 = round(female_100.mean()["putt"], 1)
            female_fw_100 = round(female_100.mean()["fw"], 1)
            female_par_on_100 = round(female_100.mean()["par_on"], 1)
            female_ob_100 = round(female_100.mean()["ob"], 1)
            female_bunker_100 = round(female_100.mean()["bunker"], 1)
            female_penalty_100 = round(female_100.mean()["penalty"], 1)

            #女性110平均
            female_score_110 = round(female_110.mean()["total_score"], 1)
            female_putt_110 = round(female_110.mean()["putt"], 1)
            female_fw_110 = round(female_110.mean()["fw"], 1)
            female_par_on_110 = round(female_110.mean()["par_on"], 1)
            female_ob_110 = round(female_110.mean()["ob"], 1)
            female_bunker_110 = round(female_110.mean()["bunker"], 1)
            female_penalty_110 = round(female_110.mean()["penalty"], 1)

            #女性120平均
            female_score_120 = round(female_120.mean()["total_score"], 1)
            female_putt_120 = round(female_120.mean()["putt"], 1)
            female_fw_120 = round(female_120.mean()["fw"], 1)
            female_par_on_120 = round(female_120.mean()["par_on"], 1)
            female_ob_120 = round(female_120.mean()["ob"], 1)
            female_bunker_120 = round(female_120.mean()["bunker"], 1)
            female_penalty_120 = round(female_120.mean()["penalty"], 1)


            #女性平均cxt
            if f'{female_score_avgs}' != "nan":
                context["female_score_avgs"] = f'{female_score_avgs}'
                context["female_putt_avgs"] = f'{female_putt_avgs}'
                context["female_fw_avgs"] = f'{female_fw_avgs}'+"%"
                context["female_par_on_avgs"] = f'{female_par_on_avgs}'+"%"
                context["female_ob_avgs"] = f'{female_ob_avgs}'+"回"
                context["female_bunker_avgs"] = f'{female_bunker_avgs}'
                context["female_penalty_avgs"] = f'{female_penalty_avgs}'+"回"
            
            #女性60平均cxtf'{}'+""
            if f'{female_score_60}' != "nan":
                context["female_score_60"] = female_score_60
                context["female_putt_60"] = f'{female_putt_60}'
                context["female_fw_60"] = f'{female_fw_60}'+"%"
                context["female_par_on_60"] = f'{female_par_on_60}'+"%"
                context["female_ob_60"] = f'{female_ob_60}'+"回"
                context["female_bunker_60"] = f'{female_bunker_60}'
                context["female_penalty_60"] = f'{female_penalty_60}'+"回"

            #女性70平均cxt
            if f'{female_score_70}' != "nan":
                context["female_score_70"] = female_score_70
                context["female_putt_70"] = f'{female_putt_70}'
                context["female_fw_70"] = f'{female_fw_70}'+"%"
                context["female_par_on_70"] = f'{female_par_on_70}'+"%"
                context["female_ob_70"] = f'{female_ob_70}'+"回"
                context["female_bunker_70"] = f'{female_bunker_70}'
                context["female_penalty_70"] = f'{female_penalty_70}'+"回"

            #女性80平均cxt
            if f'{female_score_80}' != "nan":
                context["female_score_80"] = female_score_80
                context["female_putt_80"] = f'{female_putt_80}'
                context["female_fw_80"] = f'{female_fw_80}'+"%"
                context["female_par_on_80"] = f'{female_par_on_80}'+"%"
                context["female_ob_80"] = f'{female_ob_80}'+"回"
                context["female_bunker_80"] = f'{female_bunker_80}'
                context["female_penalty_80"] = f'{female_penalty_80}'+"回"

            #女性90平均cxt
            if f'{female_score_90}' != "nan":
                context["female_score_90"] = female_score_90
                context["female_putt_90"] = f'{female_putt_90}'
                context["female_fw_90"] = f'{female_fw_90}'+"%"
                context["female_par_on_90"] = f'{female_par_on_90}'+"%"
                context["female_ob_90"] = f'{female_ob_90}'+"回"
                context["female_bunker_90"] = f'{female_bunker_90}'
                context["female_penalty_90"] = f'{female_penalty_90}'+"回"
                
            #女性100平均cxt
            if f'{female_score_100}' != "nan":
                context["female_score_100"] = female_score_100
                context["female_putt_100"] = f'{female_putt_100}'
                context["female_fw_100"] = f'{female_fw_100}'+"%"
                context["female_par_on_100"] = f'{female_par_on_100}'+"%"
                context["female_ob_100"] = f'{female_ob_100}'+"回"
                context["female_bunker_100"] = f'{female_bunker_100}'
                context["female_penalty_100"] = f'{female_penalty_100}'+"回"

            #女性110平均cxt
            if f'{female_score_110}' != "nan":
                context["female_score_110"] = female_score_110
                context["female_putt_110"] = f'{female_putt_110}'
                context["female_fw_110"] = f'{female_fw_110}'+"%"
                context["female_par_on_110"] = f'{female_par_on_110}'+"%"
                context["female_ob_110"] = f'{female_ob_110}'+"回"
                context["female_bunker_110"] = f'{female_bunker_110}'
                context["female_penalty_110"] = f'{female_penalty_110}'+"回"

            #女性120平均cxt
            if f'{female_score_120}' != "nan":
                context["female_score_120"] = female_score_120
                context["female_putt_120"] = f'{female_putt_120}'
                context["female_fw_120"] = f'{female_fw_120}'+"%"
                context["female_par_on_120"] = f'{female_par_on_120}'+"%"
                context["female_ob_120"] = f'{female_ob_120}'+"回"
                context["female_bunker_120"] = f'{female_bunker_120}'
                context["female_penalty_120"] = f'{female_penalty_120}'+"回"



        return context

class CsvImport(generic.FormView):
    template_name = 'score/csv_import.html'
    success_url = reverse_lazy('score:person_list')
    form_class = CSVUploadForm

    def form_valid(self, form):
        # csv.readerに渡すため、TextIOWrapperでテキストモードなファイルに変換
        form_data = io.TextIOWrapper(form.cleaned_data['file'], encoding='utf-8')
        csv_file = csv.reader(form_data)
        # 1行ずつ取り出し、作成していく
        if form_data.name.endswith('.csv'):
        
            for line in csv_file:
                try:
                    if f'[{self.request.user.id}]' != list(Person.objects.values_list('login_user', flat=True).filter(player_number=int(f'{self.request.user.id}'+"000000"+f'{line[1]}'))):
                        person, created = Person.objects.get_or_create(player_number=int(f'{self.request.user.id}'+"000000"+f'{line[1]}'))
                        person.login_user = self.request.user.id
                        person.name =line[0]
                        person.age = line[2]
                        person.sex = line[3]
                        person.save()

                    stat_number_check =list(Stat.objects.values("stat_number").all())
                    stat_number_check = f'{stat_number_check}'
                    stat_number_check = stat_number_check.replace("}", "")
                    s_check = int(f'{self.request.user.id}'+"000000"+f'{line[12]}')
                    if f': {s_check},' not in f'{stat_number_check}' and f': {s_check}]' not in f'{stat_number_check}':
                    
                        Stat.objects.create(
                            player = Person.objects.get(player_number=int(f'{self.request.user.id}'+"000000"f'{line[1]}')),
                            stat_number = int(f'{self.request.user.id}'+"000000"+f'{line[12]}'),
                            date = line[4],
                            total_score = line[5],
                            putt = line[6],
                            fw = line[7],
                            par_on = line[8],
                            ob = line[9],
                            bunker = line[10],
                            penalty = line[11]
                        )

                except:
                    messages.add_message(self.request, messages.ERROR, "内容が正しいか等確認してください")
                    return redirect('score:csv_import')
        
            return super().form_valid(form)
            
        else:
            messages.add_message(self.request, messages.ERROR, "csvファイルを選択してください")
            return redirect('score:csv_import')

def csv_export(request):
    response = HttpResponse(content_type='text/csv; charset=Shift-JIS')
    filename = urllib.parse.quote((u'仮ファイル.csv').encode("utf8"))
    response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'{}'.format(filename)
    writer = csv.writer(response)
    header = ["名前", "影響度", "パット",'FWキープ','パーオン','OB',"バンカー",'ペナルティ', "stats平均","スコア","パット数","FWキープ率","パーオン率","OB数","バンカー数","ペナルティ数"]
    writer.writerow(header)

    pks = list(Person.objects.values_list('id', flat=True).all().order_by("sex"))
    for pk in pks:

        if Stat.objects.filter(player=pk).all().exists() == True:

            df = pd.DataFrame(Stat.objects.filter(player_id=pk).values())
            df.columns = ["id", "player_id", "date", "パット",'FWキープ','パーオン','OB',"バンカー",'ペナルティ',"stat_number"]

            if len(df) > 7:
                #全stat
                z = df.drop(['id','player_id','date','stat_number'], axis=1)

                score_count = len(z)-1
                putt_true_count = f'{z.duplicated("パット")}'.count("True")
                if putt_true_count == score_count:
                    z.iat[1,1] = 101

                fw_true_count = f'{z.duplicated("FWキープ")}'.count("True")
                if fw_true_count == score_count:
                    z.iat[1,2] = 101

                par_true_count = f'{z.duplicated("パーオン")}'.count("True")
                if par_true_count == score_count:
                    z.iat[1,3] = 101
                
                ob_true_count = f'{z.duplicated("OB")}'.count("True")
                if ob_true_count == score_count:
                    z.iat[1,4] = 101

                bunker_true_count = f'{z.duplicated("バンカー")}'.count("True")
                if bunker_true_count == score_count:
                    z.iat[1,5] = 101

                penalty_true_count = f'{z.duplicated("ペナルティ")}'.count("True")
                if penalty_true_count == score_count:
                    z.iat[1,6] = 101            

                #statを標準化
                df_std = z.apply(lambda x: (x-x.mean())/x.std(), axis=0)
                #statのスコア以外
                x = df_std.drop(['スコア'], axis=1)
                #スコア
                y = df_std['スコア']

                reg = LinearRegression()
                results = reg.fit(x,y)
                coef = reg.coef_.round(4)
                n = x.shape[0]
                p = x.shape[1]

                y_hat = reg.predict(x)
                sse = np.sum((y - y_hat) **2, axis=0)
                sse = sse / (n - p - 1)
                s = np.linalg.inv(np.dot(x.T, x))
                std_err = np.sqrt(np.diagonal(sse * s)).round(4)

                t_values = (coef / std_err).round(4)
                t_values_abs = np.abs(t_values)
                t_add = t_values_abs[0] + t_values_abs[1] + t_values_abs[2] + t_values_abs[3] + t_values_abs[4] + t_values_abs[5]
                x = 100 / t_add
                t_values_abs = (x * t_values_abs).round(1)
                
                col = ["パット",'FWキープ','パーオン','OB',"バンカー",'ペナルティ',]
                practice = dict(zip(col, t_values_abs))
            
            else:
                df_score = df.sort_values("スコア")
                data_count = df["スコア"].count()
                
                df_patt = df.sort_values(by=["パット","スコア"])
                patt_count = [abs(df_patt.index.get_loc(i) - df_score.index.get_loc(i)) for i in range(data_count)]
                patt_score = sum(patt_count)
                
                df_fk = df.sort_values(by=["FWキープ","スコア"], ascending=[False,True])
                fk_count = [abs(df_fk.index.get_loc(i) - df_score.index.get_loc(i)) for i in range(data_count)]
                fk_score = sum(fk_count)
                
                df_po = df.sort_values(by=["パーオン","スコア"], ascending=[False,True])
                po_count = [abs(df_po.index.get_loc(i) - df_score.index.get_loc(i)) for i in range(data_count)]
                po_score = sum(po_count)
                
                df_OB = df.sort_values(by=["OB","スコア"])
                OB_count = [abs(df_OB.index.get_loc(i) - df_score.index.get_loc(i)) for i in range(data_count)]
                OB_score = sum(OB_count)

                df_バンカー = df.sort_values(by=["バンカー","スコア"])
                バンカー_count = [abs(df_バンカー.index.get_loc(i) - df_score.index.get_loc(i)) for i in range(data_count)]
                バンカー_score = sum(バンカー_count)
                
                df_pn = df.sort_values(by=["ペナルティ","スコア"])
                pn_count = [abs(df_pn.index.get_loc(i) - df_score.index.get_loc(i)) for i in range(data_count)]
                pn_score = sum(pn_count)               
                
                calc_add = 1/(OB_score+1) + 1/(pn_score+1) + 1/(fk_score+1) + 1/(po_score+1) + 1/(patt_score+1) + 1/(バンカー_score+1)
                cf = 100 / calc_add

                practice = {"パット": round(cf / (patt_score+1),1),
                            "FWキープ": round(cf / (fk_score+1), 1),
                            "パーオン": round(cf / (po_score+1), 1),
                            "OB": round(cf / (OB_score+1), 1),
                            "バンカー": round(cf / (バンカー_score+1),1),
                            "ペナルティ": round(cf / (pn_score+1), 1)}
                            
            score_avg = Stat.objects.filter(player=pk).aggregate(Avg("total_score"))
            putt_avg = Stat.objects.filter(player=pk).aggregate(Avg("putt"))  
            fw_avg = Stat.objects.filter(player=pk).aggregate(Avg("fw"))      
            par_on_avg = Stat.objects.filter(player=pk).aggregate(Avg("par_on"))    
            ob_avg = Stat.objects.filter(player=pk).aggregate(Avg("ob"))
            bunker_avg = Stat.objects.filter(player=pk).aggregate(Avg("bunker"))
            penalty_avg = Stat.objects.filter(player=pk).aggregate(Avg("penalty"))

            blank = ""
            player_name = list(Person.objects.values_list("name", flat=True).filter(id=pk))
            player_name = f'{player_name}'.replace("['", "").replace("']", "")
            writer.writerow([player_name,blank,practice["パット"],practice["FWキープ"],practice["パーオン"],practice["OB"],practice["バンカー"],practice["ペナルティ"],blank,
                             round(score_avg["total_score__avg"],1),
                             round(putt_avg["putt__avg"],1),
                             round(fw_avg["fw__avg"],1),
                             round(par_on_avg["par_on__avg"],1),
                             round(ob_avg["ob__avg"],1),
                             round(bunker_avg["bunker__avg"],1)],  
                             round(penalty_avg["penalty__avg"],1))
                             
    return response
