
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse

import posters.views


class LogEmail:
    def __init__(self, poster):
        self.subject = "Poster: {title}".format(title=poster.title),
        self.from_email = "postersession.ai <submissions@postersession.ai>"
        self.to_email = ["log <log@postersession.ai>"]
        self.messages = [
            'title: %s' % poster.title,
            'authors: %s' % ', '.join([str(a) for a in poster.author_list()]),
            'poster id: %s' % poster.pk,
            'upload url: %s' % reverse(posters.views.upload, args=[poster.access_key]),
            '',
        ]

    def add_message(self, msg):
        self.messages.append(msg)

    def send(self):
        EmailMultiAlternatives(
            subject=self.subject,
            body='\n'.join(self.messages),
            from_email=self.from_email,
            to=self.to_email
        ).send()

