# Generated by Django 4.0.1 on 2022-04-25 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0002_course_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='instructor',
            name='facebook',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='instructor',
            name='instagram',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='instructor',
            name='linkedln',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='instructor',
            name='twitter',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='instructor',
            name='title',
            field=models.TextField(blank=True, null=True),
        ),
    ]