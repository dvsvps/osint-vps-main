#!/usr/bin/env python3
import sys
import os
import json
import pandas as pd

CSV_PATH = os.path.join(
    os.path.dirname(__file__),
    "static",
    "mobile-prefix.csv"
)

def load_prefix_data(csv_path):
    try:
        df = pd.read_csv(csv_path, dtype=str)
        df["prefix"] = df["prefix"].str.strip()
        df["operator"] = df["operator"].str.strip()
        df["circle"] = df["circle"].str.strip()
        return df.set_index("prefix")
    except Exception as e:
        print(json.dumps({"error": f"Failed to load CSV: {e}"}))
        sys.exit(1)

def lookup_number(df, number):
    num = "".join(filter(str.isdigit, number))
    if len(num) != 10:
        return {"error": "Input must be a 10-digit Indian mobile number"}
    prefix = num[:4]
    if prefix in df.index:
        row = df.loc[prefix]
        return {
            "input": num,
            "operator": row["operator"] or "Unknown",
            "circle": row["circle"] or "Unknown"
        }
    else:
        return {
            "input": num,
            "operator": "Unknown",
            "circle": "Unknown"
        }

def main():
    if len(sys.argv) != 2:
        print(json.dumps({
            "error": "Usage: run_inmobprefix.py <10-digit-mobile-number>"
        }))
        sys.exit(1)

    df = load_prefix_data(CSV_PATH)
    result = lookup_number(df, sys.argv[1])
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()

