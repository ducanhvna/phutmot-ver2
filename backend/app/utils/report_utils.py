import pandas as pd
from fastapi import UploadFile
from typing import List
import io

def read_excel(file: UploadFile) -> pd.DataFrame:
    content = file.file.read()
    df = pd.read_excel(io.BytesIO(content))
    return df

def read_csv(file: UploadFile) -> pd.DataFrame:
    content = file.file.read()
    df = pd.read_csv(io.BytesIO(content))
    return df

def generate_report_excel(data: List[dict], filename: str = "report.xlsx") -> bytes:
    df = pd.DataFrame(data)
    output = io.BytesIO()
    df.to_excel(output, index=False, engine="openpyxl")
    return output.getvalue()

# Sample usage:
if __name__ == "__main__":
    # Giả lập dữ liệu tổng hợp
    data = [
        {"name": "Alice", "score": 90},
        {"name": "Bob", "score": 85},
        {"name": "Charlie", "score": 95},
    ]
    excel_bytes = generate_report_excel(data)
    with open("sample_report.xlsx", "wb") as f:
        f.write(excel_bytes)
    print("Sample Excel report generated: sample_report.xlsx")
