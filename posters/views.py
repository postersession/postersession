from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
import time

import logging
logger = logging.getLogger(__name__)

from .models import Poster
from .forms import PDFForm

from django.core.mail import EmailMultiAlternatives


class LogEmail:
    def __init__(self, poster):
        self.subject = "Poster: {title}".format(title=poster.title),
        self.from_email = "postersession.ai <submissions@mg.postersession.ai>"
        self.to_email = ["log <log@mg.postersession.ai>"]
        self.messages = []

    def add_message(self, msg):
        self.messages.append(msg)

    def send(self):
        email = EmailMultiAlternatives(
            subject=self.subject, body=', '.join(self.messages),
            from_email=self.from_email, to=self.to_email)
        email.send()


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
                    logger.exception('Exception while converting PDF')
                    poster.active = False
                    poster.save()
                    messages.warning(request,
                        'Your poster was uploaded successfully, but we had trouble converting it. We will look into it and activate your poster within the next few hours.')

                    log_email.add_message('conversion failed')

                    return redirect('detail', slug=poster.slug)

                poster.active = True
                poster.save()
                messages.success(request, 'Your poster was uploaded successfully!')

                log_email.add_message('conversion successful')

                return redirect('detail', slug=poster.slug)
            else:
                messages.error(request, 'Please upload a PDF.')
                log_email.add_message('invalid file')
                form = PDFForm(instance=poster)
                return render(request, 'pages/upload.html', {'form': form, 'poster': poster})
        finally:
            log_email.send()

    else:
        form = PDFForm(instance=poster)
        form.active = False
        return render(request, 'pages/upload.html', {'form': form, 'poster': poster})



