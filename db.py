from pymongo import MongoClient
import gridfs
import urllib.parse
from bson import ObjectId
import datetime


class Database:
    def __init__(self) -> None:
        try:
            username = "apc9214"
            password = "Anushree@2011"
            dbname = "coep_hackathon"

            username = urllib.parse.quote_plus(username)
            password = urllib.parse.quote_plus(password)

            connection_string = f"mongodb+srv://{username}:{password}@cluster0.lkcgxrb.mongodb.net/{dbname}?retryWrites=true&w=majority&appName=Cluster0"

            connection = MongoClient(connection_string)
            print("Connected to MongoDB Cloud\n")

            self.db = connection["coep_hackathon"]
            self.fs = gridfs.GridFS(self.db, collection="files")

        except Exception as err:
            print(f"Error in Mongo DB Connection : {err}\n")

    def upload_file(self, file_name: str) -> None:
        with open("uploads/" + file_name, "rb") as f:
            data = f.read()

        new_file_id = self.fs.put(data, filename=file_name)
        print(f"{file_name} uploaded successfully")
        return new_file_id

    def create_record_and_upload_assignment(
        self,
        name_of_assignmnet: str,
        branch: str,
        year: str,
        semester: str,
        file_name: str,
    ) -> None:
        """
        Use this function to save the assignmnet record with given propeties in db.It will do things create a entry for assignment record and also upload your file to mongodb. Make sure that file you want to upload is in the uploads directory. Just provide the name of file that is in the uploads directory
        """
        new_record = {
            "name_of_assignment": name_of_assignmnet,
            "branch": branch,
            "year": year,
            "semester": semester,
            "year_of_submission": datetime.datetime.now().year,
            "file_id": self.upload_file(file_name),
            "file_name": file_name,
        }

        self.db["assignment_records"].insert_one(new_record)

    def get_all_assignment_records_from_db(self):
        """
        This function will fetch you all the assignmnet records from the database
        """
        ans = []
        response = self.db["assignment_records"].find({})
        for record in response:
            ans.append(record)
        return ans

    def download_file(self, assignment_record_id) -> None:
        """
        This function will download the file corresponding to the given file id in the cache directory
        """
        helper = self.db["assignment_records"].find_one(
            {"_id": ObjectId(assignment_record_id)}
        )

        out_data = self.fs.get(helper["file_id"]).read()

        with open("cache/" + helper["file_name"], "wb") as f:
            f.write(out_data)

        print(f"{helper['file_name']} downloaded successfully")


# Database().create_record_and_upload_assignment("Data Science Book Upload Assignmnet","Computer Engineering","Third Year","Even Semester","DSCI_book.pdf")
# Database().download_file('661622a6c1c17b17a1088b64')
# print(Database().get_all_assignment_records_from_db())