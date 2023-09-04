from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


# AUTH USER MODEL contains id, username, first_name,
# last_name, email and password, some info about groups and permissions


class InterestHashtag(models.Model):
    name = models.CharField(max_length=50, unique=True)


class Likes(models.Model):
    # one reporter can have many articles
    from_person = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='from_person')
    to_person = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='to_person')
    like_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_person', 'to_person')


def user_directory_path(instance, filename):
    return f"profile_pics/{instance.login.id}/{filename}"


class UserInfo(models.Model):
    class Sex(models.TextChoices):
        male = "male"
        female = "female"
        different = "different"
        not_specified = "not_specified"

    login = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    gender = models.CharField(max_length=20, choices=Sex.choices, default=Sex.not_specified)
    city_of_residence_latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, default='')
    city_of_residence_longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, default='')
    year_of_birth = models.PositiveSmallIntegerField(validators=[MaxValueValidator(2022), MinValueValidator(1920)])
    user_avatar = models.URLField(default='https://http.cat/images/101.jpg')
    user_description = models.TextField()
    interest_hashtags = models.ManyToManyField(InterestHashtag, blank=True)