from md2gost.renderable import Renderable
from md2gost.renderable.heading import Heading
from md2gost.renderable.toc import ToC


class TocProcessor:
    def process(self, renderables: list[Renderable]):
        toc = None
        for renderable in renderables:
            if isinstance(renderable, ToC):
                toc = renderable
                break

        if toc:
            for renderable in renderables:
                if isinstance(renderable, Heading):
                    toc.add_item(renderable.level, renderable.text, renderable.rendered_page)

            toc.fill()
