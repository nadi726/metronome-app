import spotipy
import configparser
from spotipy.oauth2 import SpotifyClientCredentials
from kivy.utils import platform


class Spotify(spotipy.Spotify):
    """A spotipy API client based on the spotipy client."""

    def __init__(self):

        # Get spotify client credentials
        config = configparser.ConfigParser()
        config.read("metronome/config.cfg")
        client_id = config.get("SPOTIFY", "CLIENT_ID")
        client_secret = config.get("SPOTIFY", "CLIENT_SECRET")

        super().__init__(
            auth_manager=SpotifyClientCredentials(
                client_id=client_id, client_secret=client_secret
            )
        )

    def get_song_metadata(self, song, artists):
        """
        Get all relevant song metadata from the spotify API.

        Parameters
        ----------
        song : str
            The name of the song
        artists : str
            The names of the artists

        Returns
        -------
        Optional(dict)
            The song's metadata, None on failure to fetch metadata.
        """
        song, artists = self._change_to_valid_names(song, artists)
        results = self.search(
            q=f'track:"{song}" artist:"{artists}"', type="track", limit=10
        )["tracks"]["items"]
        if not results:
            return None

        # For debugging purposes(maybe replace with logging)
        print("Search results:")
        for song in results:
            print(f"song: {song['name']}. artists: {self._get_artists(song)}")

        song_id = results[0]["id"]
        song = self.track(song_id)

        # Get relevant metadata
        song_metadata = {"name": song["name"], "artists": self._get_artists(song)}
        audio_analysis = self._get_relevant_audio_analysis(song_id)

        # Merge song and artists names with the rest of the metadata
        song_metadata = {**song_metadata, **audio_analysis}
        self._format_metadata(song_metadata)

        return song_metadata

    def _change_to_valid_names(self, song, artist):
        """Change provided song and artist names to the names in the spotify API.

        Some naming conventions of names in the spotify API are a bit
        different from the names we usually call them.
        For example, 'The Eagles' are simply referred to by 'eagles',
        and searching for 'The eagles' provides no results.
        This function is responsible for finding those instances and replacing them
        with the names that the spotify API knows.
        Currently only a few songs have been found,
        so there's no need to create an external file.

        Parameters
        ----------
        song : str
            The name of the song, as provided by get_song_matadata.
        artists : str
            The names of the artists, as provided by get_song_matadata.

        Returns
        -------
        song : str
            The song name provided, modified as needed(if at all).
        artist : str
            The artists names provided, modified as needed(if at all).
        """
        song, artist = song.lower().strip(), artist.lower().strip()
        if song == "i'm yours" and artists == "jason mraz":
            return "im yours", artist
        elif artist == "the eagles":
            return song, "eagles"

        # No match
        else:
            return song, artist

    def _get_artists(self, song):
        """Get a list of artists names from dict."""
        return [artist["name"] for artist in song["artists"]]

    def _get_relevant_audio_analysis(self, song_id):
        """Extract relevant info from audio analysis."""
        full_analysis = self.audio_analysis(song_id)["track"]
        fields = ("tempo", "time_signature", "duration", "mode", "key")
        analysis = {i: full_analysis[i] for i in fields}
        return analysis

    def _format_metadata(self, metadata):
        """Format metadata to a human-readable format."""
        # Convert duration from seconds to mm:ss
        m, s = divmod(int(metadata["duration"]), 60)
        metadata["duration"] = f"{m:02d}:{s:02d}"

        # convert key to letters
        keys = "C C#/Db D D#/Eb E F F#/Gb G G#/Ab A A#/Bb B".split()
        modes = ["minor", "major"]
        key_index = metadata["key"]
        # Formatting examples: A major, D#/Eb minor
        metadata["key"] = f"{keys[key_index]} {modes[metadata['mode']]}"
        # Redundant after formatting
        metadata.pop("mode")


class PlaySound:
    """
    An interface to playing sound.

    Serves as a wrapper to both pygame.mixer and the audio interface in pynjius,
    and uses the appropiate one according to the OS.

    Parameters
    ----------
    soundfile: str
        a path to the sound file

    Attributes
    ----------
    sound: pygame.mixer.Sound / jnius.autoclass
        the sound interface being wrapped by this class
    """

    def __init__(self, soundfile):
        # Use pygame's mixer on platforms other than android
        if platform != "android":
            from pygame import mixer

            mixer.pre_init(44100, -16, 2, 256)
            mixer.init()
            self.sound = mixer.Sound("metronome/resources/click.wav")

        # On android use pyjnius
        # Solution by Jonathan De: stackoverflow.com/questions/56325453/kivy-play-sound-on-android-without-delay
        else:
            from jnius import autoclass

            MediaPlayer = autoclass("android.media.MediaPlayer")
            self.sound = mPlayer_norm = MediaPlayer()
            mPlayer_norm.setDataSource(soundfile)
            mPlayer_norm.prepare()

    def play(self):
        self.sound.play()


if __name__ == "__main__":
    sp = Spotify()
    while True:
        query = input("song name - artist name: ")
        song, artist = query.split("-")
        song, artist = song.strip(), artist.strip()
        print(sp.get_song_metadata(song, artist))
