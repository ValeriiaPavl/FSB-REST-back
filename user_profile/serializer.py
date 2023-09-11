from math import radians, sin, atan2, sqrt, cos

from django.contrib.auth.models import User
from rest_framework import serializers

from user_profile.models import UserInfo, Likes, InterestHashtag


class UserInfoSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='login.username')
    interest_hashtags = serializers.SerializerMethodField()
    user_id = serializers.ReadOnlyField(source='login.id')

    class Meta:
        model = UserInfo
        fields = ['username', 'gender',
                  'city_of_residence_latitude',
                  'city_of_residence_longitude',
                  'year_of_birth', 'user_avatar',
                  'user_description', 'interest_hashtags', 'user_id']

    def get_interest_hashtags(self, obj):
        return [hashtag.name for hashtag in obj.interest_hashtags.all()]


def get_distance(point1, point2):
    R = 6370
    lat1 = radians(point1[0])  # insert value
    lon1 = radians(point1[1])
    lat2 = radians(point2[0])
    lon2 = radians(point2[1])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance


class ExtendedUserInfoSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='login.username')
    interest_hashtags = serializers.SerializerMethodField()
    user_id = serializers.ReadOnlyField(source='login.id')
    liked = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()

    class Meta:
        model = UserInfo
        fields = ['username', 'gender',
                  'city_of_residence_latitude',
                  'city_of_residence_longitude',
                  'year_of_birth', 'user_avatar',
                  'user_description', 'interest_hashtags', 'user_id', 'liked', 'distance']

    def get_interest_hashtags(self, obj):
        return [hashtag.name for hashtag in obj.interest_hashtags.all()]

    def get_liked(self, obj):
        return obj.login_id in self.context['likes_from_me']

    def get_distance(self, obj):
        userLocation = [obj.city_of_residence_latitude, obj.city_of_residence_longitude]
        meLocation = [self.context['me'].city_of_residence_latitude, self.context['me'].city_of_residence_longitude]

        return get_distance(meLocation, userLocation)

class UserInfoPOSTSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = ['gender',
                  'city_of_residence_latitude',
                  'city_of_residence_longitude',
                  'year_of_birth', 'user_avatar',
                  'user_description']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class LikesSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='to_person.username')
    gender = serializers.ReadOnlyField(source='to_person.userinfo.gender')
    user_avatar = serializers.ReadOnlyField(source='to_person.userinfo.user_avatar')
    class Meta:
        model = Likes
        fields = ["like_added", "to_person_id", "username", "user_avatar", "gender"]





class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterestHashtag
        fields = ['name']

    name = serializers.CharField(max_length=50, validators=[])
