#!/usr/bin/env python3
"""Поднимает версию приложения (SemVer) в sw.js.

    python3 project/bump.py patch   # 1.0.0 -> 1.0.1  исправления, мелкие правки вида
    python3 project/bump.py minor   # 1.0.1 -> 1.1.0  новая возможность, сохранения совместимы
    python3 project/bump.py major   # 1.1.0 -> 2.0.0  несовместимо: меняется формат сохранений/рекорда
    python3 project/bump.py         # показать текущую версию

Смена версии меняет имя офлайн-кэша, поэтому iPad при следующем запуске
с интернетом обновит игру и удалит старый кэш.
"""
import pathlib, re, sys

SW = pathlib.Path(__file__).resolve().parent.parent / 'sw.js'
PATTERN = re.compile(r"const VERSION='(\d+)\.(\d+)\.(\d+)';")


def main():
    text = SW.read_text(encoding='utf-8')
    m = PATTERN.search(text)
    if not m:
        sys.exit(f"В {SW} не найдена строка вида const VERSION='1.2.3';")
    major, minor, patch = map(int, m.groups())
    current = f'{major}.{minor}.{patch}'
    if len(sys.argv) < 2:
        print(current)
        return
    part = sys.argv[1].lower()
    if part == 'major':
        major, minor, patch = major + 1, 0, 0
    elif part == 'minor':
        minor, patch = minor + 1, 0
    elif part == 'patch':
        patch += 1
    else:
        sys.exit('Укажите patch, minor или major')
    new = f'{major}.{minor}.{patch}'
    SW.write_text(text[:m.start()] + f"const VERSION='{new}';" + text[m.end():], encoding='utf-8')
    print(f'{current} -> {new}')
    print(f'Дальше: git add -A && git commit -m "v{new}: <что изменилось>" && git tag v{new} && git push --follow-tags')


if __name__ == '__main__':
    main()
