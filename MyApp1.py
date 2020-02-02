from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.config import Config
from kivy.graphics import Color, Rectangle
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.clock import Clock
import random
import sys
import sqlite3

Config.set('graphics', 'width', 350)  # Не забыть убрать
Config.set('graphics', 'height', 350 * 16 // 9)  # Не забыть убрать

width = Config.getint('graphics', 'width')
height = Config.getint('graphics', 'height')

size_x = 0.05
size_y = 0.04
image_x = 0.4
image_y = 0.17
alphabet = list(map(chr, list(range(1040, 1072)))) + ['Ё']


class LiterButton(Button):  # Буковка
    def __init__(self, self_x, self_y, liter):
        super().__init__(text=liter,
                         pos_hint={"x": self_x, "y": self_y},
                         size_hint=(size_x, size_y),
                         background_color=[0, .5, 0, 1],
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


class HelpButton(Button):
    def __init__(self):
        super().__init__(pos_hint={'x': 0.01, 'y': 0.95},
                         size_hint=(size_x, size_y),
                         background_color=(0, .5, 0, 1),
                         text='?',
                         background_normal='')
        self.working = True


class Game(FloatLayout):
    def __init__(self):
        super(Game, self).__init__()
        self.add_widget(Image(source='data/background.png'))
        self.help_button = HelpButton()
        self.help_button.bind(on_press=self.help_callback)
        self.add_widget(self.help_button)
        self.cages = []
        self.letters = []
        self.new_word()

    def new_word(self):  # Новое слово
        self.cages = []
        self.letters = []
        con = sqlite3.connect('content.sqlite3')
        cur = con.cursor()
        word = cur.execute("""SELECT id, answer FROM levels
        WHERE done = 0""").fetchone()
        try:
            self.word = word[1]
        except TypeError:
            cur.execute("""UPDATE levels
            SET done = 0""")
            con.commit()
            word = cur.execute("""SELECT id, answer FROM levels
                    WHERE done = 0""").fetchone()
        finally:
            self.word = word[1]
        con.close()
        self.add_widget(Image(source=f'data/{self.word}/1.png',
                              pos_hint={'x': 0.05, 'y': 0.7},
                              allow_stretch=True,
                              keep_ratio=False,
                              size_hint=(image_x, image_y)))
        self.add_widget(Image(source=f'data/{self.word}/2.png',
                              pos_hint={'x': 0.95 - image_x, 'y': 0.7},
                              allow_stretch=True,
                              keep_ratio=False,
                              size_hint=(image_x, image_y)))
        self.add_widget(Image(source=f'data/{self.word}/3.png',
                              pos_hint={'x': 0.05, 'y': 0.5},
                              allow_stretch=True,
                              keep_ratio=False,
                              size_hint=(image_x, image_y)))
        self.add_widget(Image(source=f'data/{self.word}/4.png',
                              pos_hint={'x': 0.95 - image_x, 'y': 0.5},
                              allow_stretch=True,
                              keep_ratio=False,
                              size_hint=(image_x, image_y)))
        self.add_widget(Label(text=f'{word[0]}',
                              pos_hint={'x': 0.35, 'y': 0.8},
                              size_hint=(0.3, 0.3),
                              font_size='30sp'))
        self.new_empty_cages()
        self.add_letters()

    def new_empty_cages(self):
        self.cage_coords = []
        a = len(self.word)
        for i in range(a):
            space = 0.01
            big_space = (1 - a * size_x - (a - 1) * space) / 2
            if self.word[i] != ' ':
                cage = EmptyCage(big_space + i * (size_x + space), 0.4, i)
                self.cages.append(cage)
                self.add_widget(EmptyCage(big_space + i * (size_x + space), 0.4, i))

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
            a = LiterButton((i + 1) * space_1 + i * size_x, 0.3, new_letters[i])
            a.bind(on_press=self.callback)
            self.add_widget(a)
            self.letters.append(a)
        for i in range(b):
            a = LiterButton((i + 1) * space_1 + i * size_x, 0.2, new_letters[i + b])
            a.bind(on_press=self.callback)
            self.add_widget(a)
            self.letters.append(a)

    def callback(self, instance):
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
        if not instance.working:
            return
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
                    i.background_color = (0, 0.3, 0, 1)
                    chosen.alpha_zero()
                    self.lay.remove_widget(chosen)
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
        con = sqlite3.connect('content.sqlite3')
        cur = con.cursor()
        cur.execute(f"""UPDATE levels
        SET done = 1
        WHERE answer = ?""", (self.word,))
        con.commit()
        con.close()
        self.new_word()
        self.help_button.working = True


class MyApp(App):  # Приложение
    def build(self):
        self.lay = FloatLayout()  # Корень
        self.lay.add_widget(Image(source='data/background.png'))
        self.help_button = HelpButton()
        self.help_button.bind(on_press=self.help_callback)
        self.lay.add_widget(self.help_button)
        self.cages = []
        self.letters = []
        self.new_word()  # Создаём новое слово
        return self.lay

    def new_word(self):  # Новое слово
        self.cages = []
        self.letters = []
        con = sqlite3.connect('content.sqlite3')
        cur = con.cursor()
        word = cur.execute("""SELECT id, answer FROM levels
        WHERE done = 0""").fetchone()
        try:
            self.word = word[1]
        except TypeError:
            cur.execute("""UPDATE levels
            SET done = 0""")
            con.commit()
            word = cur.execute("""SELECT id, answer FROM levels
                    WHERE done = 0""").fetchone()
        finally:
            self.word = word[1]
        con.close()
        self.lay.add_widget(Image(source=f'data/{self.word}/1.png',
                                  pos_hint={'x': 0.05, 'y': 0.7},
                                  allow_stretch=True,
                                  keep_ratio=False,
                                  size_hint=(image_x, image_y)))
        self.lay.add_widget(Image(source=f'data/{self.word}/2.png',
                                  pos_hint={'x': 0.95 - image_x, 'y': 0.7},
                                  allow_stretch=True,
                                  keep_ratio=False,
                                  size_hint=(image_x, image_y)))
        self.lay.add_widget(Image(source=f'data/{self.word}/3.png',
                                  pos_hint={'x': 0.05, 'y': 0.5},
                                  allow_stretch=True,
                                  keep_ratio=False,
                                  size_hint=(image_x, image_y)))
        self.lay.add_widget(Image(source=f'data/{self.word}/4.png',
                                  pos_hint={'x': 0.95 - image_x, 'y': 0.5},
                                  allow_stretch=True,
                                  keep_ratio=False,
                                  size_hint=(image_x, image_y)))
        self.lay.add_widget(Label(text=f'{word[0]}',
                                  pos_hint={'x': 0.35, 'y': 0.8},
                                  size_hint=(0.3, 0.3),
                                  font_size='30sp'))
        self.new_empty_cages()
        self.add_letters()

    def new_empty_cages(self):
        self.cage_coords = []
        a = len(self.word)
        for i in range(a):
            space = 0.01
            big_space = (1 - a * size_x - (a - 1) * space) / 2
            if self.word[i] != ' ':
                cage = EmptyCage(big_space + i * (size_x + space), 0.4, i)
                self.cages.append(cage)
                self.lay.add_widget(EmptyCage(big_space + i * (size_x + space), 0.4, i))

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
            a = LiterButton((i + 1) * space_1 + i * size_x, 0.3, new_letters[i])
            a.bind(on_press=self.callback)
            self.lay.add_widget(a)
            self.letters.append(a)
        for i in range(b):
            a = LiterButton((i + 1) * space_1 + i * size_x, 0.2, new_letters[i + b])
            a.bind(on_press=self.callback)
            self.lay.add_widget(a)
            self.letters.append(a)

    def callback(self, instance):
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
        if not instance.working:
            return
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
                    i.background_color = (0, 0.3, 0, 1)
                    chosen.alpha_zero()
                    self.lay.remove_widget(chosen)
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
        con = sqlite3.connect('content.sqlite3')
        cur = con.cursor()
        cur.execute(f"""UPDATE levels
        SET done = 1
        WHERE answer = ?""", (self.word,))
        con.commit()
        con.close()
        self.new_word()
        self.help_button.working = True


if __name__ == '__main__':
    MyApp().run()
