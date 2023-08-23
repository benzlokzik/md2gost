import docx
from docx.document import Document

from .debugger import Debugger
from .parser_ import Parser
from .toc_processor import TocProcessor
from .renderer import Renderer


class Converter:
    """Converts markdown file to docx file"""

    def __init__(self, input_path: str, output_path: str,
                 template_path: str = None, debug: bool = False):
        self._output_path = output_path
        self._document: Document = docx.Document(template_path)
        self._document._body.clear_content()
        self._debugger = Debugger(self._document) if debug else None
        with open(input_path, encoding="utf-8") as f:
            self.parser = Parser(self._document, f.read())

    def convert(self):
        renderables = list(self.parser.parse())

        processors = [
            Renderer(self._document, self._debugger),
            TocProcessor()
        ]

        for processor in processors:
            processor.process(renderables)

    @property
    def document(self) -> Document:
        return self._document
