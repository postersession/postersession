import json
import hashlib
import base64

from posters.models import Conference, Poster, Author, PosterAuthor

import uuid


def populate_db(input_file='iclr19.json', conference_name='ICLR 2019'):

    conference, _ = Conference.objects.get_or_create(name=conference_name)

    with open(input_file) as f:
        papers = json.load(f)

    for paper in papers:
        poster, created = Poster.objects.get_or_create(
            conference=conference,
            title=paper['title'],
            external_id=paper['id'],
            author_names=paper['id'] if 'id' in paper else None,
            )
        if created:
            poster.access_key = str(uuid.uuid4())
            poster.save()

        for author in paper['authors']:
            db_author, _ = Author.objects.get_or_create(email=author['email'], name=author['name'])
            PosterAuthor.objects.get_or_create(author=db_author, poster=poster)


if __name__ == '__main__':

    populate_db()

