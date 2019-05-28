from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.core.cache import caches
from django.views.decorators.cache import cache_page
import time
import logging

from .models import Poster
from .forms import PDFForm
from .utils import email_log

logger = logging.getLogger(__name__)


USR_FAILED = "Your poster was uploaded successfully, but we had trouble converting it. We will look into it and activate your poster within the next few hours."
USR_FAILED_MULTIPAGE = "It looks like you might have uploaded a multi-page document. We can only handle single page posters, at the moment."
USR_SUCCESS = "Your poster was uploaded successfully! It will appear on the front page within a minute or two."
USR_INVALID_FILE = "Please upload a valid file."
USR_EXISTING_FILE = "Your poster has been uploaded already. You may update it by uploading a new file."


#TODO: change to generic views

@cache_page(settings.CACHE_TTL, cache='index')
def index(request):
    poster_list = Poster.objects.filter(active=True).prefetch_related('authors')
    context = {'poster_list': poster_list}
    return render(request, 'pages/index.html', context)

def detail(request, slug):
    poster = get_object_or_404(Poster, slug=slug)
    return render(request, 'pages/detail.html', {'poster': poster})

def upload(request, access_key):
    poster = get_object_or_404(Poster, access_key=access_key)
    log_email = email_log.LogEmail(poster)
    form = PDFForm(instance=poster)
    if poster.pdf:
        messages.info(request, USR_EXISTING_FILE)

    if request.method == 'POST':
        try:
            log_email.add_message('INFO: uploaded')

            form = PDFForm(request.POST, request.FILES, instance=poster)
            if form.is_valid():
                log_email.add_message('INFO: valid file')
                form.save()
                try:
                    poster.generate_preview()
                    poster.active = True
                    poster.save()
                    messages.success(request, USR_SUCCESS)
                    log_email.add_message('INFO: conversion successful')
                    return redirect('detail', slug=poster.slug)
                except TypeError:
                    poster.active = False
                    poster.save()
                    logger.exception('ERR: failed to convert PDF (id %s) -- likely multi-page document' % poster.pk)
                    messages.error(request, USR_FAILED_MULTIPAGE)
                    log_email.add_message('ERR: conversion failed -- likely multi-page document')
                except:
                    poster.active = False
                    poster.save()
                    logger.exception('ERR: failed to convert PDF (id %s)' % poster.pk)
                    messages.warning(request, USR_FAILED)
                    log_email.add_message('ERR: conversion failed')
                    return redirect('detail', slug=poster.slug)
            else:
                log_email.add_message('ERR: invalid file')
                messages.error(request, USR_INVALID_FILE)
        finally:
            caches['index'].clear()
            log_email.send()

    form.active = False
    return render(request, 'pages/upload.html', {'form': form, 'poster': poster})

def rss(request):
    pass




