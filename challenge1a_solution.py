import os
import json
import fitz  # PyMuPDF
from typing import List, Dict, Tuple
from pathlib import Path
from statistics import median
import re
from concurrent.futures import ThreadPoolExecutor


class HeadingExtractor:
    def __init__(self):
        self.min_words = 2
        self.max_words = 15
        self.min_len = 8

    def get_font_info(self, span) -> Tuple[float, str, int]:
        return span.get("size", 12.0), span.get("font", ""), span.get("flags", 0)

    def is_bold(self, flags: int) -> bool:
        return bool(flags & 2) or bool(flags & (1 << 4))

    def merge_spans(self, line) -> str:
        return " ".join(span["text"].strip() for span in line["spans"] if span["text"].strip())

    def extract_font_clusters(self, sizes: List[float]) -> List[float]:
        return sorted(list(set(sizes)), reverse=True)[:4]

    def classify_level(self, font_size: float, size_clusters: List[float]) -> str:
        if font_size >= size_clusters[0]:
            return "H1"
        elif len(size_clusters) > 1 and font_size >= size_clusters[1]:
            return "H2"
        elif len(size_clusters) > 2 and font_size >= size_clusters[2]:
            return "H3"
        return ""

    def heading_score(self, text: str, font_size: float, flags: int,
                      page_avg: float, is_uniform: bool, position_ratio: float) -> float:
        score = 0
        if self.is_bold(flags):
            score += 1
        if text.isupper():
            score += 1
        if is_uniform:
            score += 1
        if position_ratio < 0.25:
            score += 1
        if font_size > page_avg:
            score += 1
        return score / 5.0

    def is_heading_candidate(self, text: str, font_size: float, flags: int,
                             page_avg: float, is_uniform: bool, position_ratio: float) -> bool:
        if not text or len(text) < self.min_len:
            return False
        if len(text.split()) < self.min_words or len(text.split()) > self.max_words:
            return False
        if text.endswith(('.', ',', ';', '?', ':', '”', '"')):
            return False
        if text[0].islower():
            return False
        if any(p in text.lower() for p in ["which", "that", "based on", "from", "with"]) and len(text.split()) > 6:
            return False
        if font_size < page_avg * 0.9:
            return False
        if sum(c.isdigit() for c in text) > len(text) * 0.4:
            return False
        if len(text.split()) == 1 and len(text) < 10:
            return False
        return self.heading_score(text, font_size, flags, page_avg, is_uniform, position_ratio) >= 0.6

    def extract_title(self, spans: List[Tuple[str, float]]) -> str:
        spans = sorted(spans, key=lambda x: -x[1])
        for text, size in spans:
            clean = text.strip().rstrip(':.,;!?')
            if len(clean.split()) >= 3 and not clean.isupper():
                return clean
        return spans[0][0].strip() if spans else "Untitled Document"

    def extract(self, pdf_path: str) -> Dict:
        doc = fitz.open(pdf_path)
        all_font_sizes = []
        title_candidates = []
        headings = []
        seen = set()

        page_fonts = {}
        for page_num, page in enumerate(doc, start=1):
            fonts = []
            for block in page.get_text("dict")["blocks"]:
                for line in block.get("lines", []):
                    for span in line["spans"]:
                        if span["text"].strip():
                            fonts.append(span["size"])
                            if page_num == 1:
                                title_candidates.append((span["text"].strip(), span["size"]))
            if fonts:
                page_fonts[page_num] = sum(fonts) / len(fonts)
                all_font_sizes.extend(fonts)

        size_clusters = self.extract_font_clusters(all_font_sizes)
        title = self.extract_title(title_candidates)

        for page_num, page in enumerate(doc, start=1):
            page_height = page.rect.height
            page_avg = page_fonts.get(page_num, median(all_font_sizes))
            for block in page.get_text("dict")["blocks"]:
                for line in block.get("lines", []):
                    text = self.merge_spans(line).strip()
                    if not text:
                        continue
                    clean_text = re.sub(r"\\s+", " ", text.lower())
                    if (clean_text, page_num) in seen:
                        continue

                    sizes = [span["size"] for span in line["spans"]]
                    fonts = [span["font"] for span in line["spans"]]
                    is_uniform = len(set(sizes)) == 1 and len(set(fonts)) == 1
                    position_ratio = line["bbox"][1] / page_height if page_height else 1.0
                    span = line["spans"][0]
                    font_size, font_name, flags = self.get_font_info(span)

                    if self.is_heading_candidate(text, font_size, flags, page_avg, is_uniform, position_ratio):
                        level = self.classify_level(font_size, size_clusters)
                        confidence = round(self.heading_score(text, font_size, flags, page_avg, is_uniform, position_ratio), 2)
                        if level:
                            headings.append({
                                "level": level,
                                "text": text,
                                "page": page_num,
                                "confidence": confidence
                            })
                            seen.add((clean_text, page_num))

        doc.close()
        return {
            "title": title,
            "outline": sorted(headings, key=lambda x: (x['page'], x['text']))
        }


def process_all_pdfs(input_dir="/app/input", output_dir="/app/output"):
    os.makedirs(output_dir, exist_ok=True)
    extractor = HeadingExtractor()

    def process(file):
        if file.lower().endswith(".pdf"):
            path = os.path.join(input_dir, file)
            result = extractor.extract(path)
            output_path = os.path.join(output_dir, f"{Path(file).stem}.json")
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"✅ Extracted: {output_path}")

    with ThreadPoolExecutor() as executor:
        executor.map(process, os.listdir(input_dir))


if __name__ == "__main__":
    process_all_pdfs()
