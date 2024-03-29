# Generated by Django 4.2 on 2023-04-15 16:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0002_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='election',
            name='secondary',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='secondary_election_set', to='voting.votetaker'),
        ),
        migrations.AlterField(
            model_name='election',
            name='votetaker',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='voting.votetaker'),
        ),
    ]
