from bs4 import BeautifulSoup
import csv
import json
import os
from pathlib import Path
import re


def extract_string(tag):
    direct_text = ''.join(t for t in tag if isinstance(t, str))
    return re.sub(r"[^\w /]+", "", direct_text)


def convert_to_csv(shard_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    file_name = Path(shard_path).name

    header_data = []
    # obfuscate_cols = []

    with open(f"{output_folder}/{file_name}.csv", "w", newline='') as f:
        csv_writer = csv.writer(f)

        for file in os.listdir(path=shard_path):
            with open(f"{shard_path}/{file}") as f1:
                data = json.load(f1)['d'][0]

            s = BeautifulSoup(data, "lxml")

            if not header_data:
                # Gathering the headers
                header_data = [j for i in s.find("tr", {"class": "gHeader"}).find_all("a") if (j := extract_string(i))]
                csv_writer.writerow(header_data)

                # Obfuscating col names
                # obfuscate_cols = [i for i, j in enumerate(header_data) if "name" in j.lower()]

            for child in s.find_all("tr", {"class": "gData"}):
                row_data = [j for i in child.children if (j := extract_string(i))]

                # for c in obfuscate_cols:
                #     row_data[c] = hash(row_data[c])

                csv_writer.writerow(row_data)


def main():
    for file in os.listdir("shards"):
        convert_to_csv(f"shards/{file}", "preprocess")



if __name__ == "__main__":
    main()
