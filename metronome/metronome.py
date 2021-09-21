from kivy.config import Config
Config.set("kivy", "kivy_clock", "free_all")

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.clock import Clock

from kivy.core.audio import SoundLoader
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty, NumericProperty, DictProperty
from kivy.core.window import Window
from kivymd.uix.button import MDIconButton

from metronome.helpers import PlaySound, Spotify
"""<div>Icons made by <a href="https://www.freepik.com" title="Freepik">Freepik</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a></div>"""

#Builder.load_file("metronome.kv")
Window.size = (450, 600)


class PlayButton(MDIconButton):
    bpm = NumericProperty(None)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.icon = "resources/play-button.png"
        self.sound = PlaySound("click.wav")
        self.event = None # For clock event
        self.is_playing = False
        self.bind(bpm = self.on_bpm_change)
    
    def on_press(self):
        if not self.is_playing:
            self.play()
        elif self.is_playing:
            self.stop()

    def play(self):
        self.icon = "resources/pause-button.png"
        self.event = Clock.schedule_interval_free(self.play_sound, 60 / self.bpm)
        self.is_playing = True
    
    def stop(self):
        self.icon = "resources/play-button.png"
        self.event.cancel()
        self.is_playing = False

    def on_bpm_change(self, instance, value):
        if self.is_playing:
            # Reset and play
            self.event.cancel()
            self.play()
        
    def play_sound(self, dt):
        self.sound.play()

    
class MainLayout(FloatLayout):
    sp = Spotify()
    song_name = ObjectProperty(None)
    bpm = NumericProperty(120)
    max_bpm = 240
    min_bpm = 20
    metadata = dict.fromkeys(["name", "artists", "tempo",
                     "time_signature", "duration", "mode", "key"], '')
    
    def on_search(self):
        """ Is binded to the search button's on_press method
        Gets metadata based on the text input and returns results accordingly.
        """
        search_text = self.song_name.text
        # Basic validation and reformatting
        if "-" not in search_text:
            return
        song, artist = search_text.split("-")
        song, artist = song.strip(), artist.strip()

        metadata = self.sp.get_song_metadata(song, artist)
        if metadata is None:
            return
        
        self.bpm = round(metadata["tempo"])
        self.metadata = metadata
        print("Song metadata:\n" + str(self.metadata))
         
 
class MetronomeApp(MDApp):

    def build(self):
        return MainLayout()


if __name__ == '__main__':
    MetronomeApp().run()
