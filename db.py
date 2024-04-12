from pymongo import MongoClient
import gridfs
import urllib.parse
from bson import ObjectId
import datetime


class Database:
    def __init__(self) -> None:

        # CONFIG FOR CLOUD MONGODB
        """try:
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
            print(f"Error in Mongo DB Connection : {err}\n")"""

        # CONFIG FOR LOCAL MONGODB
        connection = MongoClient("mongodb://localhost:27017")
        print("Connected to MongoDB Cloud\n")
        self.db = connection["coep_hackathon"]
        self.fs = gridfs.GridFS(self.db, collection="files")

    def upload_file(self, file_name: str) -> None:
        with open("../uploads/" + file_name, "rb") as f:
            data = f.read()

        new_file_id = self.fs.put(data, filename=file_name)
        print(f"{file_name} uploaded successfully")
        return new_file_id

    def create_record_and_upload_assignment(
        self,
        name_of_assignmnet: str,
        branch: str,
        year: str,
        div: str,
        batch: str,
        semester: str,
        file_name: str,
    ) -> None:
        """
        Use this function to save the assignmnet record with given propeties in db.It will do things create a entry for assignment record and also upload your file to mongodb. Make sure that file you want to upload is in the uploads directory. Just provide the name of file that is in the uploads directory
        """

        existing_records = list(
            self.db["assignment_records"].find(
                {
                    "name_of_assignment": name_of_assignmnet,
                    "branch": branch,
                    "year": year,
                    "semester": semester,
                    "div": div,
                    "batch": batch,
                }
            )
        )

        if len(existing_records) != 0:
            print("Cannot add this record!")
            return

        new_record = {
            "name_of_assignment": name_of_assignmnet,
            "branch": branch,
            "year": year,
            "semester": semester,
            "div": div,
            "batch": batch,
            "year_of_submission": datetime.datetime.now().year,
            "file_id": self.upload_file(file_name),
            "file_name": file_name,
        }

        self.db["assignment_records"].insert_one(new_record)

        print("Record added successfully!")

    def get_unique_assignments_from_db_using_3_params(
        self, branch: str, year: str, semester: str
    ) -> list:
        """
        This function will fetch you all the unique assignment names for given 3 params
        """

        records = list(
            self.db["assignment_records"].find(
                {
                    "branch": branch,
                    "year": year,
                    "semester": semester,
                }
            )
        )

        # return list(set([item["name_of_assignment"] for item in records]))
        return records

    # def get_assignment_records_from_db_using_4_params(
    #     self, name_of_assignmnet: str, branch: str, year: str, semester: str
    # ) -> list:
    #     """
    #     This function will fetch you all the assignmnet records from the database when uou provide the given 4 params
    #     """
    #     return list(
    #         self.db["assignment_records"].find(
    #             {
    #                 "name_of_assignment": name_of_assignmnet,
    #                 "branch": branch,
    #                 "year": year,
    #                 "semester": semester,
    #             }
    #         )
    #     )

    def download_file(self, assignment_record_id) -> None:
        """
        This function will download the file corresponding to the given file id in the cache directory
        """
        helper = self.db["assignment_records"].find_one(
            {"_id": ObjectId(assignment_record_id)}
        )

        out_data = self.fs.get(helper["file_id"]).read()

        with open(f"../cache/{assignment_record_id}.zip", "wb") as f:
            f.write(out_data)

        print(f"{helper['file_name']} downloaded successfully")

    def store_gpt_response(self, query: str, response: str) -> None:
        """
        This function will store the gpt response in the Database
        """
        record = {"query": query, "response": response}
        self.db["cache_gpt_response"].insert_one(record)

        print("Record saved successfully!")

    def check_and_get_cache_response_for_query(self, query: str) -> str:
        """
        This function will check whether cache in the database has the response for given query.If it has then it returns the response else it returns ""
        """
        temp = self.db["cache_gpt_response"].find_one({"query": query})
        if temp:
            return temp["response"]
        else:
            return ""


# Database().create_record_and_upload_assignment("A1","Computer Engineering","Third Year","Div1","T1","Even Sem","Assignment 1.zip")
# Database().create_record_and_upload_assignment("A2","Electrical Engineering","Second Year","Div1","T2","Even Sem","test_dir_2.zip")
# Database().create_record_and_upload_assignment("A3","Mechanical Engineering","Second Year","Div2","T4","Odd Sem","test_dir_3.zip")
# Database().create_record_and_upload_assignment("A4","Computer Engineering","Third Year","Div1","T1","Even Sem","test_dir_4.zip")
# Database().create_record_and_upload_assignment("A5","Computer Engineering","Second Year","Div2","T2","Even Sem","test_dir_5.zip")
# Database().create_record_and_upload_assignment("A6","Computer Engineering","Third Year","Div2","T2","Even Sem","test_dir_6.zip")
# print(Database().get_assignment_records_from_db("Test 13","Computer Engineering","Third Year",))

