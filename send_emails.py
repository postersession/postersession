import json
import hashlib
import base64
import datetime

from django.core.mail import EmailMultiAlternatives
from posters.models import Conference, Poster, Author, PosterAuthor


def send_email(paper):

    poster = Poster.objects.get(external_id=paper['id'])

    filtered_authors = []

    for author in poster.author_list():
        poster_author = PosterAuthor.objects.get(author=author, poster=poster)
        if poster_author.email_sent:
            print('WARN: Not re-sending %s (%s)' % (author, poster))
            continue
        if poster_author.exclude:
            print('WARN: excluding %s (%s)' % (author, poster))
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

Please reach out if you have any questions.

Thanks a lot,
Jonathan Binas (Mila) and Avital Oliver (Google Brain).

""".format(
        author_names=u", ".join([author.name for author in filtered_authors]),
        upload_key=poster.access_key,
        title=poster.title,
        to=[str(author) for author in filtered_authors])

    msg = EmailMultiAlternatives(
        subject="Share your ICLR poster on postersession.ai",
        body=body,
        from_email="postersession.ai <submissions@mg.postersession.ai>",
#        to=["{name} <{email}>".format(name=author['name'], email=author['email']) for author in authors],
        to=["Avital Oliver <avital@thewe.net>", "Jonathan Binas <jbinas@gmail.com>"]
        )

    print(msg)

    try:
        msg.send()

        for author in filtered_authors:
            poster_author = PosterAuthor.objects.get(author=author, poster=poster)
            poster_author.email_sent = datetime.datetime.now()
            poster_author.save()
    except:
        print('ERR: Message could not be sent.')


def send_emails():
    with open('iclr19.json') as f:
        papers = json.load(f)
        for paper in papers[0:2]:
            send_email(paper)


