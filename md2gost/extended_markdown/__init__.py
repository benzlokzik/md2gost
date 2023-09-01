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
from .equation import Equation
from .heading import Heading
from .reference import Reference
from .table import Table
from .toc import TOC
from .inline_formula import InlineEquation
from .image import Image

Extension = MarkoExtension(
    elements=[
        Equation,
        Reference,
        Caption,
        Table,
        TOC,
        Heading,
        InlineEquation,
        Image
    ]
)

markdown = Markdown(extensions=[GFM, Extension])
