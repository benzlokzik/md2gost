from collections import defaultdict


class Numberer:
    def __init__(self):
        self._categories: dict[str, int] = defaultdict(lambda: 0)

    def get_current_number(self, category) -> int:
        return self._categories[category]

    def save_number(self, category, number):
        self._categories[category] = number
