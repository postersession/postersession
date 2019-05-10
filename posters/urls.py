
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:poster_id>/', views.detail, name='detail'),
]
