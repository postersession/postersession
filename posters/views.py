from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
import time

import logging
logger = logging.getLogger(__name__)

from .models import Poster
from .forms import PDFForm

from django.core.mail import EmailMultiAlternatives


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
        log_msg = EmailMultiAlternatives(
            subject="Poster: {title}".format(title=poster.title),
            body="Uploaded",
            from_email="postersession.ai <submissions@mg.postersession.ai>",
            to=["log <log@mg.postersession.ai>"])
        log_msg.send()

        form = PDFForm(request.POST, request.FILES, instance=poster)
        if form.is_valid():
            log_msg = EmailMultiAlternatives(
                subject="Poster: {title}".format(title=poster.title),
                body="Valid file",
                from_email="postersession.ai <submissions@mg.postersession.ai>",
                to=["log <log@mg.postersession.ai>"])
            log_msg.send()

            form.save()
            try:
                poster.generate_preview()
            except:
                logger.exception('Exception while converting PDF')
                poster.active = False
                poster.save()
                messages.warning(request,
                    'Your poster was uploaded successfully, but we had trouble converting it. We will look into it and activate your poster within the next few hours.')

                log_msg = EmailMultiAlternatives(
                    subject="Poster: {title}".format(title=poster.title),
                    body="Conversion failed",
                    from_email="postersession.ai <submissions@mg.postersession.ai>",
                    to=["log <log@mg.postersession.ai>"])
                log_msg.send()

                return redirect('detail', slug=poster.slug)
            poster.active = True
            poster.save()
            messages.success(request, 'Your poster was uploaded successfully!')

            log_msg = EmailMultiAlternatives(
                subject="Poster: {title}".format(title=poster.title),
                body="Conversion successful",
                from_email="postersession.ai <submissions@mg.postersession.ai>",
                to=["log <log@mg.postersession.ai>"])
            log_msg.send()

            return redirect('detail', slug=poster.slug)
        else:
            log_msg = EmailMultiAlternatives(
                subject="Poster: {title}".format(title=poster.title),
                body="Invalid file",
                from_email="postersession.ai <submissions@mg.postersession.ai>",
                to=["log <log@mg.postersession.ai>"])
            log_msg.send()

    else:
        form = PDFForm(instance=poster)
        form.active = False
    return render(request, 'pages/upload.html', {'form': form, 'poster': poster})

