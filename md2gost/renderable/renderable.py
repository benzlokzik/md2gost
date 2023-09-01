from __future__ import annotations
from collections.abc import Generator
from abc import ABC, abstractmethod

from ..layout_tracker import LayoutState
from ..rendered_info import RenderedInfo


class Renderable(ABC):
    @abstractmethod
    def render(self, previous_rendered: RenderedInfo, layout_state: LayoutState)\
            -> Generator[RenderedInfo | Renderable, None, None]:
        """Renders the object to one or multiple Parented objects or Renderables to be rendered on the next page"""

    def added_to_document(self):
        pass
