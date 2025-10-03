import argparse
import csv
import os
import tempfile


def reorder_columns(path: str) -> None:
    new_header = [
        "data",
        "Battery",
        "Camera",
        "Performance",
        "Display",
        "Design",
        "Software",
        "Packaging",
        "Price",
        "Warranty",
        "Shop_Service",
        "Shipping",
        "General",
        "Others",
    ]

    fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(path))
    try:
        with open(path, newline="", encoding="utf-8-sig") as source, os.fdopen(
            fd, "w", newline="", encoding="utf-8"
        ) as tmp:
            reader = csv.reader(source)
            try:
                original_header = next(reader)
            except StopIteration:
                raise RuntimeError("Input CSV is empty; cannot update header.")

            writer = csv.writer(tmp)
            writer.writerow(new_header)

            for row in reader:
                row_dict = {}
                for idx, value in enumerate(row):
                    if idx < len(original_header):
                        row_dict[original_header[idx]] = value
                    else:
                        last_key = original_header[-1]
                        existing = row_dict.get(last_key, "")
                        row_dict[last_key] = f"{existing},{value}" if existing else value

                for column in original_header:
                    row_dict.setdefault(column, "")

                shipping_value = row_dict.get("shipping", row_dict.get("Shipping", ""))
                packaging_value = row_dict.get("Packaging", "")
                software_value = row_dict.get("Software", row_dict.get("software", ""))

                new_row = [
                    row_dict.get("data", ""),
                    row_dict.get("Battery", ""),
                    row_dict.get("Camera", ""),
                    row_dict.get("Performance", ""),
                    row_dict.get("Display", ""),
                    row_dict.get("Design", ""),
                    software_value,
                    packaging_value,
                    row_dict.get("Price", row_dict.get("Pricing", "")),
                    row_dict.get("Warranty", ""),
                    row_dict.get("Shop_Service", ""),
                    shipping_value,
                    row_dict.get("General", ""),
                    row_dict.get("Others", ""),
                ]

                writer.writerow(new_row)
    except Exception:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise
    os.replace(temp_path, path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Reorder Dataset.csv columns.")
    parser.add_argument("csv_path", help="Path to the CSV file to update.")
    args = parser.parse_args()
    reorder_columns(args.csv_path)


if __name__ == "__main__":
    main()
