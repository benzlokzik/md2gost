from collections.abc import Generator
from abc import ABC, abstractmethod

from docx.shared import Length

from ..layout_tracker import LayoutState
from ..rendered_info import RenderedInfo


class Renderable(ABC):
    @abstractmethod
    def render(self, previous_rendered: RenderedInfo, layout_state: LayoutState) -> Generator[RenderedInfo, None, None]:
        """Renders the object to one or multiple Parented objects"""
