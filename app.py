from flask import Flask, render_template, request
from gpt import getGPTResp
from fs import *
from nlp import simhash_simi, get_cosine_simi

app = Flask(__name__)


temp_cache = dict()


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/gptpage')
def gptpage():
    return render_template('gpt.html')


@app.route('/gpt', methods=['POST'])
def gpt():
    option = request.form['option']
    message = request.form['message']
    resp=""
    # with open("./uploads/testfiles/inodenumber-1.c","r",encoding="utf-8") as f:
    #     resp=f.read()

    if message in temp_cache.keys():
        resp=temp_cache[message]
    else:
        resp=getGPTResp(message,option)
        temp_cache[message]=resp
    
    resp=resp.replace("\\n", "\n")

    # TEMPORARILY USING HARDCODED FILE IN UPLOADS. THIS WILL BE REPLACED BY THE ACTUAL FILE NAME PATH UPLOADED
    file_name = "testfiles"
    file_path = f"uploads/{file_name}.zip"
    extract_zip_recursively(file_path, "uploads/")
    folder_structure = Folder_Structure(
    ).get_detailed_report_of_files(f"uploads/{file_name}")
    # print(folder_structure)
    fmap = get_file_mapping(folder_structure, f"uploads/{file_name}")
    for ftype in fmap.keys():
        rel_file_paths = fmap[ftype]
        for fp in rel_file_paths:
            file_content = File_Reader().get_type_of_file_and_data(fp)[
                "file_data"]
            simi = 0
            # print(file_content)
            if (option == 'code'):
                simi = simhash_simi(file_content, resp)
            else:
                simi = get_cosine_simi(file_content, resp)

            print(f"{fp}\t{simi}")

    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)
