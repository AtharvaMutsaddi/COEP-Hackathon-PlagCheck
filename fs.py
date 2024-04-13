import docx, nbformat, os, zipfile
from PyPDF2 import PdfReader, PdfFileReader
import io
from pathlib import Path

programming_file_extensions = [
    ".txt",  # Text Files
    ".py",  # Python
    ".c",  # C
    ".cpp",  # C++
    ".c++",  # C++
    ".java",  # Java
    ".js",  # JavaScript
    ".html",  # HTML
    ".css",  # CSS
    ".php",  # PHP
    ".rb",  # Ruby
    ".swift",  # Swift
    ".kt",  # Kotlin
    ".pl",  # Perl
    ".go",  # Go
    ".ts",  # TypeScript
    ".lua",  # Lua
    ".scala",  # Scala
    ".rs",  # Rust
    ".sh",  # Shell Script
    ".asm",  # Assembly
    ".r",  # R
    ".sql",  # SQL
    ".dart",  # Dart
    ".jsx",  # JSX
    ".tsx",  # TSX
    ".yaml",  # YAML
    ".json",  # JSON
    ".xml",  # XML
    ".ini",  # INI
    ".cfg",  # Configuration files
    ".conf",  # Configuration files
    ".log",  # Log files
    ".md",  # Markdown
    ".MD",  # Markdown
    ".h",  # Header files (C/C++)
    ".hpp",  # Header files (C++)
    ".patch",  # Diff files
]


class File_Reader:
    """🔵 Utilise this class for reading text data from different files.
     Usage : File_Reader().get_type_of_file_and_data(filepath).
    It will return you the list with item[0] as extension and item[1] as data in str format.

    🔴 Make sure that whenever you give file path it should have seperator as / and not \ so that their is no conflict between escape characters
    """

    def __init__(self) -> None:
        pass

    def get_type_of_file_and_data(self, filepath: str) -> dict:
        file_name = filepath.split("/")[-1]
        file_extension = "." + file_name.split(".")[-1]

        ans = {"file_type": file_extension, "file_data": ""}

        if file_extension in programming_file_extensions:
            ans["file_data"] = self.read_code_and_text_files(filepath)
        elif file_extension == ".docx":
            ans["file_data"] = self.read_docx_files(filepath)
        elif file_extension == ".ipynb":
            ans["file_data"] = self.read_ipynb_files(filepath)
        elif file_extension == ".pdf":
            ans["file_data"] = self.read_pdf_files(filepath)

        return ans

    def isCode(self, file_path) -> str:
        """
        This function will return Code_Text for code and text files or Documents for writeups.
        """
        curr_ext = Path(file_path).suffix
        if curr_ext in [".docx", ".pdf", ".txt"]:
            return "Text"
        elif curr_ext in programming_file_extensions or curr_ext == ".ipynb":
            return "Code"
        else:
            return "Unsupported"

    def read_code_and_text_files(self, file_name: str) -> str:
        data = ""
        with open(file_name, "r", encoding="utf-8") as f:
            data = f.read()

        return data.replace("\\n", "\n")

    def read_docx_files(self, file_name: str) -> str:
        doc = docx.Document(file_name)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)

        return "\n".join(full_text)

    def read_ipynb_files(self, file_name: str) -> str:
        ans = ""
        with open(file_name, "r", encoding="utf-8") as f:
            notebook = nbformat.read(f, as_version=4)

            for cell in notebook.cells:
                ans += cell.source + "\n"

        return ans

    def read_pdf_files(self, file_name: str) -> str:
        reader = PdfReader(file_name)
        txt = ""
        for page in reader.pages:
            txt += page.extract_text() + "\n"

        return txt


def get_detailed_report_of_files(folder) -> list:
    all_files = []

    for dirpath, _, filenames in os.walk(folder):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            file_path = Path(file_path).as_posix()
            all_files.append(file_path)

    return all_files


def extract_zip_recursively(zip_file, extract_to):
    if not os.path.exists(extract_to):
        os.makedirs(extract_to)

    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(extract_to)

        for item in zip_ref.infolist():
            if item.is_dir():
                continue

            if item.filename.endswith(".zip"):
                nested_zip_path = os.path.join(extract_to, item.filename)
                nested_extract_to = os.path.join(
                    extract_to, os.path.splitext(item.filename)[0]
                )

                extract_zip_recursively(nested_zip_path, nested_extract_to)

                os.remove(nested_zip_path)


def get_file_mapping(all_files: list):
    ans = {}
    for item in all_files:
        curr_ext = Path(item).suffix

        if curr_ext not in ans:
            ans[curr_ext] = []
            
        ans[curr_ext].append(item)
    return ans

def sort_results(results: dict):
    sorted_results = {}
    for key in results.keys():
        sorted_results[key] = sorted([x for x in results[key] if x[1] != x[2]], key=lambda x: x[0], reverse=True)
    return sorted_results


# input_zip_path = 'cache/temp.zip'
# file_mapping = get_file_mapping(input_zip_path)
# print("============================")
# print(file_mapping)
# # file_conts=read_files(input_zip_path, ".txt", file_mapping)
# print(read_files(input_zip_path, ".pdf", file_mapping))

# print(File_Reader().get_type_of_file_and_data("prototype/functions.py"))


# extract_zip_recursively("testcases/Assignments/Assignment 1.zip", "cache/")
# folder_structure=get_detailed_report_of_files("uploads/Assignment 1")
# print(folder_structure)
# print(File_Reader().get_type_of_file_and_data("./cache/Assignment 2/112103015/Documents/Project_Report.pdf"))
# fmap=get_file_mapping(folder_structure)
# print(fmap)
# test_file_path=fmap["py"][0]
# print(File_Reader().get_type_of_file_and_data(test_file_path))
# extract_zip_recursively("testing/Assignments/Assignment 2.zip", "cache/")
# print(Folder_Structure().get_detailed_report_of_files("cache/Assignment 2"))

# extract_zip_recursively("uploads/testfiles/Assignment 2.zip","cache/")
# ls = get_detailed_report_of_files("cache/")
# print(get_file_mapping(ls))
""" extract_zip_recursively("uploads/testfiles/Assignment 2.zip", "cache/")
ls = get_detailed_report_of_files("cache/")
print(get_file_mapping(ls)) """

# print(File_Reader().identify_type_of_given_file("cache/db.py"))
# print(File_Reader().identify_type_of_given_file("cache/Assignment 2/Assignment 2/112103015/Documents/Project_Report.pdf"))
# extract_zip_recursively("../cache/6618e96909265674e7dbd449.zip", "../cache/6618e96909265674e7dbd449/")