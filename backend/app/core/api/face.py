from typing import List
import os, csv

# 直接复用 app.api.face 中的其余实现（若需要可继续引用）
from app.api import face as _face_api  # noqa: F401

# CSV 路径：backend/faces_data/faces.csv
CSV_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "faces_data", "faces.csv"))


def read_csv_records() -> List[dict]:
    """读取人脸 CSV 记录，返回 [{'id': str, 'name': str, 'status': str, ...}, ...]"""
    if not os.path.exists(CSV_FILE):
        return []
    records = []
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
    return records

# 其余符号全部从 app.api.face 导出，避免循环依赖
__all__ = [*dir(_face_api), "read_csv_records"] 