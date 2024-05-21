import os
import re
import time
import logging

PATH = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = "sample.log"
TRANS_DICT = {"ending": True, "like": False}


class NoFilesFound(Exception):
    pass


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(LOG_FILE)
formatter = logging.Formatter("%(asctime)s:%(funcName)s:%(levelname)s:%(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

VERT_DEL = "|"
HOR_DEL = "_"
SHIFT = " "
AMOUNT = 2


def creation_time(path: str):
    ti_m = os.path.getctime(path)
    m_ti = time.ctime(ti_m)
    t_obj = time.strptime(m_ti)
    return time.strftime("%Y-%m-%d %H:%M:%S", t_obj)


def modification_time(path: str):
    ti_m = os.path.getmtime(path)
    m_ti = time.ctime(ti_m)
    t_obj = time.strptime(m_ti)
    return time.strftime("%Y-%m-%d %H:%M:%S", t_obj)


def split_name(filename):
    names_split = filename.split(".")
    if len(names_split) > 1:
        ending = names_split[-1]
    else:
        ending = ""
    return ending


def folder_struct(path: str):
    for folder in os.scandir(path):
        if folder.is_dir():
            folder_struct(path + "\\" + folder.name)
            print(folder.name)


def tree_rep(folder_dict: dict, base_str: str = ""):
    if not base_str:
        base_str = "root_folder \n"
    res = rec_tree_str(folder_dict, 0)
    return base_str + res


def rec_tree_str(folder_dict: dict, depth: int):
    final_str, level_str = "", ""
    if folder_dict:
        for key, item in folder_dict.items():
            if key != "Files":
                act_level_str = (
                    " "
                    + "".join(VERT_DEL + AMOUNT * SHIFT for _ in range(depth))
                    + VERT_DEL
                    + HOR_DEL
                    + "\U0001f4c1 "
                    + key
                    + "\n"
                )
                deep_str = rec_tree_str(item, depth + 1)
                final_str = final_str + act_level_str + deep_str
            else:
                for filename in item:
                    file_str = " " + "".join(
                        VERT_DEL + AMOUNT * SHIFT for _ in range(depth)
                    )
                    file_str = (
                        file_str
                        + VERT_DEL
                        + 2 * HOR_DEL
                        + "\U0001f4c4 "
                        + filename
                        + "\n"
                    )
                    level_str = level_str + file_str
        return final_str + level_str
    else:
        return ""


def check_folder(path: str) -> bool:
    for f in os.scandir(path):
        if f.is_dir():
            return True
    return False


def check_file(path: str) -> bool:
    for f in os.scandir(path):
        if not f.is_dir():
            return True
    return False


def folder_structure_json(path: str):
    if check_folder(path):
        level_dict = {}
        for f in os.scandir(path):
            if f.is_dir():
                curr_dict = folder_structure_json(path + "\\" + f.name)
                if curr_dict is None:
                    level_dict[f.name] = {}
                else:
                    level_dict[f.name] = curr_dict
            else:
                level_dict.setdefault("Files", []).append(f.name)
        return level_dict
    else:
        if check_file(path):
            level_dict = {"Files": []}
            for f in os.scandir(path):
                if not f.is_dir():
                    level_dict["Files"].append(f.name)
            return level_dict
        else:
            return None


def read_config(filename: str, delimiter: str = ","):
    warning_list = []
    res_dict = {}
    with open(filename) as f:
        for index, line in enumerate(f.readlines()):
            line = line.replace("\n", "")
            line_arr = line.split(delimiter)
            if len(line_arr) == 2:
                key, value = line_arr
                res_dict[key] = value
            elif len(line_arr) != 2 and line:
                warning_list.append([index + 1, len(line_arr)])
    if warning_list:
        print(f"Warning: {len(warning_list)} irregular inputs found")
        for note in warning_list:
            line_num, length = note
            if length < 2:
                print(f"too few values ({length}) provided in line {line_num}")
            elif length > 2:
                print(f"too many values ({length}) provided in line {line_num}")
    return res_dict


def schema_packing(root: str, res_dict: dict, ending: bool):
    file_dict = {}
    file_list = []
    index = 0
    for file in os.scandir(root):
        if not file.is_dir():
            file_list.append(file.name)
            index += 1
            for key, value in res_dict.items():
                if ending:
                    if file.name.split(".")[-1] == key:
                        file_dict.setdefault(
                            file.name, [root + "\\" + value + "\\" + file.name, 0]
                        )
                        file_dict[file.name][1] += 1
                        if file_dict[file.name][1] > 1:
                            logger.warning(
                                f"File {file.name} fits to multiple folders!"
                            )

                else:
                    if file.name[: -len(file.name.split(".")[-1])].find(key) > -1:
                        file_dict.setdefault(
                            file.name, [root + "\\" + value + "\\" + file.name, 0]
                        )
                        file_dict[file.name][1] += 1
                        if file_dict[file.name][1] > 1:
                            logger.warning(
                                f"File {file.name} fits to multiple folders!"
                            )

    for file in file_list:
        if file not in file_dict:
            logger.warning(f"File {file} does not fit to any folder!")
    return file_dict


def construct_full_paths(folder_dict: dict, root_folder: str, file_list: list = None):
    if not file_list:
        file_list = []
    for key, items in folder_dict.items():
        if key == "Files":
            for name in items:
                file_list.append(root_folder + "\\" + name)
        else:
            construct_full_paths(items, root_folder + "\\" + key, file_list)
    return file_list


def future_folder_list(root: str, target_dict: dict):
    return [root + "\\" + item for _, item in target_dict.items]


def folder_to_create(root: str, needed_folders: list):
    struc = folder_structure_json(root)
    key_names_set = set(struc.keys())
    needed_folders_set = set(needed_folders)
    return needed_folders_set - key_names_set


def perform_clean_up(root: str, target_dict: dict, ending: bool):
    struc = folder_structure_json(root)
    key_names_set = set(struc.keys())
    if "Files" in key_names_set:
        file_list = set(struc["Files"])
    else:
        raise NoFilesFound("In path {root} there are no files to be put in folders!")

    target_file_list = schema_packing(root, target_dict, ending)
    # print(target_file_list)
    needed_folders = [item[0].split("\\")[-2] for _, item in target_file_list.items()]
    ##Folder Creation
    folders = folder_to_create(root, needed_folders)
    for folder in folders:
        folder_name = root + "\\" + folder
        os.mkdir(folder_name)
        logger.debug(f"Folder {folder_name} has been created!")

    target_file_keys = list(target_file_list.keys())
    for file_name, items in target_file_list.items():
        if not os.path.isfile(items[0]):
            os.replace(root + "\\" + file_name, items[0])
            logger.debug(
                f"File {root}\\{file_name} has been successfully moved to {items[0]}!"
            )
        else:
            target_file_keys.remove(file_name)
            logger.warning(f"File {file_name} with {items[0]} already exists!")
    file_list_set = set(file_list) - set(target_file_keys)
    print(file_list_set)
    # file_list = root + "\\" + file_list


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


def reverse_clean_up():
    with open(LOG_FILE) as f:
        text = f.read()
    file_list = log_moved_files(text)
    folder_list = log_created_folders(text)
    for trg_file, src_file in file_list:
        os.replace(src_file, trg_file)

    for folder in folder_list:
        os.rmdir(folder)
    log_file_restart()


def log_file_restart():
    with open(LOG_FILE, "w"):
        pass


def get_log_file(path: str):
    file_list = []
    for file in os.scandir(path):
        if file.name.find(".log") > -1 and file.name.find("sample_") > -1:
            file_list.append(file)
    # raise Exception("No Log File Found!")


# Split the full 'folder_structure_json' into two JSONs -> Files + Folders. Then get from both the representation string and afterwards put the Files Rep below the Folders rep.
def preview_changes(path: str, target_dict: dict, sort_type: str):
    struc = folder_structure_json(path)
    key_names_set = set(struc.keys())
    if "Files" in key_names_set:
        file_list = set(struc["Files"])
    else:
        raise NoFilesFound("In path {path} there are no files to be put in folders!")
    current_path = {"Files": list(file_list)} | {
        key: {} for key in key_names_set if key != "Files"
    }

    target_file_list = schema_packing(path, target_dict, TRANS_DICT[sort_type])
    needed_folders = [item[0].split("\\")[-2] for _, item in target_file_list.items()]
    folders = folder_to_create(path, needed_folders)

    target_file_keys = list(target_file_list.keys())
    for file_name, items in target_file_list.items():
        if os.path.isfile(items[0]):
            target_file_keys.remove(file_name)

    file_list_set = set(file_list) - set(target_file_keys)
    print(tree_rep(current_path))

    new_path = {
        "Files": list(file_list_set),
    }
    print(target_file_keys)
    final_dict = {}
    for file in target_file_keys:
        for folder in folders:
            if target_file_list[file][0].find(path + "\\" + folder) > -1:
                final_dict.setdefault(folder, {"Files": []})
                final_dict[folder]["Files"].append(file)
    end_path = (
        new_path
        | final_dict
        | {key: {} for key in key_names_set if key != "Files" and key not in folders}
    )

    return tree_rep(end_path)


def initiate_clean_up():
    print("Initiating Folder Manager!")
    print(
        "With the help of the Folder Manager you can clean up a folder by putting files into a specified folder!"
    )
    print(
        'You can either specify the destinations of your files via their endings, e.g. all files with ending ".exe" will go to e.g. a folder "Executeables"'
    )
    print(
        'Or you can also choose that files which contain e.g. "docu" in their name will be moved to e.g. a folder "Documents"'
    )
    print('This can be provided via the inputs "schema_dict" and "sorter".')
    print(
        'It is recommended to check out the examples first. Examples can be found in the folder "Example_Ending" and "Example_Like".'
    )
    print(
        'In each of these two folders there are two folders: "Folder_Before" and "Folder_After" and a text file: "schema.txt"'
    )
    print(
        'Example_Ending: If you provide the path of "Folder_Before", the path of text_file "schema.txt" and the input "ending" the folder "Folder_Before" will look like the "Folder_After"  '
    )
    print(
        'Example_Like: If you provide the path of "Folder_Before", the path of text_file "schema.txt" and the input "like" the folder "Folder_Before" will look like the "Folder_After"  '
    )
    input("Press Enter to continue!")
    while True:
        print("The following possibilities are now available")
        print('1.) Walk through tutorial: "Example_Like"')
        print('2.) Walk through tutorial: "Example_Ending"')
        print(
            "3.) Use the FolderManager. Recommended to walk through the tutorials first!"
        )
        print("4.) Quit")
        while True:
            choice = input("Please provide your input: ")
            if choice in ("1", "2", "3", "4"):
                break
            else:
                print(f"{choice} is an invalid input. Choose a number between 1 and 4.")
        match choice:
            case "1":
                print("1")
            case "2":
                print("2")
            case "3":
                folder_manager()
            case "4":
                print("Exiting. . .")


def folder_insert():
    while True:
        folder_path = input("Insert the path to the folder you want to clean up!: ")
        if os.path.isdir(folder_path):
            break
        else:
            print(f"The provided folder {folder_path} does not exist")
    return folder_path


def schema_insert():
    while True:
        schema_path = input("Insert the path to the schema_dictionary!: ")
        if os.path.isfile(schema_path) and schema_path.split(".")[-1] == "txt":
            break
        else:
            print(
                f"The provided schema dictionary {schema_path} does not exist or does not have the correct file ending (.txt)"
            )
    return schema_path


def sorting_insert():
    while True:
        sorting = input("Insert the sorting choice![like,ending]: ")
        if sorting in ("like", "ending"):
            break
        else:
            print(f"The provided sorting option {sorting} is not valid!")
    return sorting


def preview_choice(folder_path: str, target_dict: dict, sorting: str):
    while True:
        choice = input(
            "Do you want to preview the changes for executing the clean up?[y/n]: "
        )
        if choice == "n":
            break
        elif choice == "y":
            print("After the cleanup your folder will look like:")
            print(preview_changes(folder_path, target_dict, sorting))
            time.sleep(2.0)
            break
        else:
            print(f"The provided choice {choice} is not valid!")


def cleanup_choice(folder_path: str, target_dict: dict, sorting: str):
    while True:
        choice = input("Do you want to execute this changes?[y/n]: ")
        if choice == "n":
            break
        elif choice == "y":
            perform_clean_up(folder_path, target_dict, TRANS_DICT[sorting])
            return True
        else:
            print(f"The provided choice {choice} is not valid!")
    return False


def revert_changes():
    while True:
        choice = input("Do you want to revert the changes?[y/n]: ")
        if choice == "n":
            break
        elif choice == "y":
            reverse_clean_up()
        else:
            print(f"The provided choice {choice} is not valid!")
    return False


def folder_manager():
    print("Welcome to using the Folder Manager!")
    folder_path = folder_insert()
    schema_path = schema_insert()
    sorting = sorting_insert()
    struc = folder_structure_json(folder_path)
    target_dict = read_config(schema_path)
    current_folder_structure = tree_rep(
        struc, f"\U0001f4c1 {folder_path.split('\\')[0]} \n"
    )
    print("Your provided folder has the following structure!")
    print(current_folder_structure)
    print(sorting)
    print(TRANS_DICT[sorting])
    preview_choice(folder_path, target_dict, sorting)
    choice = cleanup_choice(folder_path, target_dict, sorting)
    if choice:
        revert_changes()
    else:
        print("Exiting Folder Manager . . .")


def example_like():
    target_dict = read_config("schema_like.txt", ",")
    path = PATH + "\\Example_Like\\Folder_Before"
    struc = folder_structure_json(path)
    after_folder_view = preview_changes(path, target_dict, "like")
    before_folder_view = tree_rep(struc, "\U0001f4c1 Folder_Before \n")
    print(f"Currently the folder looks like: \n {before_folder_view}")
    print(f"It will look like: \n {after_folder_view}")


def main():
    initiate_clean_up()
    # spaceholder


if __name__ == "__main__":
    main()
