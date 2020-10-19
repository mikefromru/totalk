from .models import Topic, Question
from django.contrib import admin

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):

    pass

@admin.register(Question)
class TopicAdmin(admin.ModelAdmin):

    search_fields = ('topic__topic', 'name')
    # search_fields = ('topic__slug', 'name')

