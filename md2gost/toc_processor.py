from md2gost.renderable import Renderable
from md2gost.renderable.heading import Heading
from md2gost.renderable.toc import ToC


class TocProcessor:
    def process(self, renderables: list[Renderable]):
        renderables_iter = iter(renderables)

        toc = None
        for renderable in renderables_iter:
            if isinstance(renderable, ToC):
                toc = renderable
                break

        if toc:
            for renderable in renderables_iter:
                if isinstance(renderable, Heading):
                    toc.add_item(renderable.level, renderable.text, renderable.rendered_page, renderable.is_numbered)

            toc.fill()
