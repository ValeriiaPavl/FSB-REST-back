from rest_framework import serializers

from user_profile.models import UserInfo, Likes


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


class LikesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Likes
        fields = '__all__'
