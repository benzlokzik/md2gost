#!/bin/python
from argparse import ArgumentParser, BooleanOptionalAction
import os.path
from getpass import getuser

from docxcompose.composer import Composer
from docx import Document

from .converter import Converter


def main():
    parser = ArgumentParser(
        prog="md2docx",
        description="Этот скрипт предназначен для генерирования отчетов/\
                курсовых работ по ГОСТ в формате docx из Markdown-файла."
    )
    parser.add_argument("filename", help="Путь до исходного markdown файла")
    parser.add_argument("-o", "--output", help="Путь до сгенерированного \
                            файла")
    parser.add_argument("-t", "--template", help="Путь до шаблона .docx")
    parser.add_argument("-T", "--title", help="Путь до файла титульной(-ых) \
                            страниц(ы)")
    parser.add_argument("--syntax-highlighting", help="Подсветка синтаксиса в листингах",
                        action=BooleanOptionalAction)
    parser.add_argument("--debug", help="Добавляет отладочные данные в документ",
                        action="store_true")

    args = parser.parse_args()
    filename, output, template, title, debug = \
        args.filename, args.output, args.template, args.title, args.debug
    if args.syntax_highlighting:
        os.environ["SYNTAX_HIGHLIGHTING"] = "1"

    if not filename.endswith(".md"):
        print("Error: filename must have md format")
        exit(1)

    os.environ["WORKING_DIR"] = os.path.dirname(filename)

    if output:
        if not output.endswith(".docx"):
            print("Error: output must have docx format")
            exit(2)
    else:
        output = os.path.basename(filename).replace(".md", ".docx")

    if not template:
        template = os.path.join(os.path.dirname(__file__), "Template.docx")

    converter = Converter(filename, output, template, debug)
    converter.convert()

    document = converter.document

    if title:
        title = Document(title)
        title.add_page_break()
        composer = Composer(title)
        composer.append(document)
        document = composer.doc

    document.core_properties.author = getuser()
    document.core_properties.comments =\
        "Создано при помощи https://github.com/witelokk/md2gost"

    document.save(output)
    print(f"Generated document: {os.path.abspath(output)}")

    if debug:
        import platform
        if platform.system() == 'Darwin':       # macOS
            import subprocess
            subprocess.call(('open', output))
        elif platform.system() == 'Windows':    # Windows
            os.startfile(output)
        else:                                   # linux variants
            import subprocess
            subprocess.call(('xdg-open', output))

if __name__ == "__main__":
    main()
