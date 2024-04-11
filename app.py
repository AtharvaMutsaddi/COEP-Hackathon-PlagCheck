from flask import Flask, render_template, request
from gpt import getGPTResp
from fs import *
from nlp import simhash_simi, get_cosine_simi

app = Flask(__name__)


# temp_cache = dict()


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
    # test_ipynb_fp="./uploads/testfiles-old/Project_Report.pdf"
    # resp=File_Reader().get_type_of_file_and_data(test_ipynb_fp)["file_data"]
    # if message in temp_cache.keys():
    #     resp=temp_cache[message]
    # else:
    #     resp=getGPTResp(message,option)
    #     temp_cache[message]=resp
    
    resp=getGPTResp(message,option)
    resp=resp.replace("\\n", "\n")
    print(resp)
    file = request.files['file']

    filename = file.filename
    
    file_path = os.path.join("../uploads", filename)
    file.save(file_path)

    if filename.endswith(".zip"):
        filename=filename.split(".")[0]
        
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

@app.route("/within",methods=["GET","POST"])
def within():
    if request.method=="GET":
        return render_template('withinzip.html')
    else:
        print("Post")
        file = request.files['file']
        filename = file.filename
    
        file_path = os.path.join("../uploads", filename)
        file.save(file_path)

        if filename.endswith(".zip"):
            filename=filename.split(".")[0]
            
        extract_zip_recursively(file_path, "../uploads/")

        folder_structure = get_detailed_report_of_files(f"../uploads/{filename}")
        fmap = get_file_mapping(folder_structure)
        superans={}
        for ftype in fmap.keys():
            rel_file_paths = fmap[ftype]
            # assuming code for all
            ans=[]
            for i in range(len(rel_file_paths)):
                file_content1=File_Reader().get_type_of_file_and_data(rel_file_paths[i])["file_data"]
                for j in range(i+1,len(rel_file_paths)):
                    file_content2=File_Reader().get_type_of_file_and_data(rel_file_paths[j])["file_data"]
                    subarr=[]
                    simi=simhash_simi(file_content1,file_content2)
                    subarr.append(simi)
                    subarr.append(rel_file_paths[i])
                    subarr.append(rel_file_paths[j])
                    ans.append(subarr)
            
            superans[ftype]=ans
        
        print(superans)
        return superans       
@app.route("/local",methods=["GET","POST"])
def local():
    if request.method=="GET":
        return render_template('localzips.html')
    else:
        print("Post")
        file = request.files['file']
        filename = file.filename
    
        file_path = os.path.join("../uploads", filename)
        file.save(file_path)

        if filename.endswith(".zip"):
            filename=filename.split(".")[0]
            
        extract_zip_recursively(file_path, "../uploads/")

        folder_structure = get_detailed_report_of_files(f"../uploads/{filename}")
        print(folder_structure)
        fmap = get_file_mapping(folder_structure)
        print(fmap)
        superans={}
        for ftype in fmap.keys():
            rel_file_paths = fmap[ftype]
            # assuming code for all
            ans=[]
            for i in range(len(rel_file_paths)):
                file_content1=File_Reader().get_type_of_file_and_data(rel_file_paths[i])["file_data"]
                for j in range(i+1,len(rel_file_paths)):
                    file_content2=File_Reader().get_type_of_file_and_data(rel_file_paths[j])["file_data"]
                    subarr=[]
                    simi=simhash_simi(file_content1,file_content2)
                    subarr.append(simi)
                    subarr.append(rel_file_paths[i])
                    subarr.append(rel_file_paths[j])
                    ans.append(subarr)
            
            superans[ftype]=ans
        
        print(superans)
        return superans        
if __name__ == '__main__':
    extra_dirs = ['uploads']
    app.run(debug=True, extra_files=extra_dirs)
