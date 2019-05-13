from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages

import logging
logger = logging.getLogger(__name__)

from .models import Poster
from .forms import PDFForm


#TODO: change to generic views

def index(request):
    poster_list = Poster.objects.filter(active=True).prefetch_related('authors')
    context = {'poster_list': poster_list}
    return render(request, 'pages/index.html', context)

def detail(request, slug):
    poster = get_object_or_404(Poster, slug=slug)
    return render(request, 'pages/detail.html', {'poster': poster})

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
                poster.active = False
                poster.save()
                messages.warning(request,
                    'Your poster was uploaded successfully, but we had trouble converting it. We will look into it and activate your poster within the next few hours.')
                return redirect('detail', slug=poster.slug)
            poster.active = True
            poster.save()
            messages.success(request, 'Your poster was uploaded successfully!')
            return redirect('detail', slug=poster.slug)
    else:
        form = PDFForm(instance=poster)
        form.active = False
    return render(request, 'pages/upload.html', {'form': form, 'poster': poster})

