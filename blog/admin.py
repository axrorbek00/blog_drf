from django.contrib import admin
from .models import Post, PostViews, Following, Comment, Like, Category, SavedPost

# Register your models here.


admin.site.register(Post)
admin.site.register(PostViews)
admin.site.register(Following)
admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(Category)
admin.site.register(SavedPost)
