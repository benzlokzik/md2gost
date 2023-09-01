from dataclasses import dataclass

from md2gost.renderable import Renderable


@dataclass(frozen=True)
class SubRenderable:
    renderable: Renderable
    add_to_new_page: bool
