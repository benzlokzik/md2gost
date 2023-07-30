import docx
from docx.document import Document

from .parser_ import Parser
from .renderer import Renderer


class Converter:
    """Converts markdown file to docx file"""

    def __init__(self, input_path: str, output_path: str,
                 template_path: str = None):
        self.output_path = output_path
        self.document: Document = docx.Document(template_path)
        self.document._body.clear_content()
        with open(input_path, encoding="utf-8") as f:
            self.parser = Parser(self.document, f.read())

    def convert(self):
        renderables = list(self.parser.parse())

        processors = [
            Renderer(self.document),
        ]

        for processor in processors:
            processor.process(renderables)

    def get_document(self) -> Document:
        return self.document
