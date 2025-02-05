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

        dept_loc = -1
        for i, j in enumerate(headers):
            if "dept" in j.lower():
                dept_loc = i
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

                if dept_loc != -1:
                    row[dept_loc] = row[dept_loc].replace("-ARTSC", "")

                for i in range(len(row)):
                    if row[i] == "N/A":
                        row[i] = None

                course_code = re.search("[A-Z]{3}[\dABCD]\d{2}[HY]\d", row[course_loc] if course_loc != -1 else "")
                if course_code:
                    row.append(course_code.group())
                else:
                    # Fall back to just default ig
                    row.append(row[course_loc])

                writer.writerow(row)


def main():
    for i in os.listdir("preprocess"):
        postprocess(f"preprocess/{i}", f"data/{i}")

    # Manual DF Joining using Pandas
    artsci = pd.read_csv("data/artsci.csv")
    fas = pd.read_csv("data/fas.csv")
    mississaugua = pd.read_csv("data/mississaugua.csv")
    scarborough = pd.read_csv("data/scarborough.csv")

    fas = fas.rename(columns={fas.columns[0]: "Dept", fas.columns[2]: "Course"})

    mississaugua = mississaugua.rename(columns={
        mississaugua.columns[5]: "INS1",
        mississaugua.columns[6]: "INS2",
        mississaugua.columns[7]: "INS3",
        mississaugua.columns[8]: "INS4",
        mississaugua.columns[9]: "INS5",
        mississaugua.columns[10]: "INS6",
        mississaugua.columns[16]: "Number Responses",
    })

    mississaugua["Division"] = "MISSI"

    scarborough = scarborough.rename(columns={
        scarborough.columns[15]: "Number Responses",
    })

    scarborough["Division"] = "SCARB"

    combined = pd.concat([artsci, fas, mississaugua, scarborough])
    combined["Response Ratio"] = combined["Number Invited"] / combined["Number Responses"]

    cols = [
        "INS1", "INS2", "INS3", "INS4", "INS5", "INS6",
        "ARTSC1", "ARTSC2", "ARTSC3",
        "APSC001", "APSC002", "APSC003", "APSC004", "APSC005", "APSC006", "APSC007", "APSC008",
        "UTSC1", "UTSC2", "UTSC3", "Course Workload", "I would recommend this course", "I attended class", "Inspired to learn subject matter",
    ]

    all_lecs = combined
    for i in cols:
        if i not in all_lecs.columns:
            continue

        all_lecs[f"{i}_sum"] = all_lecs[i] * all_lecs["Number Responses"]

    lecture_sections_combined = all_lecs.groupby(by=["Course Code", "Year", "Term"]).sum().reset_index()
    for i in cols:
        if i not in all_lecs.columns:
            continue

        lecture_sections_combined[i] = lecture_sections_combined[f"{i}_sum"] / lecture_sections_combined["Number Responses"]
        lecture_sections_combined = lecture_sections_combined.drop(labels=[f"{i}_sum"], axis=1)
    lecture_sections_combined = lecture_sections_combined.drop(labels=["Number Responses", "Number Invited", "Response Ratio"], axis=1)

    dept_combined = all_lecs
    dept_combined = dept_combined.drop(labels=["Course", "Last Name", "Term", "Year", "Course Code"], axis=1)
    dept_combined = dept_combined.groupby(by=["Division", "Dept"]).sum().reset_index()
    for i in cols:
        if i not in all_lecs.columns:
            continue

        dept_combined[i] = dept_combined[f"{i}_sum"] / dept_combined["Number Responses"]
        dept_combined = dept_combined.drop(labels=[f"{i}_sum"], axis=1)
    dept_combined = dept_combined.drop(labels=["Number Responses", "Number Invited", "Response Ratio"], axis=1)

    lecture_sections_combined.to_csv("data/lecture_sections_combined.csv", index=False)
    dept_combined.to_csv("data/dept_combined.csv", index=False)
    combined.to_csv("data/combined.csv", index=False)


if __name__ == "__main__":
    main()
