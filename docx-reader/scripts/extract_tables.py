"Extract tables from Word (.docx) files."

import argparse
import csv
import sys


def extract_tables(docx_path: str, fmt: str = markdown) -> None:
    try:
        from docx import Document
    except ImportError:
        print(Error: python-docx is not installed. Run: pip install python-docx, file=sys.stderr)
        sys.exit(1)

    try:
        doc = Document(docx_path)
    except Exception as e:
        print(fError reading docx: {e}, file=sys.stderr)
        sys.exit(1)

    tables = doc.tables
    if not tables:
        print([No tables found in this document])
        return

    for idx, table in enumerate(tables, 1):
        rows = []
        for row in table.rows:
            cells = [cell.text.strip().replace(\n,  ) for cell in row.cells]
            rows.append(cells)

        if not rows:
            continue

        print(f\n--- Table {idx} ---\n)

        if fmt == csv:
            writer = csv.writer(sys.stdout)
            for row in rows:
                writer.writerow(row)
        else:
            print_markdown_table(rows)

    print(f\nTotal: {len(tables)} table(s) extracted.)


def print_markdown_table(rows: list[list[str]]) -> None:
    col_count = max(len(row) for row in rows)
    for row in rows:
        while len(row) < col_count:
            row.append(")

 col_widths = [0] * col_count
 for row in rows:
 for i, cell in enumerate(row):
 col_widths[i] = max(col_widths[i], len(cell))
 col_widths = [max(w, 3) for w in col_widths]

 header = rows[0]
 header_line = |  +  | .join(cell.ljust(col_widths[i]) for i, cell in enumerate(header)) +  |
 separator = |  +  | .join(- * col_widths[i] for i in range(col_count)) +  |
 print(header_line)
 print(separator)

 for row in rows[1:]:
 line = |  +  | .join(cell.ljust(col_widths[i]) for i, cell in enumerate(row)) +  |
 print(line)


if __name__ == __main__:
 parser = argparse.ArgumentParser(description=Extract tables from Word (.docx) files)
 parser.add_argument(docx_path, help=Path to the .docx file)
 parser.add_argument(--format, choices=[markdown, csv], default=markdown, help=Output format (default: markdown))
 args = parser.parse_args()

 extract_tables(args.docx_path, args.format)
