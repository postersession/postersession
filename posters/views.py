from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
import time

import logging
logger = logging.getLogger(__name__)

from .models import Poster
from .forms import PDFForm



USR_CONVERSION_FAILED = "Your poster was uploaded successfully, but we had trouble converting it. We will look into it and activate your poster within the next few hours."
USR_SUCCESS = "Your poster was uploaded successfully!"
USR_INVALID_FILE = "Please upload a valid file."
USR_EXISTING_FILE = "Your poster has been uploaded already. You may update it by uploading a new file."


class LogEmail:
    def __init__(self, poster):
        self.subject = "Poster: {title}".format(title=poster.title),
        self.from_email = "postersession.ai <submissions@mg.postersession.ai>"
        self.to_email = ["log <log@mg.postersession.ai>"]
        self.messages = []

    def add_message(self, msg):
        self.messages.append(msg)

    def send(self):
        EmailMultiAlternatives(
            subject=self.subject,
            body=', '.join(self.messages),
            from_email=self.from_email,
            to=self.to_email
        ).send()


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
    log_email = LogEmail(poster)
    form = PDFForm(instance=poster)
    if poster.pdf:
        messages.info(request, USR_EXISTING_FILE)

    if request.method == 'POST':
        try:
            log_email.add_message('uploaded')

            form = PDFForm(request.POST, request.FILES, instance=poster)
            if form.is_valid():
                log_email.add_message('valid file')
                form.save()
                try:
                    poster.generate_preview()
                except:
                    poster.active = False
                    poster.save()

                    logger.exception('Exception while converting PDF')
                    messages.warning(request, USR_CONVERSION_FAILED)
                    log_email.add_message('conversion failed')

                    return redirect('detail', slug=poster.slug)

                poster.active = True
                poster.save()
                messages.success(request, USR_SUCCESS)
                log_email.add_message('conversion successful')

                return redirect('detail', slug=poster.slug)
            else:
                log_email.add_message('invalid file')
                messages.error(request, USR_INVALID_FILE)
        finally:
            log_email.send()

    form.active = False
    return render(request, 'pages/upload.html', {'form': form, 'poster': poster})



