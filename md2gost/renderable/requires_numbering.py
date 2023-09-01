from abc import ABC, abstractmethod


class RequiresNumbering:
    def __init__(self, category):
        self.numbering_category = category

    @abstractmethod
    def set_number(self, number: int):
        pass
