from django.urls import path
from . import views

app_name = "assessment"

urlpatterns = [
    path('step1/', views.upload_video, name="upload_video"),
    path('step2/', views.questionnaire_video, name="questionnaire_video"),

    path('questionnaire/', views.questionnaire, name="questionnaire"),

    path('processing/', views.processing_view, name="processing"),
]