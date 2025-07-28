import fitz 
import os
import json
from langdetect import detect

def extract_headings_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    outline = []
    title = "Unknown Title"
    combined_title = []
    text_snippets = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    spans = line["spans"]
                    text = " ".join(span["text"].strip() for span in spans).strip()

                    if not text or len(text) < 2:
                        continue

                    font_size = spans[0]["size"]
                    font_flags = spans[0]["flags"]
                    is_bold = font_flags & 2 != 0

                    text_snippets.append(text)

                    if font_size > 14 or is_bold:
                        level = "H1" if font_size >= 16 else "H2"
                        heading = {
                            "level": level,
                            "text": text,
                            "page": page_num
                        }
                        outline.append(heading)
                        if page_num == 0 and level == "H1":
                            combined_title.append(text)

    language = detect(" ".join(text_snippets[:10])) if text_snippets else "unknown"

    return {
        "title": " ".join(combined_title).strip(),
        "language": language,
        "outline": outline
    }

def main():
    input_dir = "input"
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(input_dir, filename)
            result = extract_headings_from_pdf(pdf_path)

            output_filename = f"output_{os.path.splitext(filename)[0]}.json"
            output_path = os.path.join(output_dir, output_filename)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=4)

            print(f"{output_filename} generated.")

if __name__ == "__main__":
    main()
