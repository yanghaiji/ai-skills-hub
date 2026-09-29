"""Extract text from PDF files using pdfplumber."""

import argparse
import sys


def extract_text(pdf_path: str, pages: list[int] | None = None) -> None:
    try:
        import pdfplumber
    except ImportError:
        print("Error: pdfplumber is not installed. Run: pip install pdfplumber", file=sys.stderr)
        sys.exit(1)

    try:
        with pdfplumber.open(pdf_path) as pdf:
            total = len(pdf.pages)
            target_pages = pages if pages else range(1, total + 1)

            for page_num in target_pages:
                if page_num < 1 or page_num > total:
                    print(f"[Warning] Page {page_num} out of range (1-{total}), skipping.", file=sys.stderr)
                    continue

                page = pdf.pages[page_num - 1]
                text = page.extract_text()

                print(f"{'=' * 60}")
                print(f"  Page {page_num} / {total}")
                print(f"{'=' * 60}")

                if text:
                    print(text)
                else:
                    print("[No text found on this page]")

                print()

    except FileNotFoundError:
        print(f"Error: File not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading PDF: {e}", file=sys.stderr)
        sys.exit(1)


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
    parser = argparse.ArgumentParser(description="Extract text from PDF files")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("--pages", default=None, help="Page numbers to extract (e.g., 1,2,3 or 1-5). Omit for all.")
    args = parser.parse_args()

    pages = parse_pages(args.pages)
    extract_text(args.pdf_path, pages)
