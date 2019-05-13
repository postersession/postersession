from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse

import logging
logger = logging.getLogger(__name__)

from .models import Poster
from .forms import PDFForm


#TODO: change to generic views

def index(request):
    #poster_list = Poster.objects.order_by('-pub_date')
    poster_list = Poster.objects.filter(active=True).prefetch_related('authors')
    context = {'poster_list': poster_list}
    return render(request, 'pages/index.html', context)

def detail(request, poster_id):
    poster = get_object_or_404(Poster, pk=poster_id)
    authors = poster.author_list()
    return render(request, 'pages/detail.html', {'poster': poster, 'authors': authors})

def upload(request, access_key):
    poster = get_object_or_404(Poster, access_key=access_key)
    if request.method == 'POST':
        form = PDFForm(request.POST, request.FILES, instance=poster)
        if form.is_valid():
            form.save()
            try:
                poster.generate_preview()
            except:
                logger.exception('Exception while converting PDF')
                #TODO notify admins about this case
                return redirect('success-delayed')
            poster.active = True
            poster.save()
            return redirect('success')
    else:
        form = PDFForm(instance=poster)
        form.active = False
    return render(request, 'pages/upload.html', {'form': form, 'poster': poster})
