# Generated by Django 4.1.6 on 2023-09-04 08:07

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user_profile", "0003_remove_userinfo_interest_hashtags_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="userinfo",
            name="interest_hashtags",
            field=models.ManyToManyField(blank=True, to="user_profile.interesthashtag"),
        ),
    ]
