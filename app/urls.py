from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.TopicView.as_view()),
    path('detail/<int:pk>/', views.QuestionView.as_view()),
    path('favorite/', views.FavoriteView.as_view()),
    path('play-sound/', views.PlaySoundView.as_view()),
]
