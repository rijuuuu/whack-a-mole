import random
import time
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import AsyncImage, Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.uix.button import Button
from kivy.uix.popup import Popup

Window.size = (360, 640)

# Clickable image with index
class ClickableImage(ButtonBehavior, Image):
    def __init__(self, index, app, **kwargs):
        super().__init__(**kwargs)
        self.index = index
        self.app = app
        self.images = {
            "green": 'Images/blank.png',
            "red": 'Images/hit.png',
            "blue": 'Images/mole.png'
        }
        self.source = self.images["green"]
        self.clicked = False

    def on_press(self):
        #print(f"Image at index {self.index} clicked")
        if self.source == self.images["blue"]:
            self.source = self.images["red"]
            self.clicked = True
            self.app.points_value += 1
            self.app.points.text = f"Points: {self.app.points_value}"
            
            # Play sound on hit
            sound = SoundLoader.load('Sounds/hit.mp3')
            if sound:
                sound.play()
                sound.volume = 0.5
            
            if self.app.points_value % 5 == 0:
                self.app.counter += 5  # Add bonus time
            
            def reset_after_click(dt):
                self.source = self.images["green"]
                self.clicked = False
                
            Clock.schedule_once(reset_after_click, 1)
            
            
class MyApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.image_buttons = [] 
        self.points_value = 0
        
    def play_bgm(self):
        self.bgm = SoundLoader.load('Sounds/bgm.mp3')
        if self.bgm:
            self.bgm.loop = True
            self.bgm.play()
            self.bgm.volume = 0.6
            
    def restart_game(self, instance):
        if hasattr(self, 'game_over_popup'):
            self.game_over_popup.dismiss()
        if hasattr(self, 'bgm') and self.bgm:
            self.bgm.stop()
        self.points_value = 0
        self.counter = 15
        self.label.text = f"{self.counter}"
        self.points.text = f"Points: {self.points_value}"
        for img in self.image_buttons:
            img.source = img.images["green"]
            img.clicked = False

        # Unschedule any previous timer before starting a new one
        Clock.unschedule(self.update_timer)
        self.play_bgm()
        Clock.schedule_interval(self.update_timer, 1)
        
    def exit_game(self, instance):
        if hasattr(self, 'bgm') and self.bgm:
            self.bgm.stop()
        App.get_running_app().stop()
        Window.close()

    #Game over page
    def game_over(self):      
        if hasattr(self, 'bgm') and self.bgm:
            self.bgm.stop()
        Clock.unschedule(self.update_timer)
        
        layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
               
        label = Label(
            text=f"Time's Up!\nYour Score: {self.points_value}",
            font_name="Font/Bitcount.ttf",
            font_size=24,
            color=(1, 1, 1, 1)
        )   
        
        layout.add_widget(label)
        
        retry = Button(
            background_normal='Images/green.jpg',
            text="Play Again :)",
            font_name="Font/Bitcount.ttf",
            font_size=20
        )
        retry.bind(on_press=self.restart_game)
        
        exit = Button(
            background_normal='Images/red.jpg',
            text="Exit :(",
            font_name="Font/Bitcount.ttf",
            font_size=20
        )
        exit.bind(on_press=self.exit_game)
        
        layout.add_widget(retry)
        layout.add_widget(exit)
        
        self.game_over_popup = Popup(
            title="",
            content=layout,
            size_hint=(0.8, 0.5),
            auto_dismiss=False
        )
        
        self.game_over_popup.open()
    
    # Functions required
    def update_timer(self, dt):
        if self.counter > 0:
            self.mole_appear()
            self.counter -= 1
            self.label.text = f"{self.counter}"
        else:
            sound = SoundLoader.load('Sounds/yeah.mp3')
            if sound:
                sound.play()
                sound.volume = 0.5
                sound.loop = True
            self.game_over()

    def mole_appear(self):
        idx = random.randint(0, 24)
        mole = self.image_buttons[idx]
        mole.source = mole.images["blue"]
        mole.clicked = False  # Reset the click state

        def reset_image(dt):
            if not mole.clicked:
                mole.source = mole.images["green"]              

        Clock.schedule_once(reset_image, 1)

    # Screen 
    def build(self):
        root = FloatLayout()
        
        # Background image
        bg_image = AsyncImage(
            source='Images/grassField.png',
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1)
        )
        root.add_widget(bg_image)

        # Main content
        content = BoxLayout(
            orientation='vertical',
            spacing=10,
            padding=10,
            size_hint=(1, None),
            height=540,
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )

        # Top bar with icon, timer, points
        top_bar = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=50,
            spacing=10
        )

        # Icon
        self.icon_img = Image(
            source='Images/icon.jpg',
            size_hint=(None, None),
            size=(40, 40)
        )

        # Timer
        self.counter = 15
        self.label = Label(
            text=f"{self.counter}",
            font_size=28,
            font_name="Font/Bitcount.ttf",
            color=(0,0,0,1)
        )
        # Points
        self.points = Label(
            text=f"Points: {self.points_value}",
            font_size=28,
            font_name="Font/Bitcount.ttf",
            color=(0,0,0,1)
        )
        
        Clock.schedule_interval(self.update_timer, 1)

        top_bar.add_widget(self.icon_img)
        top_bar.add_widget(self.label)
        top_bar.add_widget(self.points)

        content.add_widget(top_bar) 

        # Grid of image buttons (5x5)
        grid = GridLayout(
            cols=5,
            spacing=[5, 0],
            padding=5,
            size_hint_y=None,
            height=400
        )

        for i in range(25):
            img = ClickableImage(index=i, app=self)
            grid.add_widget(img)
            self.image_buttons.append(img)  

        #self.mole_appear()
        self.mole_appear()

        content.add_widget(grid)
        root.add_widget(content)

        self.play_bgm() 
        return root

if __name__ == "__main__":
    try:
        MyApp().run()
    except Exception as e:
        print("Error:", e)
