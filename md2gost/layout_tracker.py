from docx.shared import Length


class LayoutState:
    def __init__(self, max_height: Length, max_width: Length):
        self._max_height: Length = max_height
        self._max_width: Length = max_width
        self._current_height: Length = Length(0)

    @property
    def max_height(self):
        return self._max_height

    @property
    def max_width(self):
        return self._max_width

    @property
    def current_page_height(self):
        return self._current_height % self._max_height

    @property
    def _remaining_page_height(self) -> Length:
        return self._max_height - self.current_page_height

    @property
    def page(self):
        return self._current_height // self._max_height + 1


class LayoutTracker:
    def __init__(self, max_height: Length, max_width: Length):
        self._state = LayoutState(max_height, max_width)

    @property
    def current_state(self):
        return self._state

    def add_height(self, height: Length):
        self._state._current_height += height

    def can_fit_to_page(self, height: Length):
        return height <= self._state._remaining_page_height

    def new_page(self):
        self._state._current_height += self._state._remaining_page_height
