import os
import zipfile

def extract_files(zip_path):
    file_mapping = {}

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for member in zip_ref.infolist():
            if member.is_dir():
                continue
            file_extension = os.path.splitext(member.filename)[1]
            if file_extension not in file_mapping:
                file_mapping[file_extension] = []
            file_mapping[file_extension].append(member.filename)
    
    return file_mapping

def traverse_zip(zip_ref, file_mapping, prefix=""):
    for member in zip_ref.infolist():
        if member.is_dir():
            continue
        file_extension = os.path.splitext(member.filename)[1]
        if file_extension in ('.zip', '.gz', '.tar'):
            nested_zip_path = os.path.join(prefix, member.filename)
            with zip_ref.open(member) as nested_zip_file:
                nested_zip_ref = zipfile.ZipFile(nested_zip_file)
                traverse_zip(nested_zip_ref, file_mapping, nested_zip_path)
        else:
            if file_extension not in file_mapping:
                file_mapping[file_extension] = []
            file_mapping[file_extension].append(os.path.join(prefix, member.filename))

def get_file_mapping(input_zip_path):
    file_mapping = {}
    with zipfile.ZipFile(input_zip_path, 'r') as zip_ref:
        traverse_zip(zip_ref, file_mapping)
    return file_mapping

def read_files(input_zip_path, file_type, file_mapping):
    file_paths = file_mapping.get(file_type, [])
    file_contents = []
    
    def read_from_zip(zip_ref, file_path):
        with zip_ref.open(file_path) as file:
            file_contents.append(file.read().decode())
    
    with zipfile.ZipFile(input_zip_path, 'r') as outer_zip_ref:
        for file_path in file_paths:
            if '.zip' in file_path:
                nested_zip_path, nested_file_path = file_path.split('\\')
                with outer_zip_ref.open(nested_zip_path) as nested_zip_file:
                    nested_zip_ref = zipfile.ZipFile(nested_zip_file)
                    read_from_zip(nested_zip_ref, nested_file_path)
            else:
                read_from_zip(outer_zip_ref, file_path)
    
    return file_contents


# input_zip_path = './cache/prototype.zip'
# file_mapping = get_file_mapping(input_zip_path)
# print("============================")
# # print(file_mapping[".c"])
# print(read_files(input_zip_path, ".c", file_mapping)[4])
