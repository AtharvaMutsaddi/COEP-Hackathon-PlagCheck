from pymongo import MongoClient
import gridfs
import urllib.parse
from bson import ObjectId
import datetime
import pytz


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
        print("Connected to MongoDB Locally\n")
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

        return records

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

    def add_user(self, email_id: str) -> str:
        """
        This function will be used to add the user
        """
        existing_record = list(self.db["users"].find({"email_id": email_id}))

        if len(existing_record) != 0:
            print("Cannot add this record as it already exists!")
            return ""

        new_user_record_id = self.db["users"].insert_one(
            {"email_id": email_id, "logs_history": []}
        )
        pass

        # Will return the newly created user id as its access token
        return str(new_user_record_id.inserted_id)

    def verify_user(self, email_id: str, user_token_enetered: str) -> bool:
        """
        This function will verify the user based upon the access token he entered
        """

        record = self.db["users"].find_one({"email_id": email_id})

        if record is None:
            print("No user with this email id!")
            return False
        else:
            expected_user_token = str(record["_id"])
            if expected_user_token == user_token_enetered:
                print("User Verification Successfull!")
                return True
            else:
                print("User Verification Unsuccessfull!")
                return False

    def add_history_record_in_user_log(self, user_token, file_accessed) -> None:
        """
        This function will add the file accessed by the user to his logs and max limit is 2 so at any point of time it will only store the latest 2 log records
        """

        try:
            record_id = ObjectId(user_token)
            user_record = self.db["users"].find_one({"_id": record_id})
            if user_record is None:
                print("User does not exist")
                return
            else:
                utc_now = datetime.datetime.utcnow()
                ist_tz = pytz.timezone("Asia/Kolkata")
                ist_now = str(utc_now.astimezone(ist_tz))

                if len(user_record["logs_history"] == 2):
                    user_record["logs_history"] = user_record["logs_history"][1::]

                user_record["logs_history"].append(
                    {"file_accessed": file_accessed, "date_time": ist_now}
                )

                user_record.save()

        except:
            print("Error occurred")


# Database().create_record_and_upload_assignment("A1","Computer Engineering","Third Year","Div1","T1","Even Sem","Assignment 1.zip")
# Database().create_record_and_upload_assignment("A2","Electrical Engineering","Second Year","Div1","T2","Even Sem","test_dir_2.zip")
# Database().create_record_and_upload_assignment("A3","Mechanical Engineering","Second Year","Div2","T4","Odd Sem","test_dir_3.zip")
# Database().create_record_and_upload_assignment("A4","Computer Engineering","Third Year","Div1","T1","Even Sem","test_dir_4.zip")
# Database().create_record_and_upload_assignment("A5","Computer Engineering","Second Year","Div2","T2","Even Sem","test_dir_5.zip")
# Database().create_record_and_upload_assignment("A6","Computer Engineering","Third Year","Div2","T2","Even Sem","test_dir_6.zip")
# print(Database().get_assignment_records_from_db("Test 13","Computer Engineering","Third Year",))

# print(Database().add_user("apc9214@gmail.com"))
# print(Database().verify_user("apc9214@gmail.com","661a047733c591a0c812f0ad"))
