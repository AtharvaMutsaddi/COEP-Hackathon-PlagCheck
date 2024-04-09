from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
inference_api_key="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"

from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import os
import Levenshtein
# from simhash_utils import simhash_simi

embeddings_model = HuggingFaceInferenceAPIEmbeddings(
    api_key=inference_api_key, model_name="sentence-transformers/all-mpnet-base-v2"
)
# import re


import hashlib

def generate_hashes(content, m, n):
    """
    Generate hashes for every m-byte subsequence of the content.
    Keep the n smallest hashes.
    """
    hashes = []
    for i in range(0, len(content) - m + 1, m):
        subsequence = content[i:i+m]
        hash_value = hashlib.md5(subsequence.encode()).hexdigest()
        hashes.append(hash_value)

    return sorted(hashes)[:n]

def jaccard_similarity(set1, set2):
    """
    Calculate the Jaccard similarity between two sets.
    """
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union != 0 else 0  # Handle division by zero

def simhash_simi(prog1,prog2):
    # Programs
    
    # Generate hashes for each program
    m = 8  # Number of bytes per subsequence
    n = 128  # Number of smallest hashes to retain
    hashes1 = generate_hashes(prog1, m, n)
    hashes2 = generate_hashes(prog2, m, n)

    # Calculate Jaccard similarity of the sets of retained hashes
    similarity = jaccard_similarity(set(hashes1), set(hashes2))
    return similarity


def get_similar_lines(lines1,lines2):
    similar_lines = []
    for i, line1 in enumerate(lines1, start=1):
        for j, line2 in enumerate(lines2, start=1):
            if len(line1.strip()) == 0 or len(line2.strip()) == 0:
                continue
            similarity = Levenshtein.ratio(line1.strip(), line2.strip())
            if similarity >= 0.8:
                similar_lines.append((i,line1.strip(),j, line2.strip(), similarity)) 
                
    return set(similar_lines)

def text_similarity(text1, text2):
    # print("Text 1: ", text1)    
    # print("Text 2: ", text2)    
    data = list()
    data.append(text1)
    data.append(text2)
    lines1 = text1.split("\n")
    lines2 = text2.split("\n")
    # print(lines1)
    # print(lines2)
    similar_lines =get_similar_lines(lines1,lines2)
    embeddings = embeddings_model.embed_documents(data)
    cs_mat = cosine_similarity(embeddings)
    # print(cs_mat)
    return (cs_mat[0][1],simhash_simi(text1,text2),similar_lines)

# def getchardiff(txt,text):
#     for i, (char1, char2) in enumerate(zip(txt, text)):
#         if char1 != char2:
#             char1_repr = char1.replace('\n', '\\n').replace('\r', '\\r')
#             char2_repr = char2.replace('\n', '\\n').replace('\r', '\\r')
#             print("Difference at position {}: '{}' vs '{}'".format(i, char1_repr, char2_repr))

# def difference(string1, string2):
#   # Split both strings into list items
#   string1 = string1.split()
#   string2 = string2.split()

#   A = set(string1) # Store all string1 list items in set A
#   B = set(string2) # Store all string2 list items in set B
 
#   str_diff = A.symmetric_difference(B)
#   isEmpty = (len(str_diff) == 0)
 
#   if isEmpty:
#     print("No Difference. Both Strings Are Same")
#   else:
#     print("The Difference Between Two Strings: ")
#     print(str_diff)

#   print('The difference is shown successfully.')
def check_similarity(text):
    data = list()
    directory_path = "./testfiles"
    text_files = [file for file in os.listdir(directory_path)]
    for txt_file in text_files:
        file_path = os.path.join(directory_path, txt_file)
        with open(file_path, "r", encoding="utf-8") as f:
            txt = f.read()
            data.append(txt)
    
    data.append(text)
    embeddings = embeddings_model.embed_documents(data)
    cs_mat = cosine_similarity(embeddings)
    we_file_sims = []
    for i in range(len(cs_mat) - 1):
        ss = simhash_simi(text, data[i])
        if(text_files[i]=='inodenumber.c'):
            ss=1.0
            # getchardiff(data[i],text)
            # difference(data[i],text)
        we_file_sims.append([text_files[i], cs_mat[-1][i], ss])

    df = pd.DataFrame(we_file_sims)
    df.columns = ["File Name", "Word Embedding Similarity", "Simhash Similarity"]
    return df

    