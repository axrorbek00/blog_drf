from django.urls import path
from .views import (
    CategoryViewSet,
    PostViewSet,
    FollowingViews,
    FollowersViews,
    FollowingCounts,
    LikesViews,
    UserSavedPostsAPIView
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'Post', PostViewSet)
router.register(r'Category', CategoryViewSet)

urlpatterns = [
    # path('categories/', CategoryViewSet.as_view()),
    path('following/users/', FollowingViews.as_view()),
    path('followers/users/', FollowersViews.as_view()),
    path('followingCounts/users/', FollowingCounts.as_view()),
    path('likes/', LikesViews.as_view()),
    path('saved_post/<int:user_id>/', UserSavedPostsAPIView.as_view()),
]
urlpatterns += router.urls
