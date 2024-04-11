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
    output = ""
    # with open("./uploads/testfiles/inodenumber-1.c","r",encoding="utf-8") as f:
    #     resp=f.read()

    if message in temp_cache.keys():
        resp=temp_cache[message]
    else:
        resp=getGPTResp(message,option)
        temp_cache[message]=resp
    
    resp=resp.replace("\\n", "\n")

    file = request.files['file']

    filename = file.filename
    file_path = os.path.join("uploads", filename)
    file.save(file_path)

    if filename.endswith(".zip"):
        extract_zip_recursively(file_path, "uploads/")

    folder_structure = Folder_Structure().get_detailed_report_of_files("uploads")
    fmap = get_file_mapping(folder_structure, "uploads")

    for ftype in fmap.keys():
        rel_file_paths = fmap[ftype]
        for fp in rel_file_paths:
            file_content = File_Reader().get_type_of_file_and_data(fp)[
                "file_data"]
            simi = 0
            if (option == 'code'):
                simi = simhash_simi(file_content, resp)
            else:
                simi = get_cosine_simi(file_content, resp)

            print(f"{fp}\t{simi}")
            output += f"{fp}\t{simi}<br>"

    return output


if __name__ == '__main__':
    app.run(debug=True)
