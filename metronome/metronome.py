from kivy.config import Config

Config.set("kivy", "kivy_clock", "free_all")

from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image

from kivy.properties import (
    ObjectProperty,
    NumericProperty,
    DictProperty,
    BooleanProperty,
)
from kivy.uix.floatlayout import FloatLayout
from kivymd.uix.behaviors import CircularRippleBehavior

from metronome.helpers import PlaySound, Spotify, threaded
import functools


class PlayButton(CircularRippleBehavior, ButtonBehavior, Image):
    """
    A play button for the metronome.

    Also plays the beeps according to the bpm.

    Attributes
    ----------
    icon: str
        A path to the icon image.
    sound: PlaySound
        An interface for playing the beep of the metronome.
    clock_event: kivy.event
        The clock event for timing the beeps according to the bpm (default None).
    is_playing: Bool
        The current status of the button (play/pause).

    Methods
    -------
    on_press
        Play the button if it's paused, and pause if it's playing.
    on_bpm_change
        Define behavior for bpm change.
    """

    bpm = NumericProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.ripple_scale = 1
        self.source = "metronome/resources/play-button.png"
        self.sound = PlaySound("metronome/resources/click.wav")
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
        self.source = "metronome/resources/pause-button.png"
        self.clock_event = Clock.schedule_interval_free(self._play_sound, 60 / self.bpm)
        self.is_playing = True

    def _stop(self):
        """Handle everything needed for changing the button state to pause."""
        self.source = "metronome/resources/play-button.png"
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
    search_feedback: ObjectProperty
        The search feedback to be displayed to the user.
    bpm_input: ObjectProperty
        The input/display box for the bpm.
    bpm: NumericProperty
        Beats per minute to be played in the metronome.
    max_bpm: int
        Maximum bpm for slider.
    min_bpm: int
        Minimum bpm for slider.
    metadata: DictProperty
        The current song's metadata.
    show_metadata: BooleanProperty
        hide metadata BoxLayout when there's no metadata.
    """

    sp = Spotify()
    song_input = ObjectProperty(None)
    artist_input = ObjectProperty(None)
    search_feedback = ObjectProperty(None)
    bpm_input = ObjectProperty(None)

    bpm = NumericProperty(120)
    max_bpm = 240
    min_bpm = 20
    metadata = DictProperty(
        dict.fromkeys(
            ["name", "artists", "tempo", "time_signature", "duration", "key"],
            "",
        )
    )
    show_metadata = BooleanProperty(False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Decorate on_search with threading and handling search info
        self.on_search = threaded(self._display_search_info(self.on_search))

        self.bpm_input.bind(text=self.validate_bpm_input)

    def on_search(self):
        """Attempt to get song metadata from text and act accordingly.

        Is binded to the search button's on_press method.
        Gets metadata based on the text input and returns results accordingly.

        Returns
        -------
        int
            An error code - 0 for success, 1 for invalid search input,
            2 for no results and 3 for no config.cfg file.
        """
        if not self.sp.config_exists:
            return 3
    
        song, artist = self.song_input.text, self.artist_input.text

        # Only allow non-empty searches
        if not song:
            return 1
        song, artist = song.strip(), artist.strip()

        metadata = self.sp.get_song_metadata(song, artist)
        if metadata is None:
            return 2

        # No errors
        self.bpm = metadata["tempo"]
        self.metadata = metadata
        self.show_metadata = True
        return 0

    def validate_bpm_input(self, instance, value):
        """Check that the input is within the limits before applying it."""

        bpm_input = self.bpm_input.text
        # Ignore if empty
        if not bpm_input:
            return
        
        bpm_input = int(bpm_input)
        if self.min_bpm <= bpm_input <= self.max_bpm:
            self.bpm = bpm_input

    def _display_search_info(self, func):
        """Wrap on_search to output search info to user based on results."""
        functools.wraps(func)

        def wrapper():
            err_code = func()

            # Succesful search
            if err_code == 0:
                self.search_feedback.text = "Success!"
                self.search_feedback.theme_text_color = "Custom"
                self.search_feedback.text_color = (0, 0.8, 0.4)  # Green
                return err_code

            # Errors
            self.search_feedback.theme_text_color = "Error"
            if err_code == 1:
                self.search_feedback.text = "Please specify a song name."
            elif err_code == 2:
                self.search_feedback.text = (
                    "Couldn't find any results.\nMaybe try modifiyng your search?"
                )
            elif err_code == 3:
                self.search_feedback.text = (
                    "No config.cfg file.\nMake a new file and re-run the program"
                )
            return err_code

        return wrapper


class MetronomeApp(MDApp):
    def build(self):
        return MainLayout()


if __name__ == "__main__":
    MetronomeApp().run()
