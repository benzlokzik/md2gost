# md2gost

Скрипт для генерации docx отчетов в соответствии с ГОСТ из markdown файла.

## Основные возможности
- Генерация отчета;
- ~~Добавление титульной страницы в формате docx~~(not yet);
- Генерация ~~интерактивного~~(not yet) содержания;
- Поддержка сквозной нумерации ~~и кросс-референсинга~~(not yet);
- Автоматическая расстановка картинок, продолжений таблиц и листингов и т.д.

## Пример
Markdown-файл: [example.md](https://github.com/witelokk/md2gost/blob/main/examples/example.md).

Сгенерированный файл в zip архиве (комманда `python -m md2gost --syntax-highlighting example.md`): [example.zip](https://nightly.link/witelokk/md2gost/workflows/example-generator/main/example.zip?h=f65c99d31a9379f44fcc6e923de4a735a271d5aa).

## Установка
```bash
pip install --upgrade git+https://github.com/witelokk/md2gost.git@main
```

Если ваша система приняла стандарт [PEP 668](https://peps.python.org/pep-0668/), используйте [pipx](https://pypa.github.io/pipx/):
```bash
pipx install --upgrade git+https://github.com/witelokk/md2gost.git@main
```

## Использование
```
(python -m ) md2docx [-h] [-o OUTPUT] [-t TEMPLATE] [--syntax-highlighting | --no-syntax-highlighting] [--debug] filename
```

При отсутствии флага -o, сгенерированый отчет будет иметь имя с названием исходного файла и расширением .md.

## Фичи

### Подписи рисунков, листингов, таблиц
Рисунки:
```markdown
![](path/to/image "Caption text")
```

Таблицы:
```markdown
%uniquename Caption text
| a | b | c |
|---|---|---|
| a | b | c |
```

Листинги:
~~~markdown
%uniquename Caption text
```python
print("hello world")
```
~~~

`uniquename` - уникальное имя для ссылок.

### Заголовки для основных разделов
Для того чтобы у заголовка не было сквозной нумерации (например для заголовка Содержание), используйте 
```markdown
# *Содержание
```

### Генерация содержания
```markdown
# *Содержание
[TOC]
```

### Подсветка синтаксиса в листингах
Используйте флаг ```--syntax-highlighting```

