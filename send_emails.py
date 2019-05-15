import json
import hashlib
import base64
from django.utils import timezone

from django.core.mail import EmailMultiAlternatives
from posters.models import Conference, Poster, Author, PosterAuthor

import logging
logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

fileHandler = logging.FileHandler("email.log")
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)


def send_email(paper, num_authors=99):

    poster = Poster.objects.get(external_id=paper['id'])

    filtered_authors = []

    for author in poster.author_list()[:num_authors]:
        poster_author = PosterAuthor.objects.get(author=author, poster=poster)
        if poster_author.email_sent:
            logger.warning('Not re-sending %s (%s)' % (author, poster))
            continue
        if poster_author.exclude:
            logger.warning('excluding %s (%s)' % (author, poster))
            continue
        filtered_authors.append(author)

    body = u"""
Hello {author_names},

You presented the paper "{title}" at a poster session at ICLR'19.

Poster sessions are a great way for researchers to gain a quick overview of the current state of their field. It would be great if this was available even to people who were not able to attend the conference.

We hope to get all the ICLR posters available online, creating a "virtual poster session".

We just need a minute of your time -- please visit this link, where you can upload a PDF of your poster:

https://postersession.ai/upload/{upload_key}

All posters will be made public on https://postersession.ai/
Please let us know if you have any questions!

Thanks a lot,

Jonathan Binas (Mila) and Avital Oliver (Google Brain)

""".format(
        author_names=u", ".join([author.name for author in filtered_authors]),
        upload_key=poster.access_key,
        title=poster.title,
        to=[str(author) for author in filtered_authors])

    msg = EmailMultiAlternatives(
        subject="Share your ICLR poster on postersession.ai",
        body=body,
        from_email="postersession.ai <submissions@mg.postersession.ai>",
        to=[str(author) for author in filtered_authors],
        #bcc=["log@mg.postersession.ai"]
        )

    #print(msg.to, msg.body)

    try:
        if filtered_authors:
            msg.send()

            for author in filtered_authors:
                poster_author = PosterAuthor.objects.get(author=author, poster=poster)
                poster_author.email_sent = timezone.now()
                poster_author.save()
            logger.info('Message sent.')
        else:
            logger.info('Not sending (no authors).')
    except:
        logger.error('Message could not be sent.')


def send_emails(start_id=0, end_id=1, send=False):
    with open('iclr19.json') as f:
        papers = json.load(f)
        for i, paper in enumerate(papers[start_id:end_id]):
            logger.info('processing paper %s' % (i + start_id))
            logger.info(str(paper))
            if send:
                send_email(paper)


