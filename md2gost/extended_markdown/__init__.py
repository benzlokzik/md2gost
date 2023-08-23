from marko import Markdown
from marko.ext.gfm import GFM
from marko.helpers import MarkoExtension

from marko import inline, block
from marko.ext.gfm import elements

from marko.inline import *
from marko.inline import InlineElement
from marko.block import *
from marko.block import BlockElement
from marko.ext.gfm.elements import *

from .caption import Caption
from .formula import Formula
from .heading import Heading
from .reference import Reference
from .table import Table
from .toc import TOC
from .inline_formula import InlineFormula

Extension = MarkoExtension(
    elements=[
        Formula,
        Reference,
        Caption,
        Table,
        TOC,
        Heading,
        InlineFormula
    ]
)

markdown = Markdown(extensions=[GFM, Extension])
