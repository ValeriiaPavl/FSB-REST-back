import json

from django.contrib.auth import authenticate
from django.http import Http404, JsonResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from FSB_REST.auth.authentication_utility import generate_jwt_token
from FSB_REST.auth.middleware import JWTAuthentication
from user_profile.models import UserInfo, Likes
from user_profile.serializer import UserInfoSerializer, LikesSerializer


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


class LikesView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        all_likes = Likes.objects.all()
        person_likes = all_likes.filter(from_person=pk)
        user_id = request.user.id
        person_likes = all_likes.filter(from_person=user_id)
        serialized_likes = LikesSerializer(person_likes, many=True)
        return Response(serialized_likes.data)

    def post(self, request, from_person):
        serializer = LikesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):

        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            token = generate_jwt_token(user.id)
            return JsonResponse({'token': token})
        else:
            return JsonResponse({'error': 'Authentication failed'}, status=401)
