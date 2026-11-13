from html import escape  # Экранирование защищает подписи диаграммы от специальных XML/HTML-символов.
from pathlib import Path  # Path определяет корень относительно расположения скрипта.
import sqlite3  # Стандартный драйвер читает реальную SQLite без установки дополнительных Python-библиотек.
import subprocess  # Для отрисовки ER используем локальную программу Graphviz dot, если она установлена.
ROOT = Path(__file__).resolve().parent.parent  # Скрипт находится в tools/, поэтому два parent дают корень Demo.
connection = sqlite3.connect(f"file:{ROOT / 'db.sqlite3'}?mode=ro", uri=True)  # Открываем существующую БД только для чтения и не создаём пустой файл при ошибке пути.
output = ROOT / "db"  # Все материалы проектирования складываем в одну папку.
output.mkdir(exist_ok=True)  # Повторный экспорт не требует ручного создания папки.
statements = connection.execute("SELECT type, name, sql FROM sqlite_master WHERE sql IS NOT NULL AND name NOT LIKE 'sqlite_%' ORDER BY type DESC, name").fetchall()  # sqlite_master содержит фактические определения таблиц и индексов без пользовательских данных.
lines = ["-- Справочный экспорт фактической схемы SQLite. Рабочую БД создавайте через manage.py migrate, не импортом этого файла."]  # Объясняем различие между DDL-справкой и управлением историей миграций Django.
for kind, name, sql in statements:  # Экспортируем только структуру, никогда не пароли, сессии и строки заявок.
    lines.append(f"-- {kind} {name}: определение получено из sqlite_master; подробности полей объяснены в models.py и миграции.")  # Каждое SQL-выражение сопровождается назначением и источником.
    lines.append(sql.rstrip(";") + "; -- Создаёт указанную таблицу или индекс точно по текущей схеме.")  # Завершаем выражение одной точкой с запятой и поясняем выполняемое действие.
(output / "schema.sql").write_text("\n".join(lines) + "\n", encoding="utf-8")  # Сохраняем схему UTF-8 для просмотра без интернета.
nodes = ["digraph ER { // Направленный граф описывает реальные связи бизнес-таблиц.", 'rankdir=TB; // Связанные таблицы располагаются сверху вниз.', 'graph [bgcolor="white", pad="0.4", nodesep="0.6", ranksep="0.9"]; // Настраиваем читаемые отступы диаграммы.', 'node [shape=plain, fontname="DejaVu Sans", fontsize=11]; // Узлы будут таблицами с подписями полей.']  # Начинаем исходник Graphviz, который тоже можно изучать офлайн.
tables = ["portal_user", "portal_course", "portal_application"]  # В предметной ER показываем три бизнес-сущности; служебные таблицы Django есть в schema.sql.
for table in tables:  # Содержимое узлов строим из реальной БД, а не вручную придуманного списка полей.
    columns = connection.execute(f'PRAGMA table_info("{table}")').fetchall()  # Имена здесь взяты из нашего фиксированного списка, а не из пользовательского ввода.
    foreign = {row[3] for row in connection.execute(f'PRAGMA foreign_key_list("{table}")')}  # Определяем, какие колонки являются внешними ключами.
    rows = [f'<TR><TD BGCOLOR="#d9eee3"><B>{escape(table)}</B></TD></TR>']  # Первая строка визуального узла — заголовок таблицы.
    for _, name, kind, not_null, default, primary in columns:  # PRAGMA возвращает имя, тип, обязательность, значение по умолчанию и признак PK.
        key = " PK" if primary else " FK" if name in foreign else ""  # Первичные и внешние ключи помечаем прямо в подписи поля.
        rows.append(f'<TR><TD ALIGN="LEFT">{escape(name + " : " + kind + key)}</TD></TR>')  # Одна строка диаграммы соответствует одной фактической колонке.
    nodes.append(f'{table} [label=<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="6">{"".join(rows)}</TABLE>>]; // Реальные поля таблицы {table}.')  # Закрываем узел с HTML-подобной табличной подписью Graphviz.
for row in connection.execute('PRAGMA foreign_key_list("portal_application")'):  # У заявки есть два внешних ключа, которые нужно показать рёбрами.
    target, source, destination = row[2], row[3], row[4]  # Извлекаем таблицу назначения и имена связанных колонок.
    nodes.append(f'{target} -> portal_application [label="1 : N ({source})", fontname="DejaVu Sans", fontsize=10]; // Одна запись {target} может иметь много заявок через {source}.')  # Ребро направлено от родительской таблицы к зависимой.
nodes.append("} // Завершаем граф связей бизнес-сущностей.")  # Закрываем синтаксис dot-файла.
(output / "er_diagram.dot").write_text("\n".join(nodes) + "\n", encoding="utf-8")  # Исходник позволяет пересоздать ER после изменения БД.
connection.close()  # Освобождаем соединение, поскольку все необходимые метаданные уже прочитаны.
try:  # Graphviz нужен только для повторного экспорта картинки, а не для работы самого портала.
    subprocess.run(["dot", "-Tsvg", str(output / "er_diagram.dot"), "-o", str(output / "er_diagram.svg")], check=True)  # Локально создаём векторную ER-картинку по фактической схеме SQLite.
except FileNotFoundError:  # На экзаменационном компьютере Graphviz может отсутствовать.
    print("SQL и DOT сохранены. Для картинки установите Graphviz заранее либо экспортируйте ER через DBeaver.")  # Не пытаемся скачивать графический инструмент из интернета.
else:  # Эта ветка выполняется только при успешной генерации SVG.
    print("Готово: db/schema.sql, db/er_diagram.dot, db/er_diagram.svg.")  # Называем три готовых результата экспорта структуры.
