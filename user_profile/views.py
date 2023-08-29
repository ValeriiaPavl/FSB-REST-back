from django.http import Http404
from rest_framework.response import Response
from rest_framework.views import APIView

from user_profile.models import UserInfo
from user_profile.serializer import UserInfoSerializer


class UserInfoList(APIView):
    def get(self, request, format=None):
        user_infos = UserInfo.objects.select_related('login').prefetch_related('interest_hashtags').all()
        serializer = UserInfoSerializer(user_infos, many=True)
        return Response(serializer.data)


class UserDetail(APIView):
    def get_object(self, pk):
        try:
            return UserInfo.objects.select_related('login').prefetch_related('interest_hashtags').get(pk=pk)
        except UserInfo.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = UserInfoSerializer(user)
        return Response(serializer.data)
