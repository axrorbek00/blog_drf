from itertools import chain

from django.shortcuts import render
from rest_framework.views import APIView

from .serializers import (
    CategorySerializer,
    PostSerializer,
    FollowingSerializer,
    FollowersSerializer,
    LikeSerializer,
    LikeDeleteSerializer,
    UserSavedPostsSerializer,
    UserSavedPostsCategorySerializer,

)
from user.models import MyUser
from .models import Category, Post, PostViews, Following, Like, SavedPost
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions, serializers
from rest_framework import status
from rest_framework.generics import ListAPIView
from django.utils import timezone
import datetime
from django.db.models import Q, Count
from drf_yasg.utils import swagger_auto_schema


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # permission_classes = [permissions.IsAuthenticated]


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    # permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):  # mainga chiqadgan bostlar
        # TODO optimize below if hafl a year it still checks first user
        is_all_zero = Post.objects.filter(views_count__gt=0).exists()  # agar tru qaytsa 1- user emassiz, gt==(>)

        if is_all_zero == False:  # option 1
            result = []
            categories = Category.objects.all()
            for category in categories:
                post_by_category = Post.objects.filter(category=category).order_by('-id')[:3]
                result.append(post_by_category)

            queryset = chain(*result)  # (*) fazifasi [1,2]>1,2 qiladi

        else:  # option : 2
            followings = Following.objects.filter(user=request.user).values('following_id')
            posts = Post.objects.filter(user_id__in=followings, is_draft=False).values('id')

            posts = [post['id'] for post in posts]

            post_views = PostViews.objects.filter(  # follow qilgan userlarimni postlarni ichdan korganlarimni ajratadi
                Q(post_id__in=posts) & Q(user=request.user)
            ).values('post_id')

            post_views = [unseen['post_id'] for unseen in post_views]

            unseen_posts_ids = [  # follow qilgan userlarimni postlarni ichdan kormaganlarimni ajratadi
                post_id for post_id in list(posts) if post_id not in list(post_views)
            ]

            unseen_posts = Post.objects.filter(id__in=unseen_posts_ids,
                                               is_draft=False)  # is_draft=False bolsa mainga chiqadi

            from_time = timezone.now() - datetime.timedelta(days=7)
            now_time = timezone.now()

            posts_7_days = Post.objects.filter(created_date__gte=from_time,
                                               created_date__lte=now_time).order_by('-views_count')[:20]

            queryset = chain(unseen_posts, posts_7_days)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):  # views larni sanaydi retrive get qilib 1 ta id ni oladi
        instance = self.get_object()
        instance.views_count += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class FollowingViews(APIView):

    def get(self, request):
        following = Following.objects.filter(user=request.user)  # men follow qilgan odamlar
        serializer = FollowingSerializer(following, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FollowersViews(APIView):  # menga follow qilgan odam lar

    def get(self, request):
        following = Following.objects.filter(following=request.user)  # men follow qilgan odamlar
        serializer = FollowersSerializer(following, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FollowingCounts(APIView):
    def get(self, request):
        following = Following.objects.filter(user=request.user).aggregate(Count('id'))
        followers = Following.objects.filter(following=request.user).aggregate(Count('id'))

        result = {
            'following_count': following['id__count'],  # ['id__count'] yozmasak {} ichda {} qaytadi
            'followers_count': followers['id__count']
        }

        return Response(result)


class LikesViews(APIView):
    @swagger_auto_schema(request_body=LikeSerializer)
    def post(self, request):
        serializers = LikeSerializer(data=request.data)
        if serializers.is_valid():
            like = serializers.save()  # likelani beradi
            # TODO optimize with celery task
            post = like.post  # postlani beradi
            post.like_count += 1
            post.save()
            return Response(serializers.data, status=status.HTTP_201_CREATED)

        else:
            return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=LikeDeleteSerializer)
    def delete(self, request):
        like = Like.objects.get(id=request.data['like_id'])
        like.delete()
        # TODO optimize with celery task
        post = like.post
        post.like_count -= 1
        post.save()
        return Response(
            {'message': 'deleted successfully'}, status=status.HTTP_200_OK
        )


class UserSavedPostsAPIView(APIView):
    def get(self, request, user_id):
        try:
            user = MyUser.objects.get(id=user_id)
        except MyUser.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        categories = Category.objects.all()
        response_data = []

        for category in categories:
            saved_posts_count = SavedPost.objects.filter(user=user, post__category=category).count()
            posts = Post.objects.filter(category=category, savedpost__user=user)

            category_data = {
                "category": category.name,
                "saved_posts_count": saved_posts_count,
                "posts": PostSerializer(posts, many=True).data
            }
            response_data.append(category_data)

        serializer = UserSavedPostsSerializer({
            'user_id': user_id,
            'categories': response_data
        })
        return Response(serializer.data)
# option(variant)

# option 1 : is first user get post by category last added
# option 2 : most views (3) by category and daily
# option 3 : from following users
# option 4 : by view count -> weekly count --> daily count
# option 5 : recently
# option 6 : by likes
