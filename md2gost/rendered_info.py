from dataclasses import dataclass
from docx.shared import Parented, Length


@dataclass(frozen=True)
class RenderedInfo:
    docx_element: Parented
    is_added_to_new_page: bool
    height: Length
