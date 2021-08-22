from __future__ import annotations

import japanize_kivy  # noqa
from kivy.app import App
from kivy.core.audio import Sound
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar

import duo3.audio
import duo3.history
import duo3.sentence
from duo3.sentence import Sentence
from duo3.uix import SectionSelector

Window.size = (960, 880)


class SentenceLayout(BoxLayout):
    step: Label = ObjectProperty(None)
    section: Label = ObjectProperty(None)
    no: Label = ObjectProperty(None)
    past: Label = ObjectProperty(None)
    previous: Label = ObjectProperty(None)
    bar: ProgressBar = ObjectProperty(None)
    deduction: Label = ObjectProperty(None)
    japanese: Label = ObjectProperty(None)
    english: Label = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sentence: Sentence | None = None
        self.audio: Sound | None = None

    def start(self, sentences: list[Sentence], current: int, history: list[int]):
        self.step.text = f"Step {current+1}/{len(sentences)}"
        self.sentence = sentences[current]
        self.section.text = f"Section {self.sentence.section}"
        self.no.text = f"No. {self.sentence.no}"
        if history:
            correct = sum(1 for x in history if x == 0)
            self.past.text = f"Past {correct}/{len(history)}"
            self.previous.text = f"Previous {history[-1]}"
            if history[-1] == 0:
                self.previous.color = "33ff77"
            else:
                self.previous.color = self.color(history[-1])
        else:
            self.past.text = "Past 0/0"
            self.previous.text = "Previous -"
            self.previous.color = self.color(0)

        self.bar.max = len(sentences)
        self.bar.value = current + 1
        self.japanese.text = self.sentence.japanese + " " + self.sentence.english
        self.audio = duo3.audio.read(self.sentence.no)
        self.play()
        self.flush()

    def play(self):
        if self.audio:
            self.audio.seek(0)
            self.audio.play()

    def unload(self):
        if self.audio:
            self.audio.unload()

    def flush(self):
        self.english.text = self.sentence.prompt()
        if self.sentence.is_finished():
            if self.sentence.deduction == 0:
                self.english.color = "33FF77"
            else:
                self.english.color = self.color()
        else:
            self.english.color = "EEEEEE"
        self.deduction.text = f"Deduction {self.sentence.deduction}"
        self.deduction.color = self.color()

    def finish(self):
        self.japanese.text = ""
        self.english.text = "Finished."
        self.english.color = "33FF77"

    def color(self, deduction: int | None = None):
        if deduction is None:
            deduction = self.sentence.deduction if self.sentence else 0
        return ["EEEEEE", "DDDD22", "DD8833", "DD3333"][min(deduction, 3)]


class Duo3Widget(BoxLayout):
    section_selector: SectionSelector = ObjectProperty(None)
    sentence_layout: SentenceLayout = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sentences = duo3.sentence.read()
        self.history = duo3.history.read()
        self.problems: list[Sentence] = []
        self.current: int = 0
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        key = keycode[1]
        if key == "enter":
            if sections := self.section_selector.sections:
                self.problems = self.sentences.sample(sections)
                self.current = 0
                self.start()
        elif key == "spacebar":
            self.sentence_layout.play()
        elif self.problems:
            problem = self.problems[self.current]
            if problem.is_finished():
                self.sentence_layout.unload()
                self.current += 1
                if self.current == len(self.problems):
                    self.sentence_layout.finish()
                    self.problems.clear()
                else:
                    self.start()
            else:
                if not problem.input(key) or key == "tab":
                    duo3.audio.ng.seek(0)
                    duo3.audio.ng.play()
                if problem.is_finished():
                    self.history.append(problem.no, problem.deduction)
                    self.history.save()
                self.sentence_layout.flush()
        return True

    def start(self):
        problem = self.problems[self.current]
        history = self.history.get_by_list(problem.no)
        self.sentence_layout.start(self.problems, self.current, history)


class Duo3App(App):
    def build(self):
        return Duo3Widget()


def main():
    Duo3App().run()
