"""Extract tables from PDF files using pdfplumber."""

import argparse
import csv
import io
import sys


def extract_tables(pdf_path: str, pages: list[int] | None = None, fmt: str = "markdown") -> None:
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

            for page_num in target_pages:
                if page_num < 1 or page_num > total:
                    print(f"[Warning] Page {page_num} out of range (1-{total}), skipping.", file=sys.stderr)
                    continue

                page = pdf.pages[page_num - 1]
                tables = page.extract_tables()

                if not tables:
                    continue

                for table_idx, table in enumerate(tables):
                    table_count += 1
                    print(f"\n--- Table {table_count} (Page {page_num}) ---\n")

                    if fmt == "csv":
                        output = io.StringIO()
                        writer = csv.writer(output)
                        for row in table:
                            writer.writerow([cell if cell else "" for cell in row])
                        print(output.getvalue())
                    else:
                        print_markdown_table(table)

            if table_count == 0:
                print("No tables found in the specified pages.")
            else:
                print(f"\nTotal: {table_count} table(s) extracted.")

    except FileNotFoundError:
        print(f"Error: File not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading PDF: {e}", file=sys.stderr)
        sys.exit(1)


def print_markdown_table(table: list[list[str]]) -> None:
    if not table:
        return

    # Normalize: replace None with empty string
    normalized = [[cell if cell else "" for cell in row] for row in table]

    # Calculate column widths
    col_count = max(len(row) for row in normalized)
    col_widths = [0] * col_count
    for row in normalized:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell))
    col_widths = [max(w, 3) for w in col_widths]

    # Print header
    header = normalized[0]
    header_line = "| " + " | ".join(cell.ljust(col_widths[i]) for i, cell in enumerate(header)) + " |"
    separator = "| " + " | ".join("-" * col_widths[i] for i in range(col_count)) + " |"
    print(header_line)
    print(separator)

    # Print rows
    for row in normalized[1:]:
        # Pad row if it has fewer columns
        while len(row) < col_count:
            row.append("")
        line = "| " + " | ".join(cell.ljust(col_widths[i]) for i, cell in enumerate(row)) + " |"
        print(line)


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
    parser = argparse.ArgumentParser(description="Extract tables from PDF files")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("--pages", default=None, help="Page numbers to extract (e.g., 1,2,3 or 1-5). Omit for all.")
    parser.add_argument("--format", default="markdown", choices=["markdown", "csv"], help="Output format (default: markdown)")
    args = parser.parse_args()

    pages = parse_pages(args.pages)
    extract_tables(args.pdf_path, pages, args.format)
