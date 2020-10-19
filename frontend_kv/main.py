import kivy
from kivymd.app import MDApp

from kivy.storage.jsonstore import JsonStore

import requests
import random
import time
import os

if os.path.exists('config.json'):
    store = JsonStore('config.json')
else:
    store = JsonStore('config.json')
    store.put('data', name='User', questions=5, seconds=10)

    # questions
    store.put('five_questions', number=5, active_questions=True)
    store.put('seven_questions', number=7, active_questions=False)
    store.put('ten_questions', number=10, active_questions=False)
    # minutes
    store.put('one_minute', number=60, active_seconds=False)
    store.put('two_minute', number=120, active_seconds=True)

from kivy.lang import Builder

kivy.require('1.11.1')

from kivy.clock import Clock
from kivy.properties import (
     NumericProperty,
     StringProperty,
     ObjectProperty,
     BooleanProperty
)

from kivy.utils import platform
from kivy.utils import rgba
# uix
from kivymd.uix.card import MDCard
from kivymd.uix.button import (
    MDRaisedButton,
    MDIconButton
)
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineAvatarIconListItem
from kivy.uix.screenmanager import Screen, ScreenManager

from kivy.core.audio import SoundLoader
from pydub import AudioSegment
from pydub.playback import play


# check OS
# It is one of: ‘win’, ‘linux’, ‘android’, ‘macosx’, ‘ios’ or ‘unknown’
if platform == 'android':
    domain = 'http://pythonanywere.com'
    root = Builder.load_file('templates/android_index.kv')
else:
    domain = 'http://localhost:8000'
    from kivy.core.window import Window
    Window.size = (600, 853)
    root = Builder.load_file('templates/desktop_index.kv')


class WindowManager(ScreenManager):

    pass

class TopicCard(MDCard):

    id = NumericProperty()
    topic = StringProperty()
    favorite_id = []
    favorite_topic = BooleanProperty()
    s = []

    def __init__(self, **kwargs):
        super(TopicCard, self).__init__(**kwargs)

        # print('< ', self.favorite_topic, self.topic, ' >')
        if os.path.exists('favorite.json'):
            if self.favorite_topic == True:
                # print('< ', self.favorite_topic, self.topic, ' >')
                self.iconButton = MDIconButton(
                    id='stars',
                    icon='star',
                    theme_text_color='Custom',
                    text_color=rgba('#E91E63')
                )
                self.iconButton.text_color = rgba('#E91E63')
            else:
                self.iconButton = MDIconButton(
                    id='stars',
                    icon='star',
                    theme_text_color='Custom',
                    text_color=rgba('#000000')
                )

        else:
            self.iconButton = MDIconButton(
                id='stars',
                icon='star',
                theme_text_color='Custom',
                text_color=rgba('#000000')
            )

        self.add_widget(self.iconButton)
        self.iconButton.bind(on_release=lambda x:self.favorite(self.id, self.topic))

    def favorite(self, id, topic):
        store = JsonStore('favorite.json')
        for x in store:
            self.s.append(store.get(x).get('id'))

        if id in self.s:
            try:
                store.delete(topic)
                self.iconButton.text_color = rgba('#000000')
                print('Removed')
                if len(store) == 0:
                    os.remove('favorite.json')
                    MDApp.get_running_app().root.ids.main.ids.main_star.text_color = 0, 0, 0, 0
                    print('<<<< File was removed >>>')

            except KeyError as keyerr:
                print('>>>>> Error <<<<<: ', keyerr)
                store.put(topic, id=id)
                self.iconButton.text_color = rgba('#E91E63')
                MDApp.get_running_app().root.ids.main.ids.main_star.text_color = 1, 1, 1, 1

            except FileNotFoundError as fileerr:
                print('<<< Error>>> : ', fileerr)
        else:
            store.put(topic, id=id)
            self.iconButton.text_color = rgba('#E91E63')
            print('Added to favorite')
            if len(store) == 1:
                MDApp.get_running_app().root.ids.main.ids.main_star.text_color = 1,1,1,1

        self.s = []


class ItemConfirmSeconds(OneLineAvatarIconListItem):

    store = JsonStore('config.json')

    divider = None
    name = StringProperty()
    source = NumericProperty()
    active_seconds = BooleanProperty(False)

    def set_icon(self, instance_check):
        # change text in SettingsScreen class
        secondsToMinutes = divmod(self.source, 60)[0]
        MDApp.get_running_app().root.ids.mySettings.ids.user_seconds.text = str(secondsToMinutes)[0]
        s = []  # list of key from config file
        # find in store for changing from False to True
        for key, entry in self.store.find(number=self.source):
            entry['active_seconds'] = True
            self.store[key] = entry
            for x in self.store:
                if x != key and x != 'data':
                    s.append(x)
        # set active=False others
        for x in s:
            entry = self.store.get(x)
            entry['active_seconds'] = False
            self.store[x] = entry

        check_list = instance_check.get_widgets(instance_check.group)
        for check in check_list:
            if check != instance_check:
                check.active = False

        self.parent.parent.parent.parent.dismiss()

class ItemConfirmQuestions(OneLineAvatarIconListItem):

    store = JsonStore('config.json')

    five = store.get('five_questions')
    seven = store.get('seven_questions')
    ten = store.get('ten_questions')

    divider = None
    name = StringProperty()
    source = NumericProperty()
    active_questions = BooleanProperty(False)

    def set_icon(self, instance_check):
        # change text in SettingsScreen class
        MDApp.get_running_app().root.ids.mySettings.ids.user_questions.text = str(self.source)
        s = []  # list of key from config file
        # find in store for changing from False to True
        for key, entry in self.store.find(number=self.source):
            entry['active_questions'] = True
            self.store[key] = entry
            for x in self.store:
                if x != key and x != 'data':
                    s.append(x)
        # set active=False others
        for x in s:
            entry = self.store.get(x)
            entry['active_questions'] = False
            self.store[x] = entry

        check_list = instance_check.get_widgets(instance_check.group)
        for check in check_list:
            if check != instance_check:
                check.active = False

        self.parent.parent.parent.parent.dismiss()

class SettingsScreen(Screen):

    store = JsonStore('config.json')
    dialog_questions = None
    dialog_seconds = None

    for key, entry in store.find(active_seconds=True):
        # conver second to minutes
        seconds = divmod(store.get(key).get('number'), 60)[0]

    for key, entry in store.find(active_questions=True):
        questions = store.get(key).get('number')

    five = store.get('five_questions').get('active_questions')
    seven = store.get('seven_questions').get('active_questions')
    ten = store.get('ten_questions').get('active_questions')

    one_minute = store.get('one_minute').get('active_seconds')
    two_minute = store.get('two_minute').get('active_seconds')

    def seconds_change(self):
        if not self.dialog_seconds:
            self.dialog_seconds = MDDialog(
                title="Change minutes",
                type="confirmation",
                items=[
                    ItemConfirmSeconds(source=60, text="1 minute", active_seconds=self.one_minute),
                    ItemConfirmSeconds(source=120, text="2 minutes", active_seconds=self.two_minute),
                ],
            )
        self.dialog_seconds.open()

    def questions_change(self):
        if not self.dialog_questions:
            self.dialog_questions = MDDialog(
                title="Change minutes",
                type="confirmation",
                items=[
                    ItemConfirmQuestions(source=5, text="5 questions", active_questions=self.five),
                    ItemConfirmQuestions(source=7, text="7 questions", active_questions=self.seven),
                    ItemConfirmQuestions(source=10, text="10 questions", active_questions=self.ten),
                ],
            )
        self.dialog_questions.open()

class FavoriteScreen(Screen):

    def on_enter(self, *args):
        store = JsonStore('favorite.json')
        list_id = []
        for x in store:
            list_id.append(str(store.get(x).get('id')))
        ids = ','.join(list_id)
        data = {'data': ids}
        url = domain + '/app/favorite/'
        r = requests.get(url, data=data)

        try:
            r.raise_for_status()
            topics = r.json()
            for x in topics:
                card = TopicCard(id=x.get('id'), topic=x.get('topic'))
                self.ids.box.add_widget(card)

        except requests.exceptions.HTTPError as err:
            print('Error: ', err)

    def on_leave(self, *args):
        self.ids.box.clear_widgets()

class DoneScreen(Screen):

    pass

class TalkingScreen(Screen):

    name_topic = StringProperty()
    questions = ObjectProperty()
    question = StringProperty()

    count = NumericProperty()
    pass_q = NumericProperty(1) # pass question
    pause_ = False

    def __init__(self, **kwargs):
        super(TalkingScreen, self).__init__(**kwargs)

    def speed_change(self, sound_, speed=1.0):
        sound_with_altered_frame_rate = sound_._spawn(sound_.raw_data, overrides={
            "frame_rate": int(sound_.frame_rate * speed)
        })
        return sound_with_altered_frame_rate.set_frame_rate(sound_.frame_rate)

    def sound_play(self, i):
        check = None
        try:
            url = domain + '/app/play-sound/'
            r = requests.get(url, data={'data': self.questions[0]['sound'], 'topic': self.name_topic})
        except:
            pass

        # check Response by content
        if len(r.content) > 8:
            f = open('music.ogg', 'wb')
            f.write(r.content)
            f.close()
            check = True

        if check:
            sound = SoundLoader.load('music.ogg')
            sound.play()
            # if platform == 'android':
            #     do something
            #
            # else:
            #     sound = AudioSegment.from_file('music.wav', format='wav')
            #     slower = self.speed_change(sound, 0.95)
            #     play(slower)

    def pause(self):
        if self.pause_ == False:
            self.even_2.cancel()
            self.pause_ = True
            print(self.pause_)
        else:
            self.even_2()
            self.pause_ = False
            print(self.pause_)

    def start(self):
        self.even_2()

    def timer(self, i):
        store = JsonStore('config.json')

        tmp_1 = self.count
        tmp_2 = time.gmtime(tmp_1)

        self.ids.count.text = time.strftime('%M:%S', tmp_2)
        for key, entry in store.find(active_questions=True):
            len_questions = store.get(key).get('number')

        if self.count == 0:
            self.pass_q += 1
            self.ids.text_button.text = '{}/{}'.format(self.pass_q, len_questions)
            try:
                self.questions.pop(0)
                Clock.schedule_once(self.sound_play, 1)
                store = JsonStore('config.json')

                for key, entry in store.find(active_seconds=True):
                    self.count = store.get(key).get('number')

                self.question = self.questions[0].get('name')

                # self.sound_play(self)


            except IndexError as err:
                print('IndexError: ', err)
                self.even_2.cancel()
                self.manager.current = 'done'


        self.count -= 1

    def on_enter(self, *args):

        self.name_topic = self.questions[0].get('topic').get('topic')
        Clock.schedule_once(self.sound_play, 1)

        store = JsonStore('config.json')

        self.ids.text_button.text = '{}/{}'.format(self.pass_q, len(self.questions))

        for key, entry in store.find(active_seconds=True):
            self.count = store.get(key).get('number')

        self.question = self.questions[0].get('name')
        self.even_2 = Clock.schedule_interval(self.timer, 1)


        for key, entry in store.find(active_seconds=True):
            self.count = store.get(key).get('number')
            tmp_2 = time.gmtime(self.count)
            self.ids.count.text = time.strftime('%M:%S', tmp_2)

        # self.sound_play(self)

    def on_leave(self, *args):
        self.even_2.cancel()
        store = JsonStore('config.json')

        for key, entry in store.find(active_seconds=True):
            tmp_1 = store.get(key).get('number')
            tmp_2 = time.gmtime(tmp_1)
            self.ids.count.text = time.strftime('%M:%S', tmp_2)

        self.count = tmp_1
        self.pass_q = 1
        self.ids.text_button.text = '{}/{}'.format(self.pass_q, len(self.questions))

    def go_to_home(self):
        self.manager.current = 'main'

class Detail(Screen):

    def __init__(self, **kwargs):
        super(Detail, self).__init__(**kwargs)

    def on_enter(self, *args):
        store = JsonStore('config.json')
        id_topic = self.ids.id_topic.text
        url = domain + '/app/detail/' + id_topic
        r = requests.get(url)
        try:
            r.raise_for_status()
            data = r.json()

            # get some random questions from JSON
            for key, entry in store.find(active_questions=True):
                count_questions = store.get(key).get('number')
            try:
                questions = random.sample(data, count_questions)
            except ValueError as err:
                questions = data
            TalkingScreen.questions = questions # pass Objects to TalkingScreen class
            i = 1
            for x in questions:
                q = str(i) + '. ' + x.get('name') + ' ?'
                label = MDLabel(text=q)
                self.ids.box.add_widget(label)
                i += 1

            btn = MDRaisedButton(text='Start', pos_hint={'center_x': 0.5} )
            self.ids.my_btn.add_widget(btn)
            btn.bind(on_press=self.go_to_talking)

        except requests.exceptions.HTTPError as err:
            print('Http error: ', err)

    def on_leave(self, *args):
        self.ids.box.clear_widgets()
        self.ids.my_btn.clear_widgets()

    def go_to_talking(self, instance):
        self.manager.current = 'talking'

class Main(Screen):

    page = NumericProperty(1)
    get_ids = None

    def __init__(self, **kwargs):
        super(Main, self).__init__(**kwargs)
        Clock.schedule_once(self.create_cards)

    def on_pre_enter(self, *args):
        if self.get_ids != None:
            self.create_cards(self)

    def create_cards(self, i):
        self.get_ids = self.ids.box
        store = JsonStore('favorite.json')
        if len(store) > 0:
            self.ids.main_star.text_color = 1,1,1,1
        else:
            self.ids.main_star.text_color = 0,0,0,0

        url = domain + '/app/?page={}'.format(str(self.page))
        r = requests.get(url)
        try:
            r.raise_for_status()
            data = r.json()
            if os.path.exists('favorite.json'):
                favorites = []
                for x in store:
                    favorites.append(store.get(x))
                modData = data['results']
                for d in modData:
                    for f in favorites:
                        if d['id'] == f['id']:
                            d['favorite'] = True
                            break
                        else:
                            d['favorite'] = False
                for x in modData:
                    card = TopicCard(id=x.get('id'), topic=x.get('topic'), favorite_topic=x.get('favorite'))
                    self.ids.box.add_widget(card)
            else:
                for x in data['results']:
                    card = TopicCard(id=x.get('id'), topic=x.get('topic'), favorite_topic=False)
                    self.ids.box.add_widget(card)

        except requests.exceptions.HTTPError as err:
            self.page = 1
            self.go_to_start(self)
            print('Http error: ', err)

    def go_to_start(self, instance):
        self.ids.box.clear_widgets()
        self.page = 1
        self.create_cards(self)


    def previous(self, instance):
        self.ids.box.clear_widgets()
        self.page -= instance
        self.create_cards(self)
        self.ids.my_scrollview.scroll_y = 1 # start from top

    def next(self, instance):
        self.ids.box.clear_widgets()
        self.page += instance
        self.create_cards(self)
        self.ids.my_scrollview.scroll_y = 1 # start from top

    def on_leave(self, *args):
        self.ids.box.clear_widgets()

class App(MDApp):

    def build(self):
        # self.root = Builder.load_file('index.kv')
        self.window_manager = WindowManager()
        return self.window_manager

if __name__ == '__main__':
    App().run()
