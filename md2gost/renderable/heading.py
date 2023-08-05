from copy import copy
from typing import Generator

from docx.shared import Parented

from .break_ import Break
from ..layout_tracker import LayoutState
from .paragraph import Paragraph
from ..rendered_info import RenderedInfo


class Heading(Paragraph):
    def __init__(self, parent: Parented, level: int):
        super().__init__(parent)

        self._parent = parent
        self._level = level

        if not 1 <= level <= 9:
            raise ValueError("Heading level must be in range from 1 to 9")

        self.style = f"Heading {level}"

    def render(self, previous_rendered: RenderedInfo, layout_state: LayoutState) -> Generator[RenderedInfo, None, None]:
        if self._level == 1 and layout_state.page != 1:
            yield from Break(self._parent).render(previous_rendered, copy(layout_state))

        yield from super().render(previous_rendered, layout_state)
