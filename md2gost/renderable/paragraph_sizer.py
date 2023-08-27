import logging
import os
from dataclasses import dataclass
from functools import cached_property
from math import ceil

from docx.enum.text import WD_LINE_SPACING
from docx.oxml import CT_R
from docx.text.run import Run
from freetype import Face

from docx.text.paragraph import Paragraph
from docx.text.font import Font as DocxFont
from docx.shared import Length, Pt
from docx.text.parfmt import ParagraphFormat
from docx.styles.style import _ParagraphStyle

from PIL import Image, ImageDraw, ImageFont

from .find_font import find_font


def _merge_objects(*objects):
    from inspect import getmembers, ismethod
    """
    Returns the new object containing attributes from objects, where the latest
    one has the highest priority.
    """

    class MergedObject:
        pass

    merged_object = MergedObject()
    for name, value in getmembers(objects[0]):
        if name.startswith("_") or ismethod(value):
            continue
        merged_object.__setattr__(name, value)

    for object_ in objects[1:]:
        for name, value in getmembers(object_):
            if name.startswith("_") or ismethod(value):
                continue
            if value is not None:
                merged_object.__setattr__(name, value)

    return merged_object


class Font:
    def __init__(self, name: str, bold: bool, italic: bool, size_pt: int):
        path = find_font(name, bold, italic)
        self._freetypefont = ImageFont.truetype(path, size_pt)
        self._draw = ImageDraw.Draw(Image.new("RGB", (1000, 1000)))

        self._face = Face(path)
        self._face.set_char_size(int(size_pt * 64))

    def get_text_width(self, text: str) -> Length:
        if not self.is_mono:
            bbox = self._draw.textbbox((0, 0), text, self._freetypefont)
            return Pt(bbox[2] - bbox[0])
        else:
            return Pt(len(text) * self._face.glyph.advance.x / 64)

    def get_line_height(self) -> Length:
        # TODO: make it work for all fonts
        if "Times" in str(self._face.family_name) and self._freetypefont.size == 14:
            return Pt(16.1)
        elif "Courier" in str(self._face.family_name) and self._freetypefont.size == 12:
            return Pt(13.59)
        else:
            logging.warning(f"Not supported font {self._face.family_name} {self._freetypefont.size}, rendering may be incorrect")
            return Pt(self._face.size.height / 64)

    @cached_property
    def is_mono(self):
        self._face.load_char("i")
        i_width = self._face.glyph.advance.x
        self._face.load_char("m")
        return i_width == self._face.glyph.advance.x
        # return self._face.glyph.bitmap.width


@dataclass
class ParagraphSizerResult:
    before: Length
    lines: int
    line_height: Length
    line_spacing: float
    after: Length

    @property
    def base(self) -> Length:
        return self.before + ((self.lines - 1) * self.line_spacing + 1) * self.line_height

    @property
    def full(self) -> Length:
        return Length(self.before + self.line_height * self.line_spacing * self.lines + self.after)


class ParagraphSizer:
    def __init__(self, paragraph: Paragraph, previous_paragraph: Paragraph | None, max_width: Length):
        self.previous_paragraph = previous_paragraph
        self.max_width = max_width
        self.paragraph = paragraph

        self.same_style_as_previous = (paragraph.style == previous_paragraph.style) if previous_paragraph else False

    @cached_property
    def _default_style(self):

        default_style_element = type("DefaultStyle", (), {})
        default_style_element.rPr = \
            self.paragraph.part.document.styles.element.xpath(
                'w:docDefaults/w:rPrDefault/w:rPr')[0]
        default_style_element.pPr = \
            self.paragraph.part.document.styles.element.xpath(
                'w:docDefaults/w:pPrDefault/w:pPr')[0]
        default_style = _ParagraphStyle(default_style_element)
        return default_style

    @cached_property
    def _styles(self) -> list[_ParagraphStyle]:
        styles = [self.paragraph.style]
        while styles[-1].base_style:
            styles.append(styles[-1].base_style)
        styles.append(self._default_style)
        return styles

    @cached_property
    def _is_contextual_spacing(self) -> bool:
        contextual_spacing = False
        pPrs = [self.paragraph.paragraph_format._element.pPr] + \
               [style._element.pPr for style in self._styles]
        for pPr in pPrs:
            if pPr.xpath("./w:contextualSpacing"):
                contextual_spacing = True
                break
        return contextual_spacing

    def count_lines(self, runs: list[Run], max_width: Length, docx_font: DocxFont, first_line_indent: Length, is_mono: bool = False):
        lines = 1
        line_width = first_line_indent

        space_width = Font(docx_font.name, docx_font.bold, docx_font.italic, docx_font.size.pt).get_text_width(" ")
        if not is_mono:
            space_width *= 0.8

        word_part = ""
        word_parts_widths = [0]
        spaces = 0
        for i, run in enumerate(runs):
            if word_part:
                word_part = ""
                word_parts_widths.append(0)

            run_docx_font = _merge_objects(
                docx_font,
                run.font
            )
            font = Font(run_docx_font.name, run_docx_font.bold, run_docx_font.italic, run_docx_font.size.pt)

            run_text = run.text
            if run_text == "" and run._element.xpath("w:noBreakHyphen"):
                run_text = "-"
            if i == len(runs) - 1:
                run_text += " "  # add space to the end of the last run, so it adds the last word

            for c in run_text:
                if c == " ":
                    if any(word_parts_widths):
                        width = spaces*space_width + sum(word_parts_widths)
                        if width <= max_width - line_width:
                            line_width += width
                        elif width > max_width - first_line_indent:
                            if lines == 1 and line_width == first_line_indent and not spaces:
                                lines += ceil((width - (max_width - first_line_indent)) / max_width)
                                line_width = (width - (max_width - first_line_indent)) % max_width
                            else:
                                lines += ceil(width / max_width)
                                line_width = width % max_width
                        else:
                            lines += 1
                            line_width = sum(word_parts_widths)

                        word_part = ""
                        word_parts_widths = [0]
                        spaces = 1
                    else:
                        spaces += 1
                else:
                    word_part += c
                    word_parts_widths[-1] = font.get_text_width(word_part)

        return int(lines)

    def calculate_height(self) -> ParagraphSizerResult:
        max_width = self.max_width


        docx_font: DocxFont = _merge_objects(
            *[style.font for style in self._styles[::-1] if style.font],
            self.paragraph.style.font)

        paragraph_format: ParagraphFormat = _merge_objects(
            *[style.paragraph_format for style in self._styles[::-1]
              if style.paragraph_format],
            self.paragraph.paragraph_format
        )

        max_width -= (paragraph_format.left_indent or 0) + \
            (paragraph_format.right_indent or 0)

        font = Font(docx_font.name, docx_font.bold, docx_font.italic, docx_font.size.pt)

        # here self.paragraph.runs is not used because
        # it does not always return all runs (e.g. if they are inside hyperlink)
        runs = []
        for element in self.paragraph._element.getiterator():
            if isinstance(element, CT_R):
                runs.append(Run(element, self.paragraph))

        lines = self.count_lines(runs, max_width, docx_font, paragraph_format.first_line_indent or 0,
                                 font.is_mono)

        previous_paragraph_format: ParagraphFormat = None
        if self.previous_paragraph:
            previous_paragraph_styles = [self.previous_paragraph.style]
            while previous_paragraph_styles[-1].base_style:
                previous_paragraph_styles.append(
                    previous_paragraph_styles[-1].base_style
                )
            previous_paragraph_styles.append(self._default_style)
            previous_paragraph_format = _merge_objects(
                *[style.paragraph_format for style in previous_paragraph_styles[::-1]
                    if style.paragraph_format],
                self.previous_paragraph.paragraph_format
            )

        if self._is_contextual_spacing and self.same_style_as_previous:
            before = (previous_paragraph_format.space_after or 0)
        else:
            before = (paragraph_format.space_before or 0)
            if previous_paragraph_format:
                before = max(0, before - (previous_paragraph_format.space_after or 0))

        after = (paragraph_format.space_after or 0)

        line_height = font.get_line_height()
        line_spacing = paragraph_format.line_spacing
        if paragraph_format.line_spacing_rule == WD_LINE_SPACING.EXACTLY:
            line_spacing /= line_height
            # raise NotImplementedError("Line spacing rule AT_LEAST is not supported")
        elif paragraph_format.line_spacing_rule == WD_LINE_SPACING.AT_LEAST:
            raise NotImplementedError("Line spacing rule AT_LEAST is not supported")

        return ParagraphSizerResult(before, lines, line_height, line_spacing, after)
