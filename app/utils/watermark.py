from io import StringIO
from PIL import Image
import os
from django.conf import settings
from django.core.files.base import ContentFile


def get_watermarked_image(image: Image):
    print(f'Image {image} arrives...')
    image = Image.open(image)
    watermark = Image.open(os.path.join(settings.MEDIA_ROOT, 'yagody_png.png'))
    size = tuple(map(lambda x: (x * 20) // 100, image.size))
    watermark.thumbnail(size)
    image.paste(watermark, (10, 10))
    buffer = StringIO()
    image.save(fp=buffer, format='JPEG')
    print('Image must be watermarked')
    print(type(ContentFile(buffer.getvalue())))
    return ContentFile(buffer.getvalue())
