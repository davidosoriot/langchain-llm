import streamlit as st
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
import os

# Insert apikey
with open('apikeycash.txt', 'r') as f:
    openai_api_key = f.read().strip()

# Iniciate embeddings and the openai model
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=openai_api_key)

# PDF processing
def process_pdf(file_path):
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    # Divide by chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
    docs = text_splitter.split_documents(documents)

    # Create de vector db
    db = FAISS.from_documents(docs, embeddings)
    return db

# Function to response
def ask_question(db, question):
    retriever = db.as_retriever()
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
    response = qa_chain.run(question)
    return response

# summary generator
def summarize_pdf(db):
    retriever = db.as_retriever(search_kwargs={"k": 10})
    docs = retriever.get_relevant_documents("Provide a content summary.")
    content = " ".join([doc.page_content for doc in docs])

    summary_prompt = f"""
    Provide a detailed and concise summary of the following content:
    {content}
    """
    response = llm.predict(summary_prompt)
    return response

# Streamlit
st.set_page_config(page_title="PDF chatbot", layout="centered")
st.title("PDF chatbot with langchain")
st.subheader("load the PDF and realize questions or summarize it.")

uploaded_file = st.file_uploader("load your PDF file", type=["pdf"])

if uploaded_file:
    with st.spinner("Processing PDF file..."):
        with open("temp.pdf", "wb") as f:
            f.write(uploaded_file.read())
        try:
            db = process_pdf("temp.pdf")
            st.success("the file has been processed successfully.")
        except Exception as e:
            st.error(f"Error processing PDF file: {e}")

    
    st.subheader("Options:")
    option = st.selectbox("Select an option:", ["ask question", "Obtain summary"])

    if option == "ask question":
        question = st.text_input("write your question about the PDF:")
        if st.button("send"):
            with st.spinner("Generating answer..."):
                try:
                    response = ask_question(db, question)
                    st.write("### answer:")
                    st.write(response)
                except Exception as e:
                    st.error(f"Error answering the question: {e}")

    elif option == "Obtain summary":
        if st.button("Generate summary"):
            with st.spinner("Generating summary..."):
                try:
                    summary = summarize_pdf(db)
                    st.write("### summary:")
                    st.write(summary)
                except Exception as e:
                    st.error(f"Error generating summary: {e}")
