from collections.abc import Generator

from docx import Document
from marko.block import BlankLine

from .extended_markdown import markdown, Caption
from .renderable.caption import CaptionInfo
from .renderable.renderable import Renderable
from .renderable_factory import RenderableFactory


class Parser:
    """Parses given markdown string and returns Renderable elements"""

    def __init__(self, document: Document, text: str):
        self._document = document
        self._parsed = markdown.parse(text)
        self._caption_info: CaptionInfo | None = None

    def parse(self) -> Generator[Renderable, None, None]:
        factory = RenderableFactory(self._document._body)

        for marko_element in self._parsed.children:
            if isinstance(marko_element, BlankLine):
                continue

            if isinstance(marko_element, Caption):
                self._caption_info = CaptionInfo(marko_element.unique_name, marko_element.text)
                continue

            yield factory.create(marko_element, self._caption_info)
            self._caption_info = None
