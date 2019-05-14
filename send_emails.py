import json
import hashlib
import base64

from django.core.mail import EmailMultiAlternatives


import datetime

from posters import models

def send_email(paper):
    title = paper['title']
    authors = paper['authors']

    poster = models.Poster.objects.all().filter(external_id=paper['id'])[0]

    filtered_authors = []
    for author in authors[0:3]:
        db_author = models.Author.objects.all().filter(email=author['email'])[0]
        poster_author = models.PosterAuthor.objects.all().filter(author=db_author, poster=poster)[0]
        if not poster_author.email_sent:
            filtered_authors += [author]

    upload_key = poster.access_key
    body = u"""
Hello {author_names},

We're collecting poster PDFs from ICLR'19 to make them public and 
help people who weren't able to attend the conference.

We hope to get all the ICLR posters available online, creating
a "virtual poster session". 

We just need a minute of your time -- please visit this link,
where you can upload a PDF of your poster for
{title}:
https://postersession.ai/upload/{upload_key}

To reduce load, we are only emailing the first three authors
of each paper.

All posters will be made public on https://postersession.ai/

Thanks,
Jonathan Binas (Mila) and Avital Oliver (Google Brain).

to={to}


""".format(
        author_names=u", ".join([author["name"] for author in filtered_authors]),
        paper_id=paper['id'],
        upload_key=upload_key,
        title=title,
        to=["{name} <{email}>".format(name=author['name'], email=author['email']) for author in filtered_authors])

    

    msg = EmailMultiAlternatives(
        subject="Please upload your ICLR poster for {title}".format(title=title),
        body=body,
        from_email="postersession.ai <submissions@mg.postersession.ai>",
#        to=["{name} <{email}>".format(name=author['name'], email=author['email']) for author in authors],
#        to=["test <test@mg.postersession.ai>"]
        to=["Avital Oliver <avital@thewe.net>", "Jonathan Binas <jbinas@gmail.com>"]
        )

    # Send it:
    msg.send()

    print(msg)

    for author in filtered_authors:
        db_author = models.Author.objects.all().filter(email=author['email'])[0]
        poster_author = models.PosterAuthor.objects.all().filter(author=db_author, poster=poster)[0]
        poster_author.email_sent = datetime.datetime.now()
        poster_author.save()


def send_emails():
    with open('iclr19.json') as iclr_json:
        papers = json.load(iclr_json)
        for paper in papers[0:5]:
            send_email(paper)
        

