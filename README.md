# Metronome

Metronome is a cross-platform kivy and kivymd metronome that lets you search for a song's bpm through the spotify API and immediately play it.

# Motivation

I noticed that sometimes when i hear song, i immediately want find out its bpm and see if i can keep up.

This app provides an easier way to do it that googling the bpm and opening a metronome.

# Name

Naming suggestions are welcome, i honestly have no idea what to call this.

# Screenshots

<img src="screenshots/windows.png" width="350" height="300" />
<img src="screenshots/android.jpg" width="200" height="360" />

# Setting up

You need to have spotify client credentials - client id and client secret.

Follow [this guide](https://developer.spotify.com/documentation/general/guides/app-settings/) to get client credentials.

Edit `config.cfg` with your credentials.

Afterwards, follow platform-specific instructions:

## For pc
Install required packages: `pip install -r requirements.txt`

## For android

*Note: the metronome feature might not function correctly*

You have 2 options:
1. Install the apk found in the android folder (might not be the latest version).
2. Build it yourself using buildozer:
    
    *Optional: make a virtual env for building named build*

    install buildozer and dependencies
    
    move buildozer.spec from android folder to main folder
    
    Run  `buildozer android debug deploy` from terminal

# How to use?

Run main.py from the main project folder (the one containing this readme)

# Credits

Spotify API and logo by [Spotify](spotify.com)

Play and pause icons by [Freepik](Freepik.com)

Click sound by [mixit](mixkit.co)
