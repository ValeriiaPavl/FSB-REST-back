import json

import jwt
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import Http404, JsonResponse, HttpResponseNotAllowed
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
        user_serializer = user_profile.serializer.UserSerializer(data=request.data.get("user"))

        if user_serializer.is_valid():
            user = user_serializer.save()

            profile_data = request.data.get('profile')
            profile_serializer = user_profile.serializer.UserInfoPOSTSerializer(data=profile_data)
            if profile_serializer.is_valid():
                profile = profile_serializer.save(login=user)
                return Response({'user': user_serializer.data, 'profile': profile_serializer.data},
                                status=status.HTTP_201_CREATED)
            else:
                user.delete()
                return Response({'errors': {'profile': profile_serializer.errors}}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'errors': {'user': user_serializer.errors}}, status=status.HTTP_400_BAD_REQUEST)


class UserExtendedInfoList(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header:
            jwt_token = auth_header.split(' ')[1]
            try:
                decoded_token = jwt.decode(jwt_token, settings.SECRET_KEY, algorithm='HS256')
                user_id = decoded_token.get('user_id')
                try:
                    all_users = UserInfo.objects.select_related('login').prefetch_related('interest_hashtags').exclude(
                        login__id=user_id)

                    all_likes_from = list(map(lambda l: l.to_person.id, Likes.objects.filter(from_person=user_id)))
                    me = UserInfo.objects.get(login__id=user_id)

                    serializer = user_profile.serializer.ExtendedUserInfoSerializer(all_users, many=True, context={
                        'likes_from_me': all_likes_from, 'me': me})
                    return Response(serializer.data)
                except UserInfo.DoesNotExist:
                    raise Http404
            except:
                raise HttpResponseNotAllowed


class UserExtendedDetail(APIView):
    def get_object(self, pk):
        try:
            return UserInfo.objects.select_related('login').prefetch_related('interest_hashtags').get(login_id=pk)
        except UserInfo.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header:
            jwt_token = auth_header.split(' ')[1]
            try:
                decoded_token = jwt.decode(jwt_token, settings.SECRET_KEY, algorithm='HS256')
                user_id = decoded_token.get('user_id')
                all_likes_from = list(map(lambda l: l.to_person.id, Likes.objects.filter(from_person=user_id)))
                me = UserInfo.objects.get(login__id=user_id)
                user = UserInfo.objects.select_related('login').prefetch_related("interest_hashtags").get(login_id=pk)
                serializer = user_profile.serializer.ExtendedUserInfoSerializer(user, context={
                    'likes_from_me': all_likes_from, 'me': me})
                return Response(serializer.data)
            except UserInfo.DoesNotExist:
                raise Http404


# class UserDetail(APIView):
#     def get_object(self, pk):
#         try:
#             return UserInfo.objects.select_related('login').prefetch_related('interest_hashtags').get(login_id=pk)
#         except UserInfo.DoesNotExist:
#             raise Http404
#
#     def get(self, request, pk, format=None):
#         user = self.get_object(pk)
#         serializer = user_profile.serializer.UserInfoSerializer(user)
#         return Response(serializer.data)

class UserFromTokenView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header:
            jwt_token = auth_header.split(' ')[1]
            try:
                decoded_token = jwt.decode(jwt_token, settings.SECRET_KEY, algorithm='HS256')
                user_id = decoded_token.get('user_id')
                try:
                    user = UserInfo.objects.select_related('login').prefetch_related('interest_hashtags').get(
                        login__id=user_id)
                    serializer = user_profile.serializer.MyProfileSerializer(user)
                    return Response(serializer.data)
                except UserInfo.DoesNotExist:
                    raise Http404

            except jwt.ExpiredSignatureError:
                return Response({'message': 'Token has expired'}, status=status.HTTP_401_UNAUTHORIZED)
            except jwt.DecodeError:
                return Response({'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)

    def patch(self, request):
        print(request.data)
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header:
            jwt_token = auth_header.split(' ')[1]
            try:
                decoded_token = jwt.decode(jwt_token, settings.SECRET_KEY, algorithm='HS256')
                user_id = decoded_token.get('user_id')
                user = User.objects.get(id=user_id)
                user_serializer = user_profile.serializer.UserSerializer(instance=user, data=request.data.get("user"),
                                                                         partial=True)
            except jwt.ExpiredSignatureError:
                return Response({'message': 'Token has expired'}, status=status.HTTP_401_UNAUTHORIZED)
            except jwt.DecodeError:
                return Response({'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)

        if user_serializer.is_valid():
            print(user_serializer)
            user = user_serializer.save()
            new_profile_data = request.data.get('profile')
            profile_from_db = UserInfo.objects.select_related('login').get(login_id=user_id)
            profile_serializer = user_profile.serializer.UserInfoPOSTSerializer(instance=profile_from_db,
                                                                                data=new_profile_data, partial=True)
            if profile_serializer.is_valid():
                print(profile_serializer)
                new_profile = profile_serializer.save()
                return Response({'user': user_serializer.data, 'profile': profile_serializer.data},
                                status=status.HTTP_200_OK)
            else:
                return Response({'errors': {'profile': profile_serializer.errors}}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'errors': {'user': user_serializer.errors}}, status=status.HTTP_400_BAD_REQUEST)


class LikesFromMeView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        all_likes = Likes.objects.all()
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header:
            jwt_token = auth_header.split(' ')[1]
            try:
                decoded_token = jwt.decode(jwt_token, settings.SECRET_KEY, algorithm='HS256')
                user_id = decoded_token.get('user_id')
                person_likes = all_likes.filter(from_person=user_id).select_related("to_person__userinfo")
                print(person_likes)

                serialized_likes_from = user_profile.serializer.LikesFromMeSerializer(person_likes, many=True)
                return Response(serialized_likes_from.data)
            except jwt.ExpiredSignatureError:
                return Response({'message': 'Token has expired'}, status=status.HTTP_401_UNAUTHORIZED)
            except jwt.DecodeError:
                return Response({'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)

        else:
            return Response({'message': 'Token not provided'}, status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        print(request.data)
        if auth_header:
            jwt_token = auth_header.split(' ')[1]
            try:
                decoded_token = jwt.decode(jwt_token, settings.SECRET_KEY, algorithm='HS256')
                user_id = decoded_token.get('user_id')

                serializer = user_profile.serializer.LikesFromMePOSTSerializer(
                    data={"from_person": user_id, "to_person": request.data['to_person']})
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except jwt.ExpiredSignatureError:
                return Response({'message': 'Token has expired'}, status=status.HTTP_401_UNAUTHORIZED)
            except jwt.DecodeError:
                return Response({'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)

        else:
            return Response({'message': 'Token not provided'}, status=status.HTTP_401_UNAUTHORIZED)


class LikesToMeView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.id
        who_liked_me = Likes.objects.filter(to_person=user_id).select_related("from_person__userinfo")
        serialized_likes_to = user_profile.serializer.LikesToMeSerializer(who_liked_me, many=True)
        return Response(serialized_likes_to.data)


class MutualLikesView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        all_likes = Likes.objects.all()
        user_id = request.user.id
        person_likes = set(all_likes.filter(from_person=user_id).values_list('to_person', flat=True))
        print(person_likes)
        who_liked_the_person = set(all_likes.filter(to_person=user_id).values_list('from_person', flat=True))
        mutual_likes = person_likes.intersection(who_liked_the_person)
        print(mutual_likes)
        user_infos = Likes.objects.filter(Q(from_person__in=mutual_likes) & Q(to_person=user_id)).select_related(
            "from_person__userinfo")
        serializer = user_profile.serializer.MutualLikesSerializer(user_infos, many=True)
        return Response(serializer.data)


class HashtagView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id = request.user.id
        user_from_db = UserInfo.objects.get(login__id=user_id)
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


class GetUserIdView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header:
            jwt_token = auth_header.split(' ')[1]
            try:
                decoded_token = jwt.decode(jwt_token, settings.SECRET_KEY, algorithm='HS256')
                user_id = decoded_token.get('user_id')
                try:
                    user = UserInfo.objects.select_related('login').get(
                        login_id=user_id).login_id
                    return Response(data={"user_id": user}, status=status.HTTP_200_OK)
                except UserInfo.DoesNotExist:
                    raise Http404

            except jwt.ExpiredSignatureError:
                return Response({'message': 'Token has expired'}, status=status.HTTP_401_UNAUTHORIZED)
            except jwt.DecodeError:
                return Response({'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
