# Generated by Django 4.0.2 on 2022-02-15 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_alter_user_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='image',
            field=models.ImageField(default='images/default_user_image.png', upload_to='images/user_images/'),
        ),
    ]
