from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.uix.label import Label


class MusicWindow(App):
    def build(self):
        music = SoundLoader.load("dictation/audio/DUO3/DUO_001.mp3")

        # check the exisitence of the music
        if music:
            music.play()

        return Label(text="Music is playing")


if __name__ == "__main__":
    window = MusicWindow()
    window.run()
