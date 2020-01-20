from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.config import Config
from kivy.graphics import Color, Rectangle
from kivy.uix.image import Image
import random
import sys

Config.set('graphics', 'width', 350)  # Не забыть убрать
Config.set('graphics', 'height', 350 * 16 // 9)  # Не забыть убрать

width = Config.getint('graphics', 'width')
height = Config.getint('graphics', 'height')

size_x = 0.05
size_y = 0.04
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


class EmptyCage(Button):  # Пустая клеточка
    def __init__(self, x, y, num):
        super().__init__(pos_hint={'x': x, 'y': y},
                         size_hint=(size_x, size_y),
                         background_color=(.1, .1, .1, 1),
                         background_normal='',
                         background_down='')
        self.x_ = x
        self.y_ = y
        self.filled = False
        self.let = None


class MyApp(App):  # Приложение
    def build(self):
        self.lay = FloatLayout()  # Корень
        self.lay.add_widget(Image(source='data/background.png'))
        self.cages = []
        self.new_word()  # Создаём новое слово
        return self.lay

    def new_word(self):  # Новое слово
        self.word = 'крещение руси'.upper()  # Test
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
        for i in range(b):
            a = LiterButton((i + 1) * space_1 + i * size_x, 0.2, new_letters[i + b])
            a.bind(on_press=self.callback)
            self.lay.add_widget(a)

    def callback(self, instance):
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

        cur_word = ''
        for i in self.cages:
            try:
                a = i.let.letter
                cur_word += a
            except AttributeError:
                break
        if cur_word == ''.join(self.word.split()):
            sys.exit('You win')


if __name__ == '__main__':
    MyApp().run()