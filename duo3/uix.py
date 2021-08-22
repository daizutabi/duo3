from __future__ import annotations

import random
from collections.abc import Iterator, Sequence

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton


class SectionSelector(GridLayout):
    def __init__(self, height=90, **kwargs):
        super().__init__(size_hint_y=None, height=height, **kwargs)
        self.cols = 16
        for s in range(48):
            if s == 0:
                button = Label(
                    text="Section",
                    size_hint=(None, None),
                    size=(100, self.height // 3),
                    # font_name="Times",
                    font_size=18,
                )
            elif s % 16 == 0:
                button = self.control_button(s // 16 - 1)
            else:
                text = str(s - (s // 16))
                button = ToggleButton(
                    text=text,
                    size_hint_y=None,
                    height=height // 3,
                    # font_name="Times",
                    font_size=18,
                    group="section_group",
                )
            self.add_widget(button)

    def control_button(self, index: int) -> Button:
        text = ["Clear", "Random"][index]
        on_release = [self.clear, self.random][index]
        button = Button(
            text=text,
            size_hint=(None, None),
            size=(100, self.height // 3),
            # font_name="Times",
            font_size=18,
        )
        button.on_release = on_release
        return button

    def __iter__(self) -> Iterator[ToggleButton]:
        for button in self.children:
            if isinstance(button, ToggleButton):
                yield button

    @property
    def sections(self) -> list[int]:
        sections = []
        for button in self:
            if button.state == "down":
                sections.append(int(button.text))
        sections.sort()
        return sections

    def clear(self):
        for button in self:
            if button.state != "normal":
                button.state = "normal"

    def random(self, nos: Sequence[int] | None = None):
        if nos is None:
            nos = range(1, 46)
        self.clear()
        no = random.choice(nos)
        for button in self:
            if int(button.text) == no:
                button.state = "down"
                return


class SentenceSelector(BoxLayout):
    def __init__(self, height=30, **kwargs):
        super().__init__(size_hint_y=None, height=height, **kwargs)
        self.sentences: list[ToggleButton] = []
        label = Label(
            text="Sentence",
            size_hint=(None, None),
            size=(100, self.height),
            # font_name="Times",
            font_size=18,
        )
        self.add_widget(label)
        for s in range(17):
            button = ToggleButton(
                text="",
                size_hint_y=None,
                height=height,
                # font_name="Times",
                font_size=18,
                group="sentence-group",
            )
            self.add_widget(button)
            self.sentences.append(button)

    def __getitem__(self, index: int) -> ToggleButton:
        return self.sentences[index]

    def __len__(self) -> int:
        return len(self.sentences)

    def __iter__(self) -> Iterator[ToggleButton]:
        for button in self.sentences:
            yield button

    def set_sentence_numbers(self, nos: list[int], cs: list[str]):
        self.clear()
        for b, no, c in zip(self, nos, cs):
            b.text = str(no)
            b.color = c

    def unselect(self):
        for button in self:
            button.state = "normal"

    def clear(self):
        for button in self:
            button.text = ""
            button.state = "normal"
