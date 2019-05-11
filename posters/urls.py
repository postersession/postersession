
from django.views.generic import TemplateView
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='home'),
    #path('poster/<int:poster_id>/', views.detail, name='detail'),
    path('upload/<str:access_key>/', views.upload, name='upload'),
    path('about/', TemplateView.as_view(template_name="pages/about.html"), name="about"),
    path('success/', TemplateView.as_view(template_name="pages/success.html"), name="success"),
]
