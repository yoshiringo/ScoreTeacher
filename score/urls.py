from django.urls import path
from . import views

app_name = "score"

urlpatterns = [
    path("", views.PersonList.as_view(), name="person_list"),
    path("detail/<int:pk>/", views.StatCreate.as_view(), name="detail"),
    path("person_create/", views.PersonCreate.as_view(), name="person_create"),
    path("stat_delete/<int:pk>/", views.StatDelete.as_view(), name="stat_delete"),
    path("person_delete/<int:pk>/", views.PersonDelete.as_view(), name="person_delete"),
    path("stat_analyze/<int:pk>/", views.StatAnalyze.as_view(), name="stat_analyze"),
    path("average/", views.Average.as_view(), name="average"),
    path('csv_import/', views.CsvImport.as_view(), name='csv_import'),
    path('export/', views.csv_export, name='csv_export'),
    path('csv_format/', views.csv_format, name='csv_format'),
]