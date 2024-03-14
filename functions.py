from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
inference_api_key="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"

from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import os
import Levenshtein

directory_path = "./testfiles"

embeddings_model = HuggingFaceInferenceAPIEmbeddings(
    api_key=inference_api_key, model_name="sentence-transformers/all-mpnet-base-v2"
)

sample_data = []

# text_files = [file for file in os.listdir(directory_path) if file.endswith(".txt")]
text_files = [file for file in os.listdir(directory_path)]
for txt_file in text_files:
        file_path = os.path.join(directory_path, txt_file)
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
            sample_data.append(text)

def get_similar_lines(lines1,lines2):
    similar_lines = []
    for i, line1 in enumerate(lines1, start=1):
        for j, line2 in enumerate(lines2, start=1):
            if len(line1.strip()) == 0 or len(line2.strip()) == 0:
                continue
            similarity = Levenshtein.ratio(line1.strip(), line2.strip())
            if similarity >= 0.8:
                print(f"Similar lines found: \n{line1.strip()} \n{line2.strip()} \nSimilarity: {similarity}\n")
                similar_lines.append((i,line1.strip(),j, line2.strip(), similarity)) 
                
    return similar_lines

def text_similarity(text1, text2):
    print("Text 1: ", text1)    
    print("Text 2: ", text2)    
    data = list()
    data.append(text1)
    data.append(text2)
    lines1 = text1.split("\n")
    lines2 = text2.split("\n")
    print(lines1)
    print(lines2)
    similar_lines =get_similar_lines(lines1,lines2)
    embeddings = embeddings_model.embed_documents(data)
    cs_mat = cosine_similarity(embeddings)
    print(cs_mat)
    return (cs_mat[0][1], similar_lines)

def check_similarity(text):
    data = list()
    data.extend(sample_data)
    data.append(text)
    embeddings = embeddings_model.embed_documents(data)
    cs_mat = cosine_similarity(embeddings)
    max = 0
    file = None
    for i in range(len(cs_mat)-1):
        if cs_mat[-1][i] > max:
            max = cs_mat[-1][i]
            file = text_files[i]
        print(f"Similarity score with {text_files[i]}: {cs_mat[-1][i]}")

    lines1 = text.split("\n")
    lines2 = sample_data[text_files.index(file)].split("\n")
    similar_lines = get_similar_lines(lines1,lines2)
    embeddings = embeddings_model.embed_documents(data)
    cs_mat = cosine_similarity(embeddings)
    print(cs_mat)
    return (max,similar_lines,file)
    