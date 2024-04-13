from langchain.text_splitter import RecursiveCharacterTextSplitter
import Levenshtein

def preprocess_text(text):
    return text.replace("\n", " ").replace("\r", " ").replace("\t", " ").replace("  ", " ").strip()

def split_text_into_chunks(text: str) -> list:
    return RecursiveCharacterTextSplitter(
        chunk_size=80, chunk_overlap=0, length_function=len
    ).split_text(text)


def get_similar_chunks(text_1: str, text_2: str) -> list:
    all_chunks_similarity_mapping = []
    text_1 = preprocess_text(text_1)
    text_2 = preprocess_text(text_2)
    chunks_1 = split_text_into_chunks(text_1)
    chunks_2 = split_text_into_chunks(text_2)

    for chunk_1 in chunks_1:
        for chunk_2 in chunks_2:
            curr_ratio = Levenshtein.ratio(chunk_1, chunk_2)
            if curr_ratio >= 0.6:
                all_chunks_similarity_mapping.append([curr_ratio, chunk_1, chunk_2])

    # Sorting the mapping in descending order wrt the similarity ratio
    all_chunks_similarity_mapping = sorted(
        all_chunks_similarity_mapping, key=lambda x: x[0], reverse=True
    )

    covered_chunks = []
    ans = {}

    for item in all_chunks_similarity_mapping:
        chunk_1, chunk_2 = item[1::1]

        if chunk_1 not in covered_chunks and chunk_2 not in covered_chunks:
            ans[chunk_1] = chunk_2
            covered_chunks.append(chunk_1)
            covered_chunks.append(chunk_2)

    return ans


""" file_content_1 = ""
with open("testing/file1_copy.c", "r") as f:
    file_content_1 = f.read()

file_content_2 = ""
with open("testing/file1.c", "r") as f:
    file_content_2 = f.read()

ans = get_similar_chunks(file_content_1, file_content_2)

for item in ans:
    print(item, end="\n\n") """
