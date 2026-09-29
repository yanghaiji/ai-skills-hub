"Extract text from Word (.docx) files, paragraph by paragraph."

import argparse
import sys


def extract_text(docx_path: str, headings_only: bool = False) -> None:
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

    heading_styles = {Heading 1, Heading 2, Heading 3, Heading 4, Heading 5, Title}
    heading_map = {
        Heading 1: # ,
        Heading 2: ## ,
        Heading 3: ### ,
        Heading 4: #### ,
        Heading 5: ##### ,
        Title: # ,
    }

    for para in doc.paragraphs:
        style_name = para.style.name if para.style else "
 text = para.text.strip()

 if not text:
 continue

 if headings_only:
 if style_name not in heading_styles:
 continue

 prefix = heading_map.get(style_name, )
 print(f{prefix}{text})


if __name__ == __main__:
 parser = argparse.ArgumentParser(description=Extract text from Word (.docx) files)
 parser.add_argument(docx_path, help=Path to the .docx file)
 parser.add_argument(--headings-only, action=store_true, help=Only extract heading paragraphs)
 args = parser.parse_args()

 extract_text(args.docx_path, args.headings_only)
