from dataclasses import dataclass
from docx.shared import Parented, Length


@dataclass(frozen=True)
class RenderedInfo:
    docx_element: Parented
    height: Length
