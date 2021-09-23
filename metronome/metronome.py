from kivy.config import Config

Config.set("kivy", "kivy_clock", "free_all")

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.clock import Clock

from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty, NumericProperty, DictProperty
from kivymd.uix.button import MDIconButton

from metronome.helpers import PlaySound, Spotify


# For having a rough idea of what it would look like on android
Window.size = (450, 600)


class PlayButton(MDIconButton):
    """
    A play button for the metronome.

    Also plays the beeps according to the bpm.

    Attributes
    ----------
    icon: str
        a path to the icon image
    sound: PlaySound
        an interface for playing the beep of the metronome
    clock_event: kivy.event
        the clock event for timing the beeps according to the bpm (default None)
    is_playing: Bool
        The current status of the button (play/pause)

    Methods
    -------
    on_press
        Play the button if it's paused, and pause if it's playing.
    on_bpm_change
        Defines behavior for bpm change.
    """

    bpm = NumericProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.icon = "resources/play-button.png"
        self.sound = PlaySound("click.wav")
        self.clock_event = None
        self.is_playing = False
        self.bind(bpm=self.on_bpm_change)

    def on_press(self):
        """Play the button if it's paused, and pause if it's playing."""
        if not self.is_playing:
            self._play()
        elif self.is_playing:
            self._stop()

    def on_bpm_change(self, instance, value):
        """Define behavior for bpm change."""
        if self.is_playing:
            # Reset and play
            self.clock_event.cancel()
            self._play()

    def _play(self):
        """Handle everything needed for changing the button state to play."""
        self.icon = "resources/pause-button.png"
        self.clock_event = Clock.schedule_interval_free(self._play_sound, 60 / self.bpm)
        self.is_playing = True

    def _stop(self):
        """Handle everything needed for changing the button state to pause."""
        self.icon = "resources/play-button.png"
        self.clock_event.cancel()
        self.is_playing = False

    def _play_sound(self, dt):
        self.sound.play()


class MainLayout(FloatLayout):
    """
    Main layout, has attributes and methods that are used by child widgets.

    Attributes
    ----------
    sp: Spotify
        A spotify API client with song search method.
    song_input: ObjectProperty
        The text from the 'song - artist' text field.
    bpm: NumericProperty
        Beats per minute to be played in the metronome.
    max_bpm: int
        Maximum bpm for slider.
    min_bpm: int
        Minimum bpm for slider.
    metadata: DictProperty
        The current song's metadata.
    """

    sp = Spotify()
    song_input = ObjectProperty(None)
    artist_input = ObjectProperty(None)
    bpm = NumericProperty(120)
    max_bpm = 240
    min_bpm = 20
    metadata = DictProperty(
        dict.fromkeys(
            ["name", "artists", "tempo", "time_signature", "duration", "mode", "key"],
            "",
        )
    )

    def on_search(self):
        """Attempt to get song metadata from text and act accordingly.

        Is binded to the search button's on_press method.
        Gets metadata based on the text input and returns results accordingly.
        """
        song, artist = self.song_input.text, self.artist_input.text
        
        # Only allow non-empty searches for now
        if not song or not artist:
            return
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


if __name__ == "__main__":
    MetronomeApp().run()
