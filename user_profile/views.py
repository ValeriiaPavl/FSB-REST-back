import json

from django.contrib.auth import authenticate
from django.http import Http404, JsonResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

import user_profile.serializer
from FSB_REST.auth.authentication_utility import generate_jwt_token
from FSB_REST.auth.middleware import JWTAuthentication
from user_profile.models import UserInfo, Likes, InterestHashtag


class UserInfoList(APIView):
    def get(self, request, format=None):
        user_infos = UserInfo.objects.select_related('login').prefetch_related('interest_hashtags').all()
        serializer = user_profile.serializer.UserInfoSerializer(user_infos, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = user_profile.serializer.UserInfoPOSTSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetail(APIView):
    def get_object(self, pk):
        try:
            return UserInfo.objects.select_related('login').prefetch_related('interest_hashtags').get(login_id=pk)
        except UserInfo.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = user_profile.serializer.UserInfoSerializer(user)
        return Response(serializer.data)


class LikesFromUserView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        all_likes = Likes.objects.all()
        user_id = request.user.id
        person_likes = all_likes.filter(from_person=user_id)
        serialized_likes_from = user_profile.serializer.LikesSerializer(person_likes, many=True)
        return Response(serialized_likes_from.data)

    def post(self, request, from_person):
        serializer = user_profile.serializer.LikesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LikesToUserView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.id
        who_liked_the_person = Likes.objects.filter(to_person=user_id)
        serialized_likes_to = user_profile.serializer.LikesSerializer(who_liked_the_person, many=True)
        return Response(serialized_likes_to.data)


class MutualLikesView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        all_likes = Likes.objects.all()
        user_id = request.user.id
        person_likes = all_likes.filter(from_person=user_id).values_list('to_person', flat=True)
        who_liked_the_person = all_likes.filter(to_person=user_id).values_list('from_person', flat=True)
        mutual_likes = person_likes.intersection(who_liked_the_person)
        user_infos = UserInfo.objects.filter(login_id__in=mutual_likes).prefetch_related("interest_hashtags")
        serializer = user_profile.serializer.UserInfoSerializer(user_infos, many=True)
        print(serializer.data)
        return Response(serializer.data)


class HashtagView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id = request.user.id
        user_from_db = UserInfo.objects.get(login_id=user_id)
        user_interests = user_from_db.interest_hashtags.values_list('name', flat=True)
        serializer = user_profile.serializer.HashtagSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid():
            curr_hashtag = serializer.validated_data['name']
            if curr_hashtag not in user_interests:
                all_hashtags = InterestHashtag.objects.all()
                hashtags_names = all_hashtags.values_list('name', flat=True)
                if curr_hashtag in hashtags_names:
                    print("Yes, it is")
                    existing_tag = all_hashtags.get(name=curr_hashtag)
                    user_from_db.interest_hashtags.add(existing_tag)
                else:
                    new_tag = serializer.save()
                user_from_db.interest_hashtags.add(new_tag)
                return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)

            else:
                data = {
                    'error': 'This hashtag already exists in user interest hashtags'
                }
                return JsonResponse(data, status=400)
        else:
            return JsonResponse(data=serializer.errors, status=400)


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


class RegisterView(APIView):
    def post(self, request):
        serializer = user_profile.serializer.RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
