from .models import Category, Post, Comment, ReplyComment, Like, CommentLike, SavedPost, Following
from rest_framework import serializers


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    views_count = serializers.IntegerField(read_only=True)

    # swagrda post yaratganda (views) korinmaydi, get qiganimizda kornadi

    class Meta:
        model = Post
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class ReplyCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReplyComment
        fields = '__all__'


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'

    def create(self, validated_data):  # 1 postga faqat 1 ta like boswni taminlaydi
        post_id = validated_data['post'].id
        user_id = validated_data['user'].id
        is_liked = Like.objects.filter(post_id=post_id, user_id=user_id).exists()

        if is_liked:
            raise serializers.ValidationError('You already liked this post')

        return super().create(validated_data)


class CommentLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentLike
        fields = '__all__'


class SavedPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedPost
        fields = '__all__'


class FollowingSerializer(serializers.ModelSerializer):  # men follow qilganlar
    id = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()

    def get_id(self, obj):
        return obj.following.id

    def get_first_name(self, obj):
        return obj.following.first_name

    def get_last_name(self, obj):
        return obj.following.last_name

    class Meta:
        model = Following
        fields = ['id', 'first_name', 'last_name']


class FollowersSerializer(serializers.ModelSerializer):  # menga follow qilganlar
    id = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()

    def get_id(self, obj):
        return obj.user.id

    def get_first_name(self, obj):
        return obj.user.first_name

    def get_last_name(self, obj):
        return obj.user.last_name

    class Meta:
        model = Following
        fields = ['id', 'first_name', 'last_name']


class LikeDeleteSerializer(
    serializers.Serializer):  # delitlike un alohda serlizer yozmiz bolmasa kk fildalr qowlib ketadi
    like_id = serializers.IntegerField()


#

class UserSavedPostsCategorySerializer(serializers.Serializer):
    category = serializers.CharField()
    saved_posts_count = serializers.IntegerField()
    posts = PostSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = '__all__'


class UserSavedPostsSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    categories = UserSavedPostsCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = '__all__'
