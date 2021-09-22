import spotipy
import configparser
from spotipy.oauth2 import SpotifyClientCredentials
from kivy.utils import platform


class Spotify(spotipy.Spotify):
    def __init__(self):
        config = configparser.ConfigParser()
        config.read("metronome/config.cfg")
        client_id = config.get("SPOTIFY", "CLIENT_ID")
        client_secret = config.get("SPOTIFY", "CLIENT_SECRET")

        super().__init__(
            auth_manager=SpotifyClientCredentials(
                client_id=client_id, client_secret=client_secret
            )
        )

    def get_song_metadata(self, song, artist):
        # Get song id
        # TODO: make a filtering algorithm for song and artist name
        results = self.search(
            q=f'track:"{song}" artist:"{artist}"', type="track", limit=5
        )["tracks"]["items"]
        if not results:
            return None

        song_id = results[0]["id"]
        song = self.track(song_id)

        # Get Relevant metadata
        artists = [artist["name"] for artist in song["artists"]]
        song_metadata = {"name": song["name"], "artists": artists}

        audio_analysis = self._get_relevant_audio_analysis(song_id)

        # Merge song and artists names with the rest of the metadata
        song_metadata = {**song_metadata, **audio_analysis}
        self._format_metadata(song_metadata)
        return song_metadata

    def _get_relevant_audio_analysis(self, song_id):
        """extract relevant info from audio analysis and format it"""
        full_analysis = self.audio_analysis(song_id)["track"]
        fields = ("tempo", "time_signature", "duration", "mode", "key")
        analysis = {i: full_analysis[i] for i in fields}
        return analysis

    def _format_metadata(self, metadata):
        # Convert duration to minutes:seconds
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
