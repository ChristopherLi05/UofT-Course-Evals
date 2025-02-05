import csv
import os
import pathlib
import re
import pandas as pd


def postprocess(input_path, output_path):
    with open(input_path) as f1:
        data = csv.reader(f1)

        headers = next(data)

        name_loc = -1
        if "First Name" in headers:
            name_loc = headers.index("First Name")
            headers.pop(name_loc)

        orig_course_code = -1
        for i, j in enumerate(headers):
            if "course code" in j.lower():
                orig_course_code = i
                headers.pop(orig_course_code)
                break

        course_loc = -1
        for i, j in enumerate(headers):
            if "course" in j.lower():
                course_loc = i
                break

        headers.append("Course Code")

        os.makedirs(pathlib.Path(output_path).parent, exist_ok=True)
        with open(output_path, "w", newline="") as f2:
            writer = csv.writer(f2)

            writer.writerow(headers)

            for row in data:
                if name_loc != -1:
                    row.pop(name_loc)

                if orig_course_code != -1:
                    row.pop(orig_course_code)

                for i in range(len(row)):
                    if row[i] == "N/A":
                        row[i] = None

                course_code = re.search("[A-Z]{3}\d{3}[HY]\d", row[course_loc] if course_loc != -1 else "")
                if course_code:
                    row.append(course_code.group())
                else:
                    row.append(None)

                writer.writerow(row)


def main():
    for i in os.listdir("preprocess"):
        postprocess(f"preprocess/{i}", f"data/{i}")

    # Manual DF Joining using Pandas
    artsci = pd.read_csv("data/artsci.csv")
    fas = pd.read_csv("data/fas.csv")
    mississaugua = pd.read_csv("data/mississaugua.csv")
    scarborough = pd.read_csv("data/scarborough.csv")

    fas = fas.rename(columns={fas.columns[0]: "Dept", fas.columns[1]: "Course"})

    mississaugua = mississaugua.rename(columns={
        mississaugua.columns[5]: "INS1",
        mississaugua.columns[6]: "INS2",
        mississaugua.columns[7]: "INS3",
        mississaugua.columns[8]: "INS4",
        mississaugua.columns[9]: "INS5",
        mississaugua.columns[10]: "INS6",
        mississaugua.columns[16]: "Number Responses",
    })

    scarborough = scarborough.rename(columns={
        scarborough.columns[15]: "Number Responses",
    })

    combined = pd.concat([artsci, fas, mississaugua, scarborough])
    combined.to_csv("data/combined.csv", index=False)


if __name__ == "__main__":
    main()
