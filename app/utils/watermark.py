from io import BytesIO
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
    img_io = BytesIO()
    image.save(fp=img_io, format='JPEG', quality=100)
    print(f'Image {image} must be watermarked')
    return ContentFile(img_io.getvalue(), f'{image.filename}_watermarked.jpg')
