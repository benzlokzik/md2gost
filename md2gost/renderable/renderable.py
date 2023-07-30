from collections.abc import Generator
from abc import ABC, abstractmethod

from docx.shared import Length

from ..rendered_info import RenderedInfo


class Renderable(ABC):
    @abstractmethod
    def render(self, previous_rendered: RenderedInfo, current_page_height: Length, max_height: Length,
               max_width: Length) -> Generator[RenderedInfo, None, None]:
        """Renders the object to one or multiple Parented objects"""
