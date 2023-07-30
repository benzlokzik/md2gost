from docx.shared import Length


class LayoutTracker:
    def __init__(self, max_height: Length):
        self._max_height: Length = max_height
        self._current_height: Length = Length(0)

    @property
    def current_page_height(self):
        return self._current_height % self._max_height

    @property
    def _remaining_page_height(self) -> Length:
        return self._max_height - self.current_page_height

    @property
    def page(self):
        return self._current_height // self._max_height

    def add_height(self, height: Length):
        self._current_height += height

    def can_fit_to_page(self, height: Length):
        return height <= self._remaining_page_height

    def new_page(self):
        self._current_height += self._remaining_page_height
