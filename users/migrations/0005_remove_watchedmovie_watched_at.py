# Generated by Django 4.2.5 on 2023-10-25 04:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_watchedmovie_user_alter_watchlist_user_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='watchedmovie',
            name='watched_at',
        ),
    ]
