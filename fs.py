import docx, nbformat, os, zipfile
from PyPDF2 import PdfReader,PdfFileReader
import io
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

    def read_code_and_text_files(self, file_name: str) -> str:
        data = ""
        with open(file_name, "r") as f:
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


def extract_files(zip_path):
    file_mapping = {}

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
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
        if file_extension in (".zip", ".gz", ".tar"):
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
    with zipfile.ZipFile(input_zip_path, "r") as zip_ref:
        traverse_zip(zip_ref, file_mapping)
    return file_mapping


def read_files(input_zip_path, file_type, file_mapping):
    file_paths = file_mapping.get(file_type, [])
    print(file_paths)
    file_contents = []

    def read_from_zip(zip_ref, file_path):
        file_name = zip_ref.namelist()[0]
        # file_extension = "." + file_name.split(".")[-1]
        if file_type==".pdf":
            pdf_file = PdfReader(io.BytesIO(zip_ref.read(file_name)))
            txt = ""
            for page in pdf_file.pages:
                txt += page.extract_text() + " "
            file_contents.append(txt)
        else:
            with zip_ref.open(file_path) as file:
                file_contents.append(file.read().decode())

    with zipfile.ZipFile(input_zip_path, "r") as outer_zip_ref:
        for file_path in file_paths:
            if ".zip" in file_path:
                nested_zip_path, nested_file_path = file_path.split("\\")
                with outer_zip_ref.open(nested_zip_path) as nested_zip_file:
                    nested_zip_ref = zipfile.ZipFile(nested_zip_file)
                    read_from_zip(nested_zip_ref, nested_file_path)
            else:
                read_from_zip(outer_zip_ref, file_path)

    return file_contents


input_zip_path = 'cache/temp.zip'
file_mapping = get_file_mapping(input_zip_path)
print("============================")
print(file_mapping)
# file_conts=read_files(input_zip_path, ".txt", file_mapping)
print(read_files(input_zip_path, ".pdf", file_mapping)) 

# print(File_Reader().get_type_of_file_and_data("prototype/functions.py"))
# print(File_Reader().get_type_of_file_and_data("cache/prototype/prototype/testfiles/more tests.zip\\more tests/112103079-1.patch"))
