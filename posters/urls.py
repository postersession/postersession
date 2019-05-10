
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('poster/<int:poster_id>/', views.detail, name='detail'),
]
