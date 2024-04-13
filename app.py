from flask import Flask, render_template, request
from gpt import getGPTResp
from fs import *
from nlp import simhash_simi, get_cosine_simi, get_tfidf_simi
from db import Database
from scrap import *
from chunk_similarity import *
import random

app = Flask(__name__)


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


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/gptpage")
def gptpage():
    return render_template("gpt.html")


@app.route("/gpt", methods=["POST"])
def gpt():
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

    file_path = os.path.join("../uploads", filename)
    file.save(file_path)

    if filename.endswith(".zip"):
        filename = filename.split(".")[0]

    extract_zip_recursively(file_path, "../uploads/")

    folder_structure = get_detailed_report_of_files(f"../uploads/{filename}")
    fmap = get_file_mapping(folder_structure)
    print(fmap)
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

            # print(f"{fp}\t{simi}")
            # output += f"{fp}\t{simi}<br>"
            table_rows.append({"file_path": fp, "similarity_score": simi})

    # clear_uploads_dir("../uploads")
    return render_template("table.html", table_rows=table_rows)


@app.route("/within", methods=["GET", "POST"])
def within():

    if request.method == "GET":
        return render_template("withinzip.html")
    else:
        # clear_uploads_dir("../uploads")
        # print("Post")
        file = request.files["file"]
        filename = file.filename

        file_path = os.path.join("../uploads", filename)
        file.save(file_path)

        if filename.endswith(".zip"):
            filename = filename.split(".")[0]

        extract_zip_recursively(file_path, "../uploads/")

        folder_structure = get_detailed_report_of_files(f"../uploads/{filename}")
        fmap = get_file_mapping(folder_structure)
        superans = {}
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
                    simi = simhash_simi(file_content1, file_content2)
                    # simi=get_tfidf_simi(file_content1,file_content2)
                    subarr.append(simi)
                    subarr.append(rel_file_paths[i])
                    subarr.append(rel_file_paths[j])
                    ans.append(subarr)

            superans[ftype] = ans

        superans = sort_results(superans)
        return render_template("result.html", results=superans)


@app.route("/local", methods=["GET", "POST"])
def local():
    if request.method == "GET":
        return render_template("localzips.html")
    else:
        file1 = request.files["file1"]
        filename1 = file1.filename
        file2 = request.files["file2"]
        filename2 = file2.filename

        if not os.path.exists("../uploads/1"):
            os.makedirs("../uploads/1")
        file_path1 = os.path.join("../uploads/1", filename1)
        file1.save(file_path1)

        if not os.path.exists("../uploads/2"):
            os.makedirs("../uploads/2")
        file_path2 = os.path.join("../uploads/2", filename2)
        file2.save(file_path2)
        if filename1.endswith(".zip"):
            filename1 = filename1.split(".")[0]
        if filename2.endswith(".zip"):
            filename2 = filename2.split(".")[0]
        extract_zip_recursively(file_path1, "../uploads/1/")
        extract_zip_recursively(file_path2, "../uploads/2/")
        folder_structure1 = get_detailed_report_of_files(f"../uploads/1/{filename1}")
        fmap1 = get_file_mapping(folder_structure1)
        print(fmap1)
        folder_structure2 = get_detailed_report_of_files(f"../uploads/2/{filename2}")
        fmap2 = get_file_mapping(folder_structure2)
        print(fmap2)
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
                    simi = simhash_simi(file_content1, file_content2)
                    # simi=get_tfidf_simi(file_content1,file_content2)
                    subarr.append(simi)
                    subarr.append(rel_file_paths1[i])
                    subarr.append(rel_file_paths2[j])
                    ans.append(subarr)
            if len(ans) > 0:
                superans[ftype] = ans

        superans = sort_results(superans)

        # clear_uploads_dir("../uploads")
        return render_template("result.html", results=superans)


@app.route("/download/<assignment_id>", methods=["GET", "POST"])
def download_file(assignment_id):
    if request.method == "GET":
        Database().download_file(assignment_id)
        return render_template("dbcompare.html", assignment_id=assignment_id)
    else:
        file = request.files["file"]
        filename = file.filename

        if not os.path.exists(f"../uploads/{assignment_id}"):
            os.makedirs(f"../uploads/{assignment_id}")
        file_path = os.path.join(f"../uploads/{assignment_id}", filename)
        file.save(file_path)

        extract_zip_recursively(file_path, "../uploads/")
        extract_zip_recursively(file_path, f"../cache/{assignment_id}/")

        folder_structure1 = get_detailed_report_of_files("../uploads")
        fmap1 = get_file_mapping(folder_structure1)
        print(fmap1)
        folder_structure2 = get_detailed_report_of_files(f"../cache/{assignment_id}")
        fmap2 = get_file_mapping(folder_structure2)
        print(fmap2)
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
                    simi = simhash_simi(file_content1, file_content2)
                    # simi=get_tfidf_simi(file_content1,file_content2)
                    subarr.append(simi)
                    subarr.append(rel_file_paths1[i])
                    subarr.append(rel_file_paths2[j])
                    ans.append(subarr)
            if len(ans) > 0:
                superans[ftype] = ans

        superans = sort_results(superans)

        # clear_uploads_dir("../uploads")
        return render_template("result.html", results=superans)
        # return {}


@app.route("/database", methods=["GET", "POST"])
def database():
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


@app.route("/withtext", methods=["GET", "POST"])
def withtext():
    if request.method == "GET":
        return render_template("withtext.html")
    else:
        text = request.form["text"]
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
            for i in range(len(rel_file_paths)):
                file_content1 = File_Reader().get_type_of_file_and_data(
                    rel_file_paths[i]
                )["file_data"]
                subarr = []
                # simi=get_tfidf_simi(file_content1,text)
                simi = simhash_simi(file_content1, text)
                subarr.append(simi)
                subarr.append(rel_file_paths[i])
                superans.append(subarr)

        superans = sorted(superans)

        return render_template("textresult.html", results=superans)


@app.route("/webresults", methods=["GET", "POST"])
def webresults():
    if request.method == "GET":
        return render_template("webcheck.html")
    else:
        topic = request.form["topic"]
        res = search_topic(topic)
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
                    print("Url", res[j][1])
                    subarr.append(res[j][1])
                    superans.append(subarr)

        superans = sorted(superans, reverse=True)

        return render_template("webresults.html", results=superans)


# To upload assignments to the database
@app.route("/uploadassg", methods=["GET", "POST"])
def uploadassg():
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

        Database().create_record_and_upload_assignment(
            assignment_name, branch, year, div, batch, semester, filename
        )
        return render_template("database.html")

    return render_template("uploadassg.html")


@app.route("/comparefiles", methods=["GET"])
def comparefile():
    req = request.args.to_dict()
    file1 = req["filepath1"]
    file2 = req["filepath2"]

    file1_content = File_Reader().get_type_of_file_and_data(file1)["file_data"]
    file2_content = File_Reader().get_type_of_file_and_data(file2)["file_data"]
    ans = get_similar_chunks(file1_content, file2_content)

    return render_template("compare_file.html", ans=ans)


if __name__ == "__main__":
    extra_dirs = ["uploads"]
    app.run(debug=True, extra_files=extra_dirs)
