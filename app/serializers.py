from rest_framework import serializers
from . models import Topic, Question


class TopicSerializer(serializers.ModelSerializer):

    class Meta:

        model = Topic
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):

    topic = TopicSerializer()

    class Meta:
        model = Question
        fields = '__all__'

