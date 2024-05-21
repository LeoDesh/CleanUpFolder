import re
import datetime

# pattern = re.compile(r"(DEBUG:Folder )(.+)( has)")
# DEBUG:File
""" with open(filename) as f:
    text = f.readlines()
    for line in text:
        matches = pattern.finditer(line)
        for match in matches:
            print(match, match.start(), match.end()) """


def read_file(filename: str):
    with open(filename) as f:
        text = f.read()
    return text


def log_moved_files(text: str):
    pattern = re.compile(r"(DEBUG:File )(.+)( has been successfully moved to )(.+)!")
    matches = pattern.finditer(text)
    file_list = []
    for match in matches:
        file_list.append([match.group(2), match.group(4)])
    return file_list


def log_created_folders(text: str):
    pattern = pattern = re.compile(r"(DEBUG:Folder )(.+)( has)")
    matches = pattern.finditer(text)
    folder_list = []
    for match in matches:
        folder_list.append(match.group(2))
    return folder_list


def main():
    # filename = "sample.log"
    date_now = str(datetime.datetime.now())[0:19]
    print("sample_" + str(datetime.datetime.now())[0:19] + ".log")
    date_part = str(datetime.datetime.now())[0:19].replace(" ", "_").replace(":", "_")
    date_str = "2024-04-28_12_02_29"
    format = "%Y-%m-%d_%H_%M_%S"
    print(
        max(
            datetime.datetime.strptime(date_part, format),
            datetime.datetime.strptime(date_str, format),
        )
    )


if __name__ == "__main__":
    main()
