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

# Create your views here.

class PersonList(generic.ListView):
    model = Person
    template_name = "score/index.html"
    paginate_by = 3

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        login_user_name = self.request.user.username
        personlist = Person.objects.filter(login_user=login_user_name)
        person_user = Person.objects.values_list('login_user', flat=True).filter(login_user=login_user_name)
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

        return context

    def form_valid(self, form):
        post = form.save(commit=False)
        post.login_user = self.request.user.username
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
