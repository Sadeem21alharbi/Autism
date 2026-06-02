

from django.urls import path
from . import views

app_name = 'activity'

urlpatterns = [
    path('list/', views.activity_list, name='activity_list'),
    path('play/<int:activity_id>/', views.activity_play, name='activity_play'),
]