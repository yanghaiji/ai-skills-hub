"""Extract both text and tables from PDF files in one pass."""

import argparse
import csv
import io
import os
import sys


def extract_all(pdf_path: str, pages: list[int] | None = None, output: str | None = None) -> None:
    try:
        import pdfplumber
    except ImportError:
        print("Error: pdfplumber is not installed. Run: pip install pdfplumber", file=sys.stderr)
        sys.exit(1)

    try:
        with pdfplumber.open(pdf_path) as pdf:
            total = len(pdf.pages)
            target_pages = pages if pages else range(1, total + 1)
            table_count = 0
            lines: list[str] = []

            def out(text: str = ""):
                lines.append(text)

            file_name = os.path.basename(pdf_path)
            out(f"# PDF: {file_name} (total {total} pages)")
            out()

            for page_num in target_pages:
                if page_num < 1 or page_num > total:
                    print(f"[Warning] Page {page_num} out of range (1-{total}), skipping.", file=sys.stderr)
                    continue

                page = pdf.pages[page_num - 1]

                # Extract text
                text = page.extract_text()
                out(f"{'=' * 60}")
                out(f"  Page {page_num} / {total}")
                out(f"{'=' * 60}")

                if text:
                    out(text)
                else:
                    out("[No text found on this page]")
                out()

                # Extract tables
                tables = page.extract_tables()
                if tables:
                    for table_idx, table in enumerate(tables):
                        table_count += 1
                        out(f"--- Table {table_count} (Page {page_num}) ---")
                        out()
                        print_markdown_table(table, out)
                        out()

            if table_count > 0:
                out(f"Total: {table_count} table(s) extracted.")

            result = "\n".join(lines)

            if output:
                with open(output, "w", encoding="utf-8") as f:
                    f.write(result)
                print(f"Output saved to: {output}")
            else:
                print(result)

    except FileNotFoundError:
        print(f"Error: File not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading PDF: {e}", file=sys.stderr)
        sys.exit(1)


def print_markdown_table(table: list[list[str]], out=print) -> None:
    if not table:
        return

    normalized = [[cell if cell else "" for cell in row] for row in table]

    col_count = max(len(row) for row in normalized)
    col_widths = [0] * col_count
    for row in normalized:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell))
    col_widths = [max(w, 3) for w in col_widths]

    header = normalized[0]
    header_line = "| " + " | ".join(cell.ljust(col_widths[i]) for i, cell in enumerate(header)) + " |"
    separator = "| " + " | ".join("-" * col_widths[i] for i in range(col_count)) + " |"
    out(header_line)
    out(separator)

    for row in normalized[1:]:
        while len(row) < col_count:
            row.append("")
        line = "| " + " | ".join(cell.ljust(col_widths[i]) for i, cell in enumerate(row)) + " |"
        out(line)


def parse_pages(pages_str: str | None) -> list[int] | None:
    if not pages_str:
        return None
    result = []
    for part in pages_str.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-", 1)
            result.extend(range(int(start), int(end) + 1))
        else:
            result.append(int(part))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract text and tables from PDF files")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("--pages", default=None, help="Page numbers to extract (e.g., 1,2,3 or 1-5). Omit for all.")
    parser.add_argument("--output", "-o", default=None, help="Save output to file instead of stdout")
    args = parser.parse_args()

    pages = parse_pages(args.pages)
    extract_all(args.pdf_path, pages, args.output)
