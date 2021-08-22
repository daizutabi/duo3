from __future__ import annotations

import csv
import os
from dataclasses import dataclass

from duo3.common import ROOT

PATH = os.path.join(ROOT, "history.csv")


@dataclass
class History:
    history: dict[int, str]

    def append(self, no: int, deduction: int):
        deduction = min(deduction, 9)
        self.history[no] = self.history.get(no, "D") + str(deduction)

    def get(self, *args):
        return self.history.get(*args)

    def get_by_list(self, no: int) -> list[int]:
        if history := self.get(no):
            return [int(x) for x in history[1:]]
        else:
            return []

    def is_wrong(self, no: int) -> bool:
        if history := self.get_by_list(no):
            return history[-1] != 0
        else:
            return True

    def save(self):
        save(self.history)


def read() -> History:
    history: dict[int, str] = {}
    if not os.path.exists(PATH):
        return History(history)

    with open(PATH, "r", encoding="utf8") as file:
        reader = csv.reader(file)
        for no, data in reader:
            history[int(no)] = data
    return History(history)


def save(history: dict[int, str]):
    with open(PATH, "w", encoding="utf8") as file:
        writer = csv.writer(file, lineterminator="\n")
        for line in history.items():
            writer.writerow(line)
