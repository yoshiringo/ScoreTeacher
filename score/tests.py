from django.test import TestCase, Client
from django.conf import settings
from .models import Person, Stat
from django.contrib.auth.models import User
from django.urls import reverse
from django.urls import reverse_lazy
from .models import Person
from .forms import PersonCreateForm
from django.test import TestCase
from django.utils import timezone
from unittest.mock import patch
from .views import StatAnalyze
import pytest
from django.test import RequestFactory
from mixer.backend.django import mixer
from . import views


class PersonModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # テスト用のPersonインスタンスを作成
        Person.objects.create(name='Test Person', login_user=1, sex='男性', age=30, player_number=1)

    def test_name_label(self):
        # フィールドのverbose_name属性が設定されているかを確認するテスト
        person = Person.objects.get(id=1)
        field_label = person._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')

    def test_login_user_null(self):
        # null=Trueのフィールドに対するnull値許容のテスト
        person = Person.objects.get(id=1)
        field_null = person._meta.get_field('login_user').null
        self.assertTrue(field_null)

    def test_sex_choices(self):
        # 選択肢が設定されているChoiceFieldに対するテスト
        person = Person.objects.get(id=1)
        field_choices = dict(person._meta.get_field('sex').choices)
        self.assertEqual(field_choices, {'男性': '男性', '女性': '女性'})

    def test_age_blank(self):
        # blank=Trueのフィールドに対する空白許容のテスト
        person = Person.objects.get(id=1)
        field_blank = person._meta.get_field('age').blank
        self.assertTrue(field_blank)

    def test_player_number_unique(self):
        # unique=Trueのフィールドに対する一意性のテスト
        person1 = Person.objects.create(name='Test Person2', login_user=1, sex='M', age=25, player_number=2)
        person2 = Person.objects.create(name='Test Person3', login_user=1, sex='F', age=35, player_number=2)
        with self.assertRaises(Exception):
            # player_numberがuniqueのため、同じ値を持つレコードを追加しようとするとエラーが発生することを確認する
            person2.full_clean()

class StatModelTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create(
            name="test_person",
            login_user=1,
            sex="男性",
            age=20,
            player_number=1
        )

    def test_stat_model_fields(self):
        stat = Stat.objects.create(
            player=self.person,
            date="2022-04-01",
            total_score=72,
            putt=28,
            fw=60,
            par_on=15,
            ob=1,
            bunker=2,
            penalty=5
        )

        self.assertEqual(stat.player, self.person)
        self.assertEqual(stat.date, "2022-04-01")
        self.assertEqual(stat.total_score, 72)
        self.assertEqual(stat.putt, 28)
        self.assertEqual(stat.fw, 60)
        self.assertEqual(stat.par_on, 15)
        self.assertEqual(stat.ob, 1)
        self.assertEqual(stat.bunker, 2)
        self.assertEqual(stat.penalty, 5)

class PersonListViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        #テスト用ユーザーの作成
        test_user = User.objects.create_user(username='testuser', password='testpass')
        test_user.save()
        
        #テスト用Personの作成
        Person.objects.create(name="testperson1", login_user=test_user.id, sex="男性", age=20, player_number=1)
        Person.objects.create(name="testperson2", login_user=test_user.id, sex="女性", age=30, player_number=2)

    def test_person_list_view_url_exists_at_desired_location(self):
        #person_listのURLが存在するかどうかをテストする
        response = self.client.get(reverse('score:person_list'))
        self.assertEqual(response.status_code, 200)

    def test_person_list_view_url_accessible_by_name(self):
        #person_listのURLが名前でアクセス可能かどうかをテストする
        response = self.client.get(reverse('score:person_list'))
        self.assertEqual(response.status_code, 200)

    def test_person_list_view_uses_correct_template(self):
        #person_listのビューが正しいテンプレートを使用しているかをテストする
        response = self.client.get(reverse('score:person_list'))
        self.assertTemplateUsed(response, 'score/index.html')

    def test_person_list_view_displays_persons(self):
        #person_listのビューがPersonオブジェクトを表示しているかをテストする
        login_user = User.objects.get(username='testuser')
        self.client.force_login(login_user)
        response = self.client.get(reverse('score:person_list'))
        self.assertContains(response, "testperson1")
        self.assertContains(response, "testperson2")
        
    def test_person_list_view_displays_player_add_message(self):
        #プレイヤー未登録の場合のメッセージが表示されるかをテストする
        response = self.client.get(reverse('score:person_list'))
        self.assertContains(response, "プレイヤーを追加してください")




class PersonCreateTest(TestCase):
    def setUp(self):
        self.url = reverse_lazy('score:person_create')
        self.valid_data = {
        'name': 'John',
        'sex': '男性',
        'age': 30
        }
        self.invalid_data = {
        'name': '',
        'sex': '男性',
        'age': ''
        }
    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], PersonCreateForm)

    def test_post_valid_data(self):
        response = self.client.post(self.url, data=self.valid_data)
        self.assertRedirects(response, reverse_lazy('score:person_list'))
        self.assertEqual(Person.objects.count(), 1)
        self.assertEqual(Person.objects.first().name, self.valid_data['name'])
        
    def test_post_invalid_data(self):
        response = self.client.post(self.url, data=self.invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'name', 'このフィールドは必須です。')
        self.assertEqual(Person.objects.count(), 0)
    
    class StatCreateViewTest(TestCase):
        def setUp(self):
            self.person = Person.objects.create(name="test_person", login_user=1, sex="男性", age=20, player_number=1)
            self.url = reverse("score:detail", kwargs={"pk": self.person.pk})

        def test_get(self):
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "score/detail.html")
            self.assertContains(response, self.person.name)

        def test_post(self):
            data = {
                "date": "2022-01-01",
                "total_score": 100,
                "putt": 30,
                "fw": 60,
                "par_on": 50,
                "ob": 2,
                "bunker": 3,
                "penalty": 0,
            }
            response = self.client.post(self.url, data)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(Stat.objects.count(), 1)
            stat = Stat.objects.first()
            self.assertEqual(stat.player, self.person)
            self.assertEqual(stat.date.strftime("%Y-%m-%d"), "2022-01-01")
            self.assertEqual(stat.total_score, 100)
            self.assertEqual(stat.putt, 30)
            self.assertEqual(stat.fw, 60)
            self.assertEqual(stat.par_on, 50)
            self.assertEqual(stat.ob, 2)
            self.assertEqual(stat.bunker, 3)
            self.assertEqual(stat.penalty, 0)

pytestmark = pytest.mark.django_db

class TestStatAnalyzeView:
    def test_stat_analyze_view(self):
        path = reverse('stat_analyze', kwargs={'pk': 1})
        request = RequestFactory().get(path)
        view = views.StatAnalyze.as_view()
        response = view(request, pk=1)
        assert response.status_code == 200

    def test_stat_analyze_context(self):
        person = mixer.blend('score.Person')
        stat = mixer.blend('score.Stat', player=person)
        path = reverse('stat_analyze', kwargs={'pk': person.pk})
        request = RequestFactory().get(path)
        response = views.StatAnalyze.as_view()(request, pk=person.pk)
        assert response.status_code == 200
        assert 'person_stat' in response.context_data
        assert response.context_data['person_stat'].name == person.name
        assert 'breadcrumbs_list' in response.context_data
        assert response.context_data['breadcrumbs_list'][0]['name'] == 'Stats'
        assert response.context_data['breadcrumbs_list'][1]['name'] == '分析結果'

    def test_stat_analyze_regression(self):
        person = mixer.blend('score.Person')
        mixer.cycle(5).blend('score.Stat', player=person, total_score=90, putt=30, fw=60, par_on=80, ob=5, bunker=3, penalty=5)
        mixer.cycle(5).blend('score.Stat', player=person, total_score=80, putt=28, fw=50, par_on=70, ob=4, bunker=2, penalty=4)
        path = reverse('stat_analyze', kwargs={'pk': person.pk})
        request = RequestFactory().get(path)
        response = views.StatAnalyze.as_view()(request, pk=person.pk)
        assert response.status_code == 200
        assert 'person_stat' in response.context_data
        assert response.context_data['person_stat'].name == person.name
        assert 'regression' in response.context_data
        assert response.context_data['regression'] == [-0.1772, 0.2281, -0.1939, -0.2158, -0.2013, 79.7151] 