from __future__ import annotations

import csv
import os
import random
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field

import bs4
import requests

from duo3.common import ROOT

URL = "http://hosono.com/duo3.0/section{:02d}.html"
PATH = os.path.join(ROOT, "text.csv")


@dataclass
class Sentence:
    section: int
    no: int
    english: str
    japanese: str
    state: list[int] = field(init=False)
    cursor: int = 0

    def __post_init__(self):
        self.init()

    def init(self):
        self.state = [0] * len(self.english)
        self.cursor = 0
        self.is_finished()

    def prompt(self) -> str:
        text = ""
        for k, s in enumerate(self.state):
            if s <= 0:
                text += "_"
                break
            else:
                text += self.english[k]
        return text

    def is_finished(self) -> bool:
        if self.cursor == len(self.state):
            return True
        c = self.english[self.cursor].lower()
        if "a" <= c <= "z":
            return False
        self.state[self.cursor] = 1
        self.cursor += 1
        return self.is_finished()

    def input(self, key: str) -> bool:
        if key == "tab":
            self.state[self.cursor] = 5
            self.cursor += 1
            return True
        elif self.english[self.cursor].lower() == key:
            self.state[self.cursor] = abs(self.state[self.cursor]) + 1
            self.cursor += 1
            return True
        else:
            self.state[self.cursor] -= 1
            return False

    @property
    def deduction(self) -> int:
        deduction = 0
        for s in self.state:
            if s < 0:
                deduction += abs(s)
            elif s > 1:
                deduction += s - 1
        return deduction


@dataclass
class Sentences:
    sentences: list[Sentence]

    def __iter__(self):
        yield from self.sentences

    def __len__(self):
        return len(self.sentences)

    def __getitem__(self, index: int) -> Sentence:
        return self.sentences[index]

    def sentenceiter(self, section: int | Iterable[int]) -> Iterator[Sentence]:
        sections = [section] if isinstance(section, int) else section
        for sentence in self:
            if sentence.section in sections:
                yield sentence

    def noiter(self, section: int | Iterable[int]) -> Iterator[int]:
        for sentence in self.sentenceiter(section):
            yield sentence.no

    def sample(
        self, section: int | Iterable[int], k: int = 0, shuffle: bool = True
    ) -> list[Sentence]:
        sentences = list(self.sentenceiter(section))
        for sentence in sentences:
            sentence.init()
        if k == 0 or k > len(sentences):
            k = len(sentences)
        if shuffle:
            return random.sample(sentences, k)
        else:
            return sentences[:k]


def parse(section: int) -> Iterator[str]:
    print(f"Getting text of section {section}")
    response = requests.get(URL.format(section))
    response.encoding = response.apparent_encoding
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    for tag in soup.select("p")[1:-1]:
        yield tag.text


def split(text: str) -> tuple[int, str, str]:
    no = text[: text.index(" ")]
    splitted = text.split(no)
    assert len(splitted) == 3
    return int(no), splitted[1].strip(), splitted[2].strip()


def fetch() -> Iterator[tuple[int, int, str, str]]:
    index = 1
    for section in range(1, 46):
        for text in parse(section):
            no, english, japanese = split(text)
            assert no == index
            english = collect_english(english)
            japanese = collect_japanese(japanese)
            yield section, no, english, japanese
            index += 1


def collect_english(text: str) -> str:
    return text


def collect_japanese(text: str) -> str:
    text = text.replace("｡", "。")
    if text[-1] not in ["！", "）", "？", "。", "」"]:
        text += "。"
    return text


def save():
    with open(PATH, "w", encoding="utf8") as file:
        writer = csv.writer(file, lineterminator="\n")
        for line in fetch():
            writer.writerow(line)


def read() -> Sentences:
    if not os.path.exists(PATH):
        save()

    sentences = []
    with open(PATH, "r", encoding="utf8") as file:
        reader = csv.reader(file)
        for section, no, english, japnese in reader:
            sentence = Sentence(int(section), int(no), english, japnese)
            sentences.append(sentence)
    return Sentences(sentences)


if __name__ == "__main__":
    sentences = read()
    for sentence in sentences:
        print(sentence.section, sentence.no, sentence.english[:10])
