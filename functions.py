from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
inference_api_key="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"

from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import os

directory_path = "./"

embeddings_model = HuggingFaceInferenceAPIEmbeddings(
    api_key=inference_api_key, model_name="sentence-transformers/all-mpnet-base-v2"
)

sample_data = []

text_files = [file for file in os.listdir(directory_path) if file.endswith(".txt")]
for txt_file in text_files:
        file_path = os.path.join(directory_path, txt_file)
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
            sample_data.append(text)

def text_similarity(text1, text2):
    data = list()
    data.append(text1)
    data.append(text2)
    embeddings = embeddings_model.embed_documents(data)
    cs_mat = cosine_similarity(embeddings)
    print(cs_mat)
    return cs_mat[0][1]

def check_similarity(text):
    data = list()
    data.extend(sample_data)
    data.append(text)
    embeddings = embeddings_model.embed_documents(data)
    cs_mat = cosine_similarity(embeddings)
    max = 0
    for i in range(len(cs_mat)-1):
        if cs_mat[-1][i] > max:
            max = cs_mat[-1][i]
        print(f"Similarity score with {text_files[i]}: {cs_mat[-1][i]}")

    return max


def print_sim_scores_for_all(data,cosine_similarity_mat):
    entries=[]
    i=0
    while(i<len(data)):
        j=0
        while(j<len(data)):
            if i !=j:
                entries.append([data[i],data[j],cosine_similarity_mat[i][j]])         
            j+=1
        i+=1
        
    df=pd.DataFrame(entries)
    df.columns=["text1","text2","sim score"]
    return df
    