"""解析上传的文件夹，提取开题报告文本和数据文件信息"""
import os
from pathlib import Path
from dataclasses import dataclass, field
import pandas as pd

@dataclass
class ParsedFiles:
    proposal_text: str = ""
    data_frames: dict = field(default_factory=dict)
    reference_texts: list = field(default_factory=list)
    file_list: list = field(default_factory=list)

def parse_docx(path: str) -> str:
    from docx import Document
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

def parse_pdf(path: str) -> str:
    import pdfplumber
    text_parts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages[:50]:
            t = page.extract_text()
            if t:
                text_parts.append(t)
    return "\n".join(text_parts)

def parse_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def parse_data_file(path: str) -> pd.DataFrame:
    ext = Path(path).suffix.lower()
    if ext in (".xlsx", ".xls"):
        return pd.read_excel(path)
    elif ext == ".csv":
        return pd.read_csv(path, encoding="utf-8", errors="ignore")
    return pd.DataFrame()

def parse_folder(folder_path: str) -> ParsedFiles:
    result = ParsedFiles()
    text_exts = {".docx", ".pdf", ".txt", ".md"}
    data_exts = {".xlsx", ".xls", ".csv"}

    for root, _, files in os.walk(folder_path):
        for fname in files:
            fpath = os.path.join(root, fname)
            ext = Path(fname).suffix.lower()
            result.file_list.append(fname)

            if ext == ".docx":
                text = parse_docx(fpath)
                if len(text) > len(result.proposal_text):
                    result.proposal_text = text
            elif ext == ".pdf":
                text = parse_pdf(fpath)
                if "开题" in fname or "proposal" in fname.lower():
                    result.proposal_text = text
                else:
                    result.reference_texts.append(text[:3000])
            elif ext in (".txt", ".md"):
                text = parse_txt(fpath)
                if not result.proposal_text:
                    result.proposal_text = text
            elif ext in data_exts:
                try:
                    df = parse_data_file(fpath)
                    result.data_frames[fname] = df
                except Exception:
                    pass

    return result
