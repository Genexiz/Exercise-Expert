from kivy.app import App
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, Rectangle

Window.size = (Window.width, Window.height)



class SplashScreen(App):
    def build(self):
        layout = FloatLayout(size_hint=(1, 1))
        Window.maximize()
        self.icon = '1.png'
        with layout.canvas.before:
            Color(*get_color_from_hex('EFEFE4'))
            self.rect = Rectangle(size=layout.size, pos=layout.pos)

        image = Image(source='1.png', size_hint=(0.8, 0.8), pos_hint={'center_x': 0.5, 'center_y': 0.9}, color=(1, 1, 1, 0))
        label = Image(source='Ds.png', size_hint=(0.8, 0.8), pos_hint={'center_x': 0.5, 'center_y': 0.35}, color=(1, 1, 1, 0))

        Clock.schedule_once(lambda dt: self.add_wid(layout=layout, image=image, label=label), 3)
        Clock.schedule_once(lambda dt: self.schedule_start_splash(label, image), 2)

        return layout

    def add_wid(self, layout, image, label):
        layout.add_widget(image)
        layout.add_widget(label)
        self.tada = Clock.schedule_interval(lambda dt: self.increase_splash(label, image), 0.01)

    def increase_splash(self, label, image):
        label.color[3] += 0.01
        image.color[3] += 0.01
        if label.color[3] >= 1 or image.color[3] >= 1:
            self.tada.cancel()

    def schedule_start_splash(self, label, image):
        Clock.schedule_once(lambda dt: self.start_splash(label, image), 5)

    def start_splash(self, label, image):
        self.tran = Clock.schedule_interval(lambda dt: self.dismiss_splash(label, image), 0.01)

    def dismiss_splash(self, label, image):
        label.color[3] -= 0.01
        image.color[3] -= 0.01
        if label.color[3] <= 0 or image.color[3] <= 0:
            self.tran.cancel()
            self.root_window.remove_widget(label)
            self.root_window.remove_widget(image)
            self.stop()

    def on_start(self):
        Window.clearcolor = get_color_from_hex('EFEFE4')
        self.title = 'ExerciseExpert'

    def on_stop(self):
        Window.clearcolor = (1, 1, 1, 1)


if __name__ == '__main__':
    SplashScreen().run()
