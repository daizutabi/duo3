import os

from kivy.core.audio import Sound, SoundLoader

import duo3

ROOT = os.path.join(os.path.dirname(duo3.__file__), "audio")

ok: Sound = SoundLoader.load(os.path.join(ROOT, "ng.mp3"))
ng: Sound = SoundLoader.load(os.path.join(ROOT, "ng.mp3"))


def read(no: int) -> Sound:
    path = os.path.join(ROOT, f"DUO_{no:03d}.mp3")
    return SoundLoader.load(path)
