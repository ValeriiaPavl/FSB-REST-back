from rest_framework import serializers
from user_profile.models import UserInfo


class UserInfoSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='login.username')
    interest_hashtags = serializers.SerializerMethodField()

    class Meta:
        model = UserInfo
        fields = ['username', 'gender',
                  'city_of_residence_latitude',
                  'city_of_residence_longitude',
                  'year_of_birth', 'user_avatar',
                  'user_description', 'interest_hashtags']

    def get_interest_hashtags(self, obj):
        return [hashtag.name for hashtag in obj.interest_hashtags.all()]
