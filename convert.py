import os
import pandas as pd
import json
import numpy as np

# Folder chứa các file XLSX
INPUT_DIR = "C://Users//admin//Documents//SAP"
# Folder output chứa JSON
OUTPUT_DIR = "C://Users//admin//Documents//SAP//output_json"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def convert_all_xlsx_to_json():
    for filename in os.listdir(INPUT_DIR):
        if filename.lower().endswith(".xlsx"):
            xlsx_path = os.path.join(INPUT_DIR, filename)
            
            print(f"Đang xử lý: {filename}")

            # Load file
            df = pd.read_excel(xlsx_path)

            # Convert NaN → "NaN"
            df = df.replace({np.nan: "NaN"})

            # Save JSON
            json_filename = filename.replace(".xlsx", ".json")
            json_path = os.path.join(OUTPUT_DIR, json_filename)

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(df.to_dict(orient="records"), f, ensure_ascii=False)
            
            print(f"→ Đã tạo: {json_filename}")

    print("\nHoàn tất convert!")

if __name__ == "__main__":
    convert_all_xlsx_to_json()
