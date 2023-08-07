from django.contrib import admin
from .models import Post, Comment


# admin.site.register(Post)
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'author', 'publish', 'status']
    list_filter = ['status','created', 'author', 'publish']
    search_fields = ['title', 'body']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['author']
    date_hierarchy = 'publish'
    ordering = ['status', 'publish']
    list_editable = ['status']


# Django administration site that the model is registered in the site using a custom 
# class that inherits from ModelAdmin. In this class, we can include information about how to display 
# the model on the site and how to interact with it.
# The list_display attribute allows you to set the fields of your model that you want to display on the 
# administration object list page

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'post', 'created', 'active']
    list_filter = ['active', 'created', 'updated']
    search_fields = ['name', 'email', 'body']