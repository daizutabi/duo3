from __future__ import annotations

from kivy.app import App
from kivy.core.audio import Sound
from kivy.core.text import DEFAULT_FONT, LabelBase
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.resources import resource_add_path
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar

import duo3.audio
import duo3.history
import duo3.sentence
from duo3.sentence import Sentence
from duo3.uix import SectionSelector, SentenceSelector

resource_add_path(r"C:\\WIndows\\Fonts")
LabelBase.register(DEFAULT_FONT, "meiryo.ttc")

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
        self.display(self.sentence, history, False)
        self.bar.max = len(sentences)
        self.bar.value = current + 1
        self.flush()

    def finish(self):
        self.japanese.text = ""
        self.english.text = "Finished."
        self.english.color = "33FF77"

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

    def color(self, deduction: int | None = None):
        if deduction is None:
            deduction = self.sentence.deduction if self.sentence else 0
        return ["EEEEEE", "DDDD22", "DD8833", "DD3333"][min(deduction, 3)]

    def display(self, sentence: Sentence, history: list[int], english: bool = False):
        self.section.text = f"Section {sentence.section}"
        self.no.text = f"No. {sentence.no}"
        if history:
            last = history[-1]
            correct = sum(1 for x in history if x == 0)
            self.past.text = f"Past {correct}/{len(history)}"
            self.previous.text = f"Previous {last}"
            if last == 0:
                self.previous.color = "33ff77"
            else:
                self.previous.color = self.color(last)
        else:
            self.past.text = "Past 0/0"
            self.previous.text = "Previous -"
            self.previous.color = self.color(0)
        if english:
            self.english.text = sentence.english
            self.english.color = "EEEEEE"
        self.japanese.text = sentence.japanese
        self.audio = duo3.audio.read(sentence.no)
        self.play()

    def clear(self):
        self.section.text = "Section 0"
        self.no.text = "No. 0"
        self.past.text = "Past 0/0"
        self.previous.text = "Previous -"
        self.previous.color = self.color(0)
        self.english.text = ""
        self.japanese.text = ""
        self.unload()


class Duo3Widget(BoxLayout):
    section_selector: SectionSelector = ObjectProperty(None)
    sentence_selector: SentenceSelector = ObjectProperty(None)
    sentence_layout: SentenceLayout = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sentences = duo3.sentence.read()
        self.history = duo3.history.read()
        self.problems: list[Sentence] = []
        self.current: int = 0
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        for button in self.section_selector:
            button.bind(state=self.section_changed)
        for button in self.sentence_selector:
            button.bind(state=self.sentence_changed)
        self.update_section_selector()

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        key = keycode[1]
        if key == "escape" and self.problems:
            self.finish()
        elif key == "enter":
            self.sentence_selector.unselect()
            if sections := self.section_selector.sections:
                self.problems = self.sentences.sample(sections)
                if ps := [p for p in self.problems if self.history.is_wrong(p.no)]:
                    self.problems = ps
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
                    self.finish()
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

    def finish(self):
        self.sentence_layout.finish()
        duo3.audio.finish2.seek(0)
        duo3.audio.finish2.play()
        self.update_section_selector()
        if self.problems:
            self.update_sentence_selector(self.problems[0].section)
        self.problems.clear()

    def section_changed(self, button, value):
        if value == "down":
            self.update_sentence_selector(int(button.text))
        elif value == "normal":
            self.sentence_selector.clear()

    def sentence_changed(self, button, value):
        if value == "down" and button.text:
            no = int(button.text)
            history = self.history.get_by_list(no)
            self.sentence_layout.display(self.sentences[no - 1], history, True)
        elif value == "normal":
            self.sentence_layout.clear()

    def update_section_selector(self):
        for button in self.section_selector:
            no = int(button.text)
            count = sum(self.history.is_wrong(i) for i in self.sentences.noiter(no))
            if count == 0:
                button.color = "33FF77"
            else:
                button.color = "EEEEEE"

    def update_sentence_selector(self, section: int):
        nos = sorted(self.sentences.noiter(section))
        cs: list[str] = []
        for no in nos:
            if self.history.is_wrong(no):
                cs.append("EEEEEE")
            else:
                cs.append("33FF77")
        self.sentence_selector.set_sentence_numbers(nos, cs)


class Duo3App(App):
    def build(self):
        return Duo3Widget()


def main():
    Duo3App().run()
