
from os import name
from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.contrib.staticfiles.urls import static
from django.conf.urls import handler404, handler500


app_name = "image_quality"

urlpatterns = [
    path ('', views.home, name='home'),
    path('personal_info', views.personal_info, name='personal_info'),
    path('ghs_fk', views.ghs_fk, name='ghs_fk'),
    path('profileBuilder', views.profileBuilder, name='profileBuilder'),
    path('rate_recipes',views.rate_recipes, name='rate_recipes'),
    path('choice_evaluation',views.choice_evaluation, name='choice_evaluation'),
    path('thank_u', views.thank_u,name='thank_u'),

]