import os
from rest_framework.response import Response
from django.http import HttpResponse
from wsgiref.util import FileWrapper

from . models import Topic, Question
from . serializers import TopicSerializer, QuestionSerializer
from rest_framework.pagination import PageNumberPagination

from django.http import Http404

from rest_framework.views import APIView
from rest_framework.generics import ListAPIView

from pydub import AudioSegment
from pydub.playback import play


def speed_change(sound_, speed=1.0):
    sound_with_altered_frame_rate = sound_._spawn(sound_.raw_data, overrides={
        "frame_rate": int(sound_.frame_rate * speed)
    })
    return sound_with_altered_frame_rate.set_frame_rate(sound_.frame_rate)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class PlaySoundView(APIView):

    def get(self, request, *args, **kwargs):
        name_topic = request.data['topic']
        try:
            path_sound = request.data['data']
            if path_sound:
                sound_name = os.path.basename(path_sound)
                name = f'sounds/{name_topic}/{sound_name}'
                short_report = open(name, 'rb')
                response = HttpResponse(FileWrapper(short_report), content_type='application/pdf')
                return response
        except:
            pass

        return Response('PYthon')
    #
    # def get(self, request):
    #     name_topic = request.data['topic']
    #     path_sound = request.data['data']
    #
    #     sound_name = os.path.basename(path_sound)
    #
    #     name = f'sounds/{name_topic}/{sound_name}'
    #
        # sound = AudioSegment.from_file(name, format='wav')
        # slower = speed_change(sound, 0.95)
        # play(slower)

        # return Response('Done')

class FavoriteView(APIView):

    def get(self, request, **kwargs):
        ids = request.data['data'].split(',')
        f = Topic.objects.filter(id__in=ids).all()
        serializer = TopicSerializer(f, many=True)
        return Response(serializer.data)

class TopicView(ListAPIView):

    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    pagination_class = StandardResultsSetPagination

class QuestionView(APIView):

    def get_object(self, pk):
        try:
            return Question.objects.filter(topic__pk=pk).all()
        except Question.DoesNotExists:
            raise Http404

    def get(self, request, pk, format=None):
        queryset = self.get_object(pk)
        serializer = QuestionSerializer(queryset, many=True)
        return Response(serializer.data)

