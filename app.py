from flask import Flask, render_template, request, session, redirect, url_for, flash, get_flashed_messages
from gpt import getGPTResp
from fs import *
from nlp import simhash_simi, get_cosine_simi, get_tfidf_simi, generate_wordcloud
from db import Database
from scrap import *
from chunk_similarity import *
from research import *
import random
from mail import *

app = Flask(__name__)
app.secret_key = '1234567890'

# temp_cache = dict()


def clear_uploads_dir(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            os.remove(file_path)
            print("Removed file:", file_path)

        for dir in dirs:
            dir_path = os.path.join(root, dir)
            clear_uploads_dir(dir_path)
            os.rmdir(dir_path)
            print("Removed directory:", dir_path)


@app.route("/home")
def home():
    if "user_id" in session:
        return render_template("home.html",checkloggedin=True)
    else:
        flash("Please log in!", "Warning")
        return redirect(url_for("login"))
        

@app.route("/",methods=["GET","POST"])
def login():
    if "user_id" not in session:
        if request.method=="POST":
            email = request.form["email"]
            token = request.form["token"]
            status= Database().verify_user(email,token)
            if(status==True):
                session["user_id"]=token
                return redirect(url_for("home"))
            else:
                flash("User with the entered Credentials was not found. Please try again.", "Warning")
        return render_template("login.html")
    else:
        flash("You are already logged in! Please logout first.", "Warning")
        return redirect(url_for("home"))

@app.route("/logout", methods=["POST"])
def logout():
    if  request.method == "POST":
        session.clear()
        return redirect(url_for("login"))
    
@app.route("/forgottoken", methods=["GET", "POST"])
def forgotToken():
    if "user_id" not in session:
        if request.method == "GET":
            return render_template("forgottoken.html")
        if request.method=="POST":
            email = request.form["email"]            

            resp = Database().get_user_access_token_from_email_id(email)

            if(resp == ""):
                flash("User doesn't exist.", "Warning")
            else:
                send_email(email, body=f"Your token is {resp}")
                flash("Please check you mail. Access token is sent on mail.", "Note")
                return redirect(url_for("login"))
            
        return render_template("forgottoken.html")


    else:
        flash("You are already logged in! Please logout first.", "Warning")
        return redirect(url_for("home"))
    
@app.route("/gptpage")
def gptpage():
    return render_template("gpt.html")


@app.route("/gpt", methods=["POST"])
def gpt():
    if "user_id" in session:
        table_rows = []
        option = request.form["option"]
        message = request.form["message"]
        message = message.lower().strip()
        resp = ""
        output = ""
        # test_ipynb_fp="./uploads/testfiles-old/Project_Report.pdf"
        # resp=File_Reader().get_type_of_file_and_data(test_ipynb_fp)["file_data"]
        # if message in temp_cache.keys():
        #     resp=temp_cache[message]
        # else:
        #     resp=getGPTResp(message,option)
        #     temp_cache[message]=resp

        resp = getGPTResp(message, option)
        resp = resp.replace("\\n", "\n")
        print(resp)
        file = request.files["file"]

        filename = file.filename
        
        user_id = session["user_id"]
        
        if not os.path.exists(f"../uploads/{user_id}"):
                os.makedirs(f"../uploads/{user_id}")

        file_path = os.path.join(f"../uploads/{user_id}", filename)
        file.save(file_path)

        if filename.endswith(".zip"):
            filename = filename.split(".")[0]

        extract_zip_recursively(file_path, f"../uploads/{user_id}")

        folder_structure = get_detailed_report_of_files(f"../uploads/{user_id}/{filename}")
        fmap = get_file_mapping(folder_structure)
        for ftype in fmap.keys():
            rel_file_paths = fmap[ftype]
            for fp in rel_file_paths:
                # fname=fp.split("/")[-1]

                # if(fname!=filename):
                #     continue
                file_content = File_Reader().get_type_of_file_and_data(fp)["file_data"]
                simi = 0
                if option == "code":
                    simi = simhash_simi(file_content, resp)
                    # simi = get_tfidf_simi(file_content, resp)
                else:
                    simi = get_cosine_simi(file_content, resp)

                table_rows.append({"file_path": fp, "similarity_score": simi})

        # clear_uploads_dir("../uploads")
        return render_template("table.html", table_rows=table_rows)
    else:
        flash("Please log in!", "Warning")
        return redirect(url_for("login"))


@app.route("/within", methods=["GET", "POST"])
def within():
    if "user_id" in session:
        if request.method == "GET":
            return render_template("withinzip.html")
        else:
            # clear_uploads_dir("../uploads")
            file = request.files["file"]
            filename = file.filename
            user_id=session["user_id"]
            
            if not os.path.exists(f"../uploads/{user_id}"):
                os.makedirs(f"../uploads/{user_id}")
            file_path = os.path.join(f"../uploads/{user_id}", filename)
            file.save(file_path)

            if filename.endswith(".zip"):
                filename = filename.split(".")[0]

            extract_zip_recursively(file_path, f"../uploads/{user_id}")

            folder_structure = get_detailed_report_of_files(f"../uploads/{user_id}/{filename}")
            fmap = get_file_mapping(folder_structure)
            superans = {}
            file_type_res="Code"
            for ftype in fmap.keys():
                rel_file_paths = fmap[ftype]
                # assuming code for all
                ans = []
                for i in range(len(rel_file_paths)):
                    file_content1 = File_Reader().get_type_of_file_and_data(
                        rel_file_paths[i]
                    )["file_data"]
                    for j in range(i + 1, len(rel_file_paths)):
                        file_content2 = File_Reader().get_type_of_file_and_data(
                            rel_file_paths[j]
                        )["file_data"]
                        subarr = []
                        file_type_res=File_Reader().isCode(rel_file_paths[j])
                        if(file_type_res=="Code"):
                            simi = (simhash_simi(file_content1, file_content2)+get_tfidf_simi(file_content1,file_content2))/2
                        elif file_type_res=="Text":
                            simi=get_cosine_simi(file_content1,file_content2)
                        else:
                            print("Unsupported File Extension")
                            simi=0
                        # simi=get_tfidf_simi(file_content1,file_content2)
                        subarr.append(simi)
                        subarr.append(rel_file_paths[i])
                        subarr.append(rel_file_paths[j])
                        ans.append(subarr)

                superans[ftype] = ans

            superans = sort_results(superans)
            return render_template("result.html", results=superans, filename=filename, inputfiletype=file_type_res)
    else:
            flash("Please log in!", "Warning")
            return redirect(url_for("login"))
       


@app.route("/local", methods=["GET", "POST"])
def local():
    if "user_id" in session:
        if request.method == "GET":
            return render_template("localzips.html")
        else:
            file1 = request.files["file1"]
            filename1 = file1.filename
            file2 = request.files["file2"]
            filename2 = file2.filename
            user_id=session["user_id"]
            
            if not os.path.exists(f"../uploads/{user_id}/1"):
                os.makedirs(f"../uploads/{user_id}/1")
            file_path1 = os.path.join(f"../uploads/{user_id}/1", filename1)
            file1.save(file_path1)

            if not os.path.exists(f"../uploads/{user_id}/2"):
                os.makedirs(f"../uploads/{user_id}/2")
            file_path2 = os.path.join(f"../uploads/{user_id}/2", filename2)
            file2.save(file_path2)
            if filename1.endswith(".zip"):
                filename1 = filename1.split(".")[0]
            if filename2.endswith(".zip"):
                filename2 = filename2.split(".")[0]
            extract_zip_recursively(file_path1, f"../uploads/{user_id}/1/")
            extract_zip_recursively(file_path2, f"../uploads/{user_id}/2/")
            folder_structure1 = get_detailed_report_of_files(f"../uploads/{user_id}/1/{filename1}")
            fmap1 = get_file_mapping(folder_structure1)
            folder_structure2 = get_detailed_report_of_files(f"../uploads/{user_id}/2/{filename2}")
            fmap2 = get_file_mapping(folder_structure2)
            superans = {}
            file_type_res="Code"

            for ftype in fmap1.keys():
                rel_file_paths1 = fmap1[ftype]
                if ftype in fmap2.keys():
                    rel_file_paths2 = fmap2[ftype]
                else:
                    rel_file_paths2 = []
                # assuming code for all
                ans = []
                for i in range(len(rel_file_paths1)):
                    file_content1 = File_Reader().get_type_of_file_and_data(
                        rel_file_paths1[i]
                    )["file_data"]
                    for j in range(len(rel_file_paths2)):
                        file_content2 = File_Reader().get_type_of_file_and_data(
                            rel_file_paths2[j]
                        )["file_data"]
                        subarr = []
                        file_type_res=File_Reader().isCode(rel_file_paths2[j])
                        if(file_type_res=="Code"):
                            simi = (simhash_simi(file_content1, file_content2)+get_tfidf_simi(file_content1,file_content2))/2
                        elif file_type_res=="Text":
                            simi=get_cosine_simi(file_content1,file_content2)
                        else:
                            print("Unsupported File Extension")
                            simi=0
                        subarr.append(simi)
                        subarr.append(rel_file_paths1[i])
                        subarr.append(rel_file_paths2[j])
                        ans.append(subarr)
                if len(ans) > 0:
                    superans[ftype] = ans

            superans = sort_results(superans)

            # clear_uploads_dir("../uploads")
            combined_name = filename1+"_"+filename2
            return render_template("result.html", results=superans, filename=combined_name, inputfiletype=file_type_res)
    else:
        flash("Please log in!", "Warning")
        return redirect(url_for("login"))

@app.route("/download/<assignment_id>/<owner_id>/<file_name>", methods=["GET", "POST"])
def download_file(assignment_id, owner_id, file_name):
    if "user_id" in session:
        if request.method == "GET":
            user_id = session["user_id"]
            print(assignment_id, ".")
            Database().download_file(assignment_record_id=assignment_id, user_id=user_id)
            Database().add_history_record_in_user_log(user_token=owner_id, file_accessed=file_name, consumer_user_token=user_id)
            return render_template("dbcompare.html", assignment_id=assignment_id, owner_id=owner_id, file_name=file_name)
        else:
            file = request.files["file"]
            filename = file.filename
            
            user_id = session["user_id"]

            if not os.path.exists(f"../uploads/{user_id}/{assignment_id}"):
                os.makedirs(f"../uploads/{user_id}/{assignment_id}")
            file_path = os.path.join(f"../uploads/{user_id}/{assignment_id}", filename)
            file.save(file_path)

            # extract_zip_recursively(file_path, "../uploads/")
            # extract_zip_recursively(file_path, f"../cache/{assignment_id}/")
            
            extract_zip_recursively(file_path, f"../uploads/{user_id}/{assignment_id}")
            extract_zip_recursively(f"../cache/{user_id}/{assignment_id}.zip", f"../cache/{user_id}/{assignment_id}/")
            folder_structure1 = get_detailed_report_of_files(f"../uploads/{user_id}/{assignment_id}")
            fmap1 = get_file_mapping(folder_structure1)
            folder_structure2 = get_detailed_report_of_files(f"../cache/{user_id}/{assignment_id}")
            fmap2 = get_file_mapping(folder_structure2)
            superans = {}
            for ftype in fmap1.keys():
                rel_file_paths1 = fmap1[ftype]
                if ftype in fmap2.keys():
                    rel_file_paths2 = fmap2[ftype]
                else:
                    rel_file_paths2 = []
                # assuming code for all
                ans = []
                for i in range(len(rel_file_paths1)):
                    file_content1 = File_Reader().get_type_of_file_and_data(
                        rel_file_paths1[i]
                    )["file_data"]
                    for j in range(len(rel_file_paths2)):
                        file_content2 = File_Reader().get_type_of_file_and_data(
                            rel_file_paths2[j]
                        )["file_data"]
                        subarr = []
                        file_type_res=File_Reader().isCode(rel_file_paths2[j])
                        if(file_type_res=="Code"):
                            simi = (simhash_simi(file_content1, file_content2)+get_tfidf_simi(file_content1,file_content2))/2
                        elif file_type_res=="Text":
                            simi=get_cosine_simi(file_content1,file_content2)
                        else:
                            print("Unsupported File Extension")
                            simi=0
                        subarr.append(simi)
                        subarr.append(rel_file_paths1[i])
                        subarr.append(rel_file_paths2[j])
                        ans.append(subarr)
                if len(ans) > 0:
                    superans[ftype] = ans

            superans = sort_results(superans)

            # clear_uploads_dir("../uploads")
            return render_template("result.html", results=superans)
    else:
        flash("Please log in!", "Warning")
        return redirect(url_for("login"))


@app.route("/database", methods=["GET", "POST"])
def database():
    if "user_id" in session:
        if request.method == "GET":
            return render_template("database.html")
        if request.method == "POST":
            branch = request.form["branch"]
            year = request.form["year"]
            semester = request.form["sem"]
            data = Database().get_unique_assignments_from_db_using_3_params(
                branch, year, semester
            )
            return render_template("assignmenttables.html", data=data)

        return render_template("database.html")
    else:
        flash("Please log in!", "Warning")
        return redirect(url_for("login"))


@app.route("/withtext", methods=["GET", "POST"])
def withtext():
    if "user_id" in session:
        if request.method == "GET":
            return render_template("withtext.html")
        else:
            text = request.form["text"]
            file = request.files["file"]
            filename = file.filename
            
            user_id = session["user_id"]

            if not os.path.exists(f"../uploads/{user_id}"):
                os.makedirs(f"../uploads/{user_id}")

            text_file_path = os.path.join(f"../uploads/{user_id}", "input_text")

            with open(text_file_path, 'w') as text_file:
                text_file.write(text)

            file_path = os.path.join(f"../uploads/{user_id}", filename)
            file.save(file_path)

            if filename.endswith(".zip"):
                filename = filename.split(".")[0]

            extract_zip_recursively(file_path, f"../uploads/{user_id}")

            folder_structure = get_detailed_report_of_files(f"../uploads/{user_id}/{filename}")
            fmap = get_file_mapping(folder_structure)
            superans = []
            file_type_res="Code"
            for ftype in fmap.keys():
                rel_file_paths = fmap[ftype]
                for i in range(len(rel_file_paths)):
                    file_content1 = File_Reader().get_type_of_file_and_data(
                        rel_file_paths[i]
                    )["file_data"]
                    subarr = []
                    file_type_res=File_Reader().isCode(rel_file_paths[i])
                    if(file_type_res=="Code"):
                        simi = (simhash_simi(file_content1, text)+get_tfidf_simi(file_content1,text))/2
                    elif file_type_res=="Text":
                        simi=get_cosine_simi(file_content1,text)
                    else:
                        print("Unsupported File Extension")
                        simi=0
                    # simi=get_tfidf_simi(file_content1,text)
                    simi = simhash_simi(file_content1, text)
                    subarr.append(simi)
                    subarr.append(rel_file_paths[i])
                    superans.append(subarr)

            superans = sorted(superans)
            print(superans)

            return render_template("textresult.html", results=superans, filename=filename, inputfiletype=file_type_res, text=text_file_path)
    else:
        flash("Please log in!", "Warning")
        return redirect(url_for("login"))

@app.route("/webresults", methods=["GET", "POST"])
def webresults():
    if "user_id" in session:
        if request.method == "GET":
            return render_template("webcheck.html")
        else:
            user_id=session["user_id"]
            topic = request.form["topic"]
            res = search_topic(topic)
            file = request.files["file"]
            filename = file.filename
            
            if not os.path.exists(f"../uploads/{user_id}"):
                os.makedirs(f"../uploads/{user_id}")
                
            file_path = os.path.join(f"../uploads/{user_id}", filename)
            file.save(file_path)

            if filename.endswith(".zip"):
                filename = filename.split(".")[0]

            extract_zip_recursively(file_path, f"../uploads/{user_id}")

            folder_structure = get_detailed_report_of_files(f"../uploads/{user_id}/{filename}")
            fmap = get_file_mapping(folder_structure)
            superans = []
            file_type_res= "Code"
            for ftype in fmap.keys():
                rel_file_paths = fmap[ftype]
                for i in range(len(rel_file_paths)):
                    file_content1 = File_Reader().get_type_of_file_and_data(
                        rel_file_paths[i]
                    )["file_data"]
                    file_type_res=File_Reader().isCode(rel_file_paths[i])
                    for j in range(len(res)):
                        text = res[j][0][0]
                        text_file_path = os.path.join(f"../uploads/{user_id}",f"url{j}" )            
                        with open(text_file_path, 'w') as url_file:
                            url_file.write(text)
                        subarr = []
                        simi = get_tfidf_simi(file_content1, text)
                        subarr.append(simi)
                        subarr.append(rel_file_paths[i])
                        subarr.append(res[j][1])
                        subarr.append(text_file_path)
                        superans.append(subarr)
                        
            superans = sorted(superans, reverse=True)

            return render_template("webresults.html", results=superans, filename=filename, inputfiletype=file_type_res)
    else:
        flash("Please log in!", "Warning")
        return redirect(url_for("login"))

# To upload assignments to the database
@app.route("/uploadassg", methods=["GET", "POST"])
def uploadassg():
    if "user_id" in session:
        if request.method == "GET":
            return render_template("uploadassg.html")
        if request.method == "POST":
            assignment_name = request.form["name"]
            branch = request.form["branch"]
            year = request.form["year"]
            div = request.form["division"]
            batch = request.form["batch"]
            semester = request.form["sem"]
            file = request.files["file"]
            filename = file.filename
            
            user_id = session["user_id"]
            
            if not os.path.exists(f"../uploads/{user_id}"):
                os.makedirs(f"../uploads/{user_id}")
                
            file_path = os.path.join(f"../uploads/{user_id}", filename)
            file.save(file_path)
            Database().create_record_and_upload_assignment(
                assignment_name, branch, year, div, batch, semester, filename, user_id
            )
            return render_template("database.html")

        return render_template("uploadassg.html")
    else:
        flash("Please log in!", "Warning")
        return redirect(url_for("login"))


@app.route("/comparefiles", methods=["GET"])
def comparefile():
    if "user_id" in session:
        req = request.args.to_dict()
        file1 = req["filepath1"]
        file2 = req["filepath2"]

        file1_content = File_Reader().get_type_of_file_and_data(file1)["file_data"]
        file2_content = File_Reader().get_type_of_file_and_data(file2)["file_data"]
        ans = get_similar_chunks(file1_content, file2_content)
    
        generate_wordcloud(file1_content,"1")
        generate_wordcloud(file2_content,"2")
        return render_template("compare_file.html", ans=ans)
    else:
        flash("Please log in!", "Warning")
        return redirect(url_for("login"))

@app.route("/researchpaper", methods=["GET", "POST"])
def researchpaper():
    if "user_id" in session:
        if request.method == "GET":
            return render_template("researchpaper.html")
        else:
            abstract = request.form["abstract"]
            print(abstract)
            res = gptTopic(abstract)
            # print("res\n",res)
            file = request.files["file"]
            filename = file.filename
            file_path = os.path.join("../uploads", filename)
            file.save(file_path)

            if filename.endswith(".zip"):
                filename = filename.split(".")[0]

            extract_zip_recursively(file_path, "../uploads/")

            folder_structure = get_detailed_report_of_files(f"../uploads/{filename}")
            fmap = get_file_mapping(folder_structure)
            superans = []
            for ftype in fmap.keys():
                rel_file_paths = fmap[ftype]
                print("Number of websites", len(res))
                for i in range(len(rel_file_paths)):
                    file_content1 = File_Reader().get_type_of_file_and_data(
                        rel_file_paths[i]
                    )["file_data"]
                    for j in range(len(res)):
                        text = res[j][0][0]
                        print(text)
                        subarr = []
                        simi = get_tfidf_simi(file_content1, text)
                        subarr.append(simi)
                        subarr.append(rel_file_paths[i])
                        print("\n\nUrl", res[j][0][1])
                        print("\n\nUrl\n", res[j])
                        print("\n\n")
                        subarr.append(res[j][1])
                        superans.append(subarr)

            superans = sorted(superans, reverse=True)
            print("\n\nsuperans\n",superans)

            return render_template("webresults.html", results=superans)
    else:
        flash("Please log in!", "Warning")
        return redirect(url_for("login"))


@app.route("/logs", methods=["GET"])
def logs():
    if "user_id" in session:
        user_id = session["user_id"]

        logs = Database().get_all_history_records_for_user(user_token=user_id)
        print(logs)
        
        return render_template("logs.html", logs=logs)
    else:
        flash("Please log in!", "Warning")
        return redirect(url_for("login"))

if __name__ == "__main__":
    clear_uploads_dir("../uploads/")
    clear_uploads_dir("../cache/")
    app.run(debug=True)
