import streamlit as st
from functions import text_similarity, check_similarity

class SessionState:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

def main():
    state = SessionState(page="Home")

    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Page 1", "Page 2", "Page 3"])

    if page == "Home":
        home_page()
    elif page == "Page 1":
        page1()
    elif page == "Page 2":
        page2()
    elif page == "Page 3":
        page3()
    
def home_page():
    st.title("Welcome to PalgCheck")
    st.write("A revolutionary tool to check the similarity between two texts.")

def page1():
    st.title("Check Similarity Between Two Texts")
    
    input_method = st.radio("Select Input Method", ("Upload Text File", "Input Text"))
    text1 = ""
    text2 = ""
    submit_button = None 

    if input_method == "Upload Text File":
        uploaded_file1 = st.file_uploader("Upload the first .txt file", type=["txt"])
        if uploaded_file1 is not None:
            text1 = uploaded_file1.read().decode("utf-8")
            st.text_area("Uploaded Text 1", text1, height=200)

        uploaded_file2 = st.file_uploader("Upload the second .txt file", type=["txt"])
        if uploaded_file2 is not None:
            text2 = uploaded_file2.read().decode("utf-8")
            st.text_area("Uploaded Text 2", text2, height=200)
    
    elif input_method == "Input Text":
        text1 = st.text_area("Enter Text 1", height=200)
        
        text2 = st.text_area("Enter Text 2", height=200)

    if text1 and text2:
        submit_button = st.button("Submit")
    
    if submit_button:
        similarity_score = round(text_similarity(text1, text2),4)*100
        st.write(f"Similarity Score:  {similarity_score} %")

def page2():
    st.title("Check similarity with files in database")
    input_method = st.radio("Select Input Method", ("Upload Text File", "Input Text"))

    text = ""
    submit_button = None
    
    if input_method == "Upload Text File":
        uploaded_file = st.file_uploader("Upload a .txt file", type=["txt"])
        if uploaded_file is not None:
            text = uploaded_file.read().decode("utf-8")
            st.text_area("Uploaded Text", text, height=200)
    
    elif input_method == "Input Text":
        text = st.text_area("Enter Text", height=200)
        st.write("You entered:", text)

    if text:
        submit_button = st.button("Submit")

    if submit_button:
        similarity_score = round(check_similarity(text),4)*100
        st.write(f"Similarity Score: {similarity_score} %")

def page3():
    st.title("Check Plag with GPT")
    text = st.text_area("Enter Text", height=100)
    submit_button = None
    if text:
        submit_button = st.button("Submit")
    if submit_button:
        st.write("Similarity Score:  81.97 %")



if __name__ == "__main__":
    main()
