import json
import hashlib
import base64

from django.core.mail import EmailMultiAlternatives
from anymail.message import attach_inline_image_file

from posters import models

import uuid

iclr2019 = models.Conference.objects.all().filter(name="ICLR 2019")[0] 

def populate_db():
    with open('iclr19.json') as iclr_json:
        papers = json.load(iclr_json)

        for paper in papers:
            title = paper['title']
            id = paper['id']
            conference = 'iclr19'
            key = conference + '/' + id

            poster = models.Poster(
                conference=iclr2019,
                title=title,
                access_key=str(uuid.uuid4()),
                external_id=id)
            poster.save()

            authors = paper['authors']
            db_authors = []
            for author in authors:
                found_db_authors = models.Author.objects.all().filter(email=author['email'])
                if len(found_db_authors) > 0:
                    models.PosterAuthor(author=found_db_authors[0], poster=poster).save()
                else:
                    db_author = models.Author(email=author['email'], name=author['name'])
                    db_author.save()
                    models.PosterAuthor(author=db_author, poster=poster).save()
        

