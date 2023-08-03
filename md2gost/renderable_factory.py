from functools import singledispatchmethod

from docx.shared import Parented, RGBColor

from .renderable import *
from .renderable import Renderable
from . import extended_markdown


class RenderableFactory:
    @singledispatchmethod
    @staticmethod
    def create(marko_element: extended_markdown.BlockElement, parent: Parented) \
            -> Renderable:
        paragraph = Paragraph(parent)
        paragraph.add_run(f"{marko_element.get_type()} is not supported", color=RGBColor.from_string('ff0000'))
        return paragraph

    @staticmethod
    def _create_runs(paragraph: Paragraph, children, classes: list[type] = None):
        if not classes:
            classes = []
        for child in children:
            if isinstance(child, extended_markdown.RawText):
                paragraph.add_run(child.children,
                                  extended_markdown.StrongEmphasis in classes,
                                  extended_markdown.Emphasis in classes)
            elif isinstance(child, (extended_markdown.Emphasis, extended_markdown.StrongEmphasis)):
                RenderableFactory._create_runs(paragraph, child.children, classes+[type(child)])
            else:
                paragraph.add_run(f" {child.get_type()} is not supported ", color=RGBColor.from_string("FF0000"))

    @create.register
    @staticmethod
    def _(marko_paragraph: extended_markdown.Paragraph, parent: Parented):
        paragraph = Paragraph(parent)
        RenderableFactory._create_runs(paragraph, marko_paragraph.children)
        return paragraph


    @create.register
    @staticmethod
    def _(marko_code_block: extended_markdown.FencedCode | extended_markdown.CodeBlock, parent: Parented):
        listing = Listing(parent)
        listing.set_text(marko_code_block.children[0].children)
        return listing
