
from django.views.generic import TemplateView
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('upload/<str:access_key>/', views.upload, name='upload'),
    path('poster/<str:slug>/', views.detail, name='detail'),
    path('search', views.search, name='search'),
    path('about/', TemplateView.as_view(template_name="pages/about.html"), name="about"),
    path('contact/', TemplateView.as_view(template_name="pages/contact.html"), name="contact"),
    path('disclaimer/', TemplateView.as_view(template_name="pages/disclaimer.html"), name="disclaimer"),
    path('success/', TemplateView.as_view(template_name="pages/success.html"), name="success"),
    path('success-delayed/', TemplateView.as_view(template_name="pages/success-delayed.html"), name="success-delayed"),
    path('sitemap.xml', views.sitemap, name='sitemap'),
    path('robots.txt/', TemplateView.as_view(template_name='robots.txt', content_type='text/plain'), name='robots'),
    path('<str:conference_id>/', views.index, name='conference'),
]
