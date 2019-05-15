
from django.conf import settings
from django.core.files import File
import tempfile
import os


def generate_preview(poster, small=300, large=1200):

    if not poster.pdf:
        raise ValueError('no pdf file available')

    from PIL import Image
    from pylovepdf.tools.pdftojpg import PdfToJpg
    PIL.Image.MAX_IMAGE_PIXELS = 2**29

    with tempfile.TemporaryDirectory() as path:
        t = PdfToJpg(settings.ILPDF_KEY, verify_ssl=True, proxies=None)

        pdf_path = os.path.join(path, 'poster.pdf')
        with open(pdf_path, 'wb') as f:
            f.write(poster.pdf.read())

        t.add_file(pdf_path)
        t.pdfjpg_mode = 'pages'
        t.debug = False

        t.set_output_folder(path)
        t.execute()
        t.download()

        # generate previews
        img_path = os.path.join(t.download_path, t.downloaded_filename)
        large_path = os.path.join(path, 'large.jpg')
        small_path = os.path.join(path, 'small.jpg')
        img = Image.open(img_path)
        img.thumbnail((large, large))
        img.save(large_path)
        img.thumbnail((small, small))
        img.save(small_path)

        with open(large_path, 'rb') as f:
            poster.preview_large.save('large.jpg', File(f), save=True)
        with open(small_path, 'rb') as f:
            poster.preview_small.save('small.jpg', File(f), save=True)

