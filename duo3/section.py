from __future__ import annotations

import random
from collections.abc import Iterator

from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.togglebutton import ToggleButton


class SectionSelector(GridLayout):
    def __init__(self, height=90, **kwargs):
        super().__init__(size_hint_y=None, height=height, **kwargs)
        self.cols = 16
        for s in range(48):
            if s % 16 == 0:
                button = self.control_button(s // 16)
            else:
                text = str(s - (s // 16))
                button = ToggleButton(
                    text=text,
                    size_hint_y=None,
                    height=height // 3,
                    font_name="Times",
                    font_size=20,
                )
            self.add_widget(button)

    def control_button(self, index: int) -> Button:
        text = ["Clear", "All", "Random"][index]
        on_release = [self.clear, self.all, self.random][index]
        size = (80, self.height // 3)
        button = Button(
            text=text,
            size_hint=(None, None),
            size=size,
            font_name="Times",
            font_size=20,
        )
        button.on_release = on_release
        return button

    def sectioniter(self) -> Iterator[ToggleButton]:
        for button in self.children:
            if isinstance(button, ToggleButton):
                yield button

    @property
    def sections(self) -> list[int]:
        sections = []
        for button in self.sectioniter():
            if button.state == "down":
                sections.append(int(button.text))
        sections.sort()
        return sections

    def clear(self):
        for button in self.sectioniter():
            button.state = "normal"

    def all(self):
        for button in self.sectioniter():
            button.state = "down"

    def random(self):
        n = len(self.sections)
        if n == 0 or n == 45:
            n = 1
        self.clear()
        sections = random.sample(range(1, 46), n)
        for button in self.sectioniter():
            if int(button.text) in sections:
                button.state = "down"
