from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.config import Config
from kivy.graphics import Color, Rectangle
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
# from jnius import autoclass
from itertools import cycle
import random
import sqlite3

Window.size = (350, 350 * 16 / 9)

width, height = Window.size

size_x = 0.05
size_y = 0.04
image_x = 0.43
image_y = 0.43 / 16 * 9
alphabet = list(map(chr, list(range(1040, 1072)))) + ['Ё']

# MediaPlayer = autoclass('android.media.MediaPlayer')


class Mixer:
    on = True
    right = SoundLoader.load('data/right.mp3')
    click = SoundLoader.load('data/click.mp3')
    click.volume = 0.1
    # right = MediaPlayer()
    # right.setDataSource('data/right.mp3')
    # click = MediaPlayer()
    # click.setDataSource('data/click.mp3')
    # right.prepare()
    # click.prepare()

    @staticmethod
    def play_right():
        Mixer.right.play()

    @staticmethod
    def play_click():
        Mixer.click.play()

    @staticmethod
    def turn_off():
        Mixer.right.volume = 0
        Mixer.click.volume = 0

    @staticmethod
    def turn_on():
        Mixer.right.volume = 1
        Mixer.click.volume = .1


class LiterButton(Button):  # Буковка
    def __init__(self, self_x, self_y, liter):
        super().__init__(text=liter,
                         pos_hint={"x": self_x, "y": self_y},
                         size_hint=(size_x, size_y),
                         background_color=[0, .3, 0.025, 1],
                         background_normal='',
                         background_down='')
        self.x_ = self_x
        self.y_ = self_y
        self.clicked = False
        self.cage = None
        self.letter = liter
        self.working = True


class EmptyCage(Button):  # Пустая клеточка
    def __init__(self, x, y, num):
        super().__init__(pos_hint={'x': x, 'y': y},
                         size_hint=(size_x, size_y),
                         background_color=(.5, .5, .5, 1),
                         background_normal='',
                         background_down='')
        self.x_ = x
        self.y_ = y
        self.filled = False
        self.let = None
        self.num = num

    def alpha_zero(self):
        self.background_color = (0, 0, 0, 0)


class SettingsButton(Button):
    def __init__(self):
        super(SettingsButton, self).__init__(size_hint=(0.15, 0.15 / height * width),
                                             pos_hint={'x': 0.0005, 'y': 0.915},
                                             background_normal='data/sound.png',
                                             background_down='data/sound.png')
        self.images = cycle(['data/no_sound.png', 'data/sound.png'])

    def change_image(self, instance):
        new_image = next(self.images)
        self.background_normal = new_image
        self.background_down = new_image
        if Mixer.on:
            Mixer.turn_off()
        else:
            Mixer.turn_on()
        Mixer.on = not Mixer.on


class HelpButton(Button):
    def __init__(self):
        super().__init__(pos_hint={'x': 0.01, 'y': 0.95},
                         size_hint=(size_x, size_y),
                         background_color=(0, .5, 0, 1),
                         text='?',
                         background_normal='')
        self.working = True


class ImageBorder(Widget):
    def __init__(self, pos_x, pos_y):
        super(ImageBorder, self).__init__(pos_hint={'x': pos_x, 'y': pos_y},
                                          size_hint=(0.45, .45 / 16 * 9))
        with self.canvas.before:
            Color(.1, .1, .1, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)


class HintDialog(FloatLayout):
    def __init__(self, game):
        super().__init__(size_hint=(.67, .25),
                         pos_hint={'x': .17, 'y': .33})
        self.canvas.before.clear()
        with self.canvas.before:
            Color(.1, .1, .1, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)

        self.game = game
        self.add_widget(Label(text='Вы действительно хотите\nпотратить [color=fafa00]60[/color] монет,\nчтобы получить подсказку?',
                              pos_hint={'x': 0.4, 'y': 0.6},
                              size_hint=(0.2, 0.2),
                              halign='center',
                              valign='center',
                              font_size='15sp',
                              markup=True))

        self.add_widget(Button(text='Да',
                               background_color=(0, 0.75, 0.2, 1),
                               size_hint=(0.2, 0.2),
                               pos_hint={'x': 0.1, 'y': 0.1},
                               on_press=self.callback)),

        self.add_widget(Button(text='Нет',
                               background_color=(0, 0.75, 0.2, 1),
                               size_hint=(0.2, 0.2),
                               pos_hint={'x': 0.7, 'y': 0.1},
                               on_press=self.callback))

    def callback(self, instance):
        Mixer.play_click()
        if instance.text == 'Да':
            self.game.hint()
        self.game.remove_widget(self)


class MainMenu(FloatLayout):
    def __init__(self):
        super(MainMenu, self).__init__(pos_hint={'x': 0, 'y': 0})
        self.add_settings()
        self.add_label()
        self.add_button()
        self.add_emblem()

    def add_settings(self):
        a = SettingsButton()
        a.bind(on_press=a.change_image)
        self.add_widget(a)

    def add_emblem(self):
        self.add_widget(Image(source='data/fml.png',
                              size_hint=(.1, .1)))
        self.add_widget(Label(text='МАОУ "Лицей №131"',
                              font_size='17sp',
                              pos_hint={'x': 0.2, 'y': 0},
                              size_hint=(.4, .1)))

    def add_label(self):
        self.add_widget(Label(font_name='data/9772.otf',
                              text='[color=109810]4 фото\n       1 слово[/color]',
                              pos_hint={'x': 0.01, 'y': 0.6},
                              size_hint=(1, 0.2),
                              markup=True,
                              font_size='50sp'))
        self.add_widget(Image(source='data/sign.png',
                              size_hint=(0.23, 0.23),
                              pos_hint={'x': 0.115, 'y': 0.517}))

    def add_button(self):
        self.add_widget(Button(text='Играть',
                               size_hint=(0.4, 0.1),
                               pos_hint={'x': 0.3, 'y': 0.3},
                               background_color=(.06, 1, .06, 1),
                               on_press=self.play_callback))

    def play_callback(self, instance):
        Mixer.play_click()
        self.parent.start_game()

    def settings_callback(self, instance):
        Mixer.play_click()
        self.parent.open_settings()


class Game(FloatLayout):
    def __init__(self):
        super(Game, self).__init__(pos_hint={'x': 1, 'y': 0})
        self.help_button = HelpButton()
        self.help_button.bind(on_press=self.help_callback)
        self.add_widget(self.help_button)
        self.cages = []
        self.letters = []
        self.new_word()
        self.get_score()

    def get_score(self):
        try:
            self.remove_widget(self.score_label)
        except AttributeError:
            pass
        con = sqlite3.connect('content.sqlite3')
        cur = con.cursor()
        self.score = cur.execute("""SELECT money FROM stats""").fetchone()[0]
        self.score_label = Label(text=str(self.score),
                                 pos_hint={'x': 0.89, 'y': 0.95},
                                 size_hint=(0.03, 0.03))
        self.add_widget(self.score_label)
        self.add_widget(Image(source='data/coin.png',
                              allow_stretch=True,
                              keep_ratio=False,
                              size_hint=(0.03, 0.03 / 16 * 9),
                              pos_hint={'x': 0.95, 'y': 0.9555}))

    def pay(self):
        con = sqlite3.connect('content.sqlite3')
        cur = con.cursor()
        self.score -= 60
        cur.execute("""UPDATE stats
        SET money = ?""", (self.score,))
        con.commit()
        con.close()
        self.get_score()

    def new_word(self):  # Новое слово
        self.cages = []
        self.letters = []
        con = sqlite3.connect('content.sqlite3')
        cur = con.cursor()
        word = cur.execute("""SELECT id, answer FROM levels
        WHERE done = 0 ORDER BY id""").fetchone()
        try:  # Этот блок описывает действия, если все уровни пройдены
            self.word = word[1]
        except TypeError:  # Его нужно будет изменить
            cur.execute("""UPDATE levels
            SET done = 0""")
            con.commit()
            word = cur.execute("""SELECT id, answer FROM levels
                    WHERE done = 0 ORDER BY id""").fetchone()
        finally:
            self.word = word[1]
        con.close()

        self.add_image_borders()
        self.add_images(word)
        self.new_empty_cages()
        self.add_letters()

    def new_empty_cages(self):
        self.cage_coords = []
        a = len(self.word)
        for i in range(a):
            space = 0.01
            big_space = (1 - a * size_x - (a - 1) * space) / 2
            if self.word[i] != ' ':
                cage = EmptyCage(big_space + i * (size_x + space), 0.3, i)
                self.cages.append(cage)
                self.add_widget(cage)

    def add_letters(self):
        b = 11
        new_letters = random.choices(population=alphabet, k=b * 2)

        let_nums = list(range(2 * b))
        for i in range(len(self.word)):
            if self.word[i] == ' ':
                continue
            a = random.choice(let_nums)
            new_letters[a] = self.word[i]
            let_nums.remove(a)

        space_1 = (1 - b * size_x) / (b + 1)
        for i in range(b):
            a = LiterButton((i + 1) * space_1 + i * size_x, 0.2, new_letters[i])
            a.bind(on_press=self.callback)
            self.add_widget(a)
            self.letters.append(a)
        for i in range(b):
            a = LiterButton((i + 1) * space_1 + i * size_x, 0.1, new_letters[i + b])
            a.bind(on_press=self.callback)
            self.add_widget(a)
            self.letters.append(a)

    def add_images(self, word):
        pass
        self.add_widget(Image(source=f'data/{self.word}/1.png',
                              pos_hint={'x': 0.05, 'y': 0.655},
                              size_hint=(image_x, image_y)))
        self.add_widget(Image(source=f'data/{self.word}/2.png',
                              pos_hint={'x': 0.52, 'y': 0.655},
                              size_hint=(image_x, image_y)))
        self.add_widget(Image(source=f'data/{self.word}/3.png',
                              pos_hint={'x': 0.05, 'y': 0.355},
                              size_hint=(image_x, image_y)))
        self.add_widget(Image(source=f'data/{self.word}/4.png',
                              pos_hint={'x': .52, 'y': 0.355},
                              size_hint=(image_x, image_y)))
        self.lvl_label = Label(text=f'[color=109810][b]lvl {word[0]}[/b][/color]',
                               pos_hint={'x': 0.35, 'y': 0.8},
                               size_hint=(0.3, 0.3),
                               font_size='30sp',
                               markup=True)
        self.add_widget(self.lvl_label)

    def add_image_borders(self):
        for i in [(.04, .35), (.04, .65), (.51, .35), (.51, .65)]:
            a = ImageBorder(*i)
            a.bind(size=self._update_rect, pos=self._update_rect)
            self.add_widget(a)

    def callback(self, instance):
        Mixer.play_click()
        if not instance.working:
            return
        if not instance.clicked:
            for i in self.cages:
                if not i.filled:
                    instance.pos_hint = {'x': i.x_, 'y': i.y_}
                    i.filled = True
                    instance.clicked = True
                    instance.cage = i
                    i.let = instance
                    break
        else:
            instance.pos_hint = {'x': instance.x_, 'y': instance.y_}
            instance.cage.filled = False
            instance.cage.let = None
            instance.cage = None
            instance.clicked = False

        self.check_win()

    def help_callback(self, instance):
        Mixer.play_click()
        if not instance.working:
            return
        if self.score < 60:
            return
        dialog = HintDialog(self)
        dialog.bind(pos=self._update_rect, size=self._update_rect)
        self.add_widget(dialog)

    def hint(self):
        self.pay()
        possible = list(filter(lambda x: not x.filled, self.cages))
        try:
            chosen = random.choice(possible)
        except IndexError:
            for i in self.cages:
                if not i.let.working:
                    continue
                if i.let.letter != self.word[i.num]:
                    self.callback(i.let)
                    break
        else:
            done = False
            liter = ''.join(self.word.split())[chosen.num]
            for i in self.letters:
                if i.clicked:
                    continue
                if i.text == liter:
                    i.pos_hint = {'x': chosen.x_, 'y': chosen.y_}
                    i.working = False
                    i.background_color = (0, 0.15, 0, 1)
                    chosen.alpha_zero()
                    self.remove_widget(chosen)
                    i.clicked = True
                    i.cage = chosen
                    i.cage.filled = True
                    i.cage.let = i
                    done = True
                    break
            if not done:
                for i in self.cages:
                    if not i.let.working:
                        continue
                    if i.let.letter != self.word[i.num]:
                        self.callback(i.let)
                        break

            self.check_win()

    def check_win(self):
        cur_word = ''
        for i in self.cages:
            try:
                a = i.let.letter
                cur_word += a
            except AttributeError:
                break
        if cur_word == ''.join(self.word.split()):
            for i in self.letters:
                i.working = False
            self.help_button.working = False
            Clock.schedule_once(self.win, 1)

    def win(self, dt):
        for i in self.cages:
            self.remove_widget(i)
        for i in self.letters:
            self.remove_widget(i)
        self.remove_widget(self.lvl_label)
        con = sqlite3.connect('content.sqlite3')
        cur = con.cursor()
        cur.execute(f"""UPDATE levels
        SET done = 1
        WHERE answer = ?""", (self.word,))
        self.score += 50
        cur.execute("""UPDATE stats
        SET money = ?""", (self.score,))
        con.commit()
        con.close()
        Mixer.play_right()
        self.new_word()
        self.help_button.working = True
        self.get_score()

    def _update_rect(self, instance, value):
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size


class Root(FloatLayout):
    def __init__(self):
        super().__init__()
        self.add_widget(Image(source='data/background1.png',
                              keep_ratio=False,
                              allow_stretch=True,
                              size_hint=(1, 1)))
        self.game = Game()
        self.menu = MainMenu()
        self.start()

        self.timer = 0

    def start(self):
        self.add_widget(self.menu)
        self.add_widget(self.game)

    def start_game(self):
        try:
            self.event.cancel()
        except AttributeError:
            pass
        self.event = Clock.schedule_interval(self.play_callback, 1 / 60)
        Window.bind(on_keyboard=self.back_button_previous)
        Config.set('kivy', 'exit_on_escape', 0)

    def end_game(self):
        try:
            self.event.cancel()
        except AttributeError:
            pass
        self.event = Clock.schedule_interval(self.previous_callback, 1 / 60)

    def play_callback(self, dt):
        if self.timer <= -0.48:
            self.event.cancel()
        self.game.pos_hint['x'] -= 1 / 30
        self.menu.pos_hint['x'] -= 1 / 30
        self.timer -= 1 / 60
        self.remove_widget(self.game)
        self.add_widget(self.game)
        self.remove_widget(self.menu)
        self.add_widget(self.menu)

    def previous_callback(self, dt):
        if self.timer >= -0.02:
            self.event.cancel()
            Config.set('kivy', 'exit_on_escape', 1)
        self.game.pos_hint['x'] += 1 / 30
        self.menu.pos_hint['x'] += 1 / 30
        self.timer += 1 / 60
        self.remove_widget(self.game)
        self.add_widget(self.game)
        self.remove_widget(self.menu)
        self.add_widget(self.menu)

    def back_button_previous(self, window, key, *args):
        if key == 27:
            self.end_game()


class MyApp(App):  # Приложение
    def build(self):
        return Root()


if __name__ == '__main__':
    MyApp().run()
