from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

from .models import Poster


#TODO: change to generic views

def index(request):
    #poster_list = Poster.objects.order_by('-pub_date')
    poster_list = Poster.objects.prefetch_related('authors')
    context = {'poster_list': poster_list}
    return render(request, 'pages/index.html', context)

def detail(request, poster_id):
    poster = get_object_or_404(Poster, pk=poster_id)
    authors = poster.authors
    return render(request, 'pages/detail.html', {'poster': poster, 'authors': authors})

