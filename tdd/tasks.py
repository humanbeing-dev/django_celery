from io import BytesIO
from tdd.models import Member

from PIL import Image
from django.core.files import File
from celery import shared_task


@shared_task(name="generate_avatar_thumbnail")
def generate_avatar_thumbnail(member_pk):
    member = Member.objects.get(pk=member_pk)
    
    image = Image.open(member.avatar)
    size = (100, 100)
    image.thumbnail(size)
    thumb_io = BytesIO()
    image.save(thumb_io, "JPEG")
    
    member.avatar_thumbnail = File(thumb_io, name=f"{member.pk}-avatar-thumbnail.jpg")
    member.save(update_fields=["avatar_thumbnail"])