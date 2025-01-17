import streamlit as st
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
import os

# Configurar la clave de OpenAI
with open('apikeycash.txt', 'r') as f:
    openai_api_key = f.read().strip()

# Inicializar embeddings y modelo de lenguaje
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=openai_api_key)

# Función para procesar el PDF
def process_pdf(file_path):
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    # Dividir en chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
    docs = text_splitter.split_documents(documents)

    # Crear la base vectorial
    db = FAISS.from_documents(docs, embeddings)
    return db

# Función para responder preguntas
def ask_question(db, question):
    retriever = db.as_retriever()
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
    response = qa_chain.run(question)
    return response

# Función para generar resumen
def summarize_pdf(db):
    retriever = db.as_retriever(search_kwargs={"k": 10})
    docs = retriever.get_relevant_documents("Proporciona un resumen del contenido.")
    content = " ".join([doc.page_content for doc in docs])

    summary_prompt = f"""
    Proporciona un resumen detallado y conciso del siguiente contenido:
    {content}
    """
    response = llm.predict(summary_prompt)
    return response

# Interfaz con Streamlit
st.set_page_config(page_title="Chatbot de PDF", layout="centered")
st.title("Chatbot de PDF con LangChain")
st.subheader("Carga un archivo PDF y realiza preguntas o resúmelo.")

uploaded_file = st.file_uploader("Sube tu archivo PDF", type=["pdf"])

if uploaded_file:
    with st.spinner("Procesando el archivo PDF..."):
        with open("temp.pdf", "wb") as f:
            f.write(uploaded_file.read())
        try:
            db = process_pdf("temp.pdf")
            st.success("El archivo ha sido procesado exitosamente.")
        except Exception as e:
            st.error(f"Error al procesar el archivo PDF: {e}")

    # Opciones de interacción
    st.subheader("Opciones:")
    option = st.selectbox("Selecciona una opción:", ["Hacer una pregunta", "Obtener un resumen"])

    if option == "Hacer una pregunta":
        question = st.text_input("Escribe tu pregunta sobre el PDF:")
        if st.button("Enviar"):
            with st.spinner("Generando respuesta..."):
                try:
                    response = ask_question(db, question)
                    st.write("### Respuesta:")
                    st.write(response)
                except Exception as e:
                    st.error(f"Error al responder la pregunta: {e}")

    elif option == "Obtener un resumen":
        if st.button("Generar resumen"):
            with st.spinner("Generando resumen..."):
                try:
                    summary = summarize_pdf(db)
                    st.write("### Resumen:")
                    st.write(summary)
                except Exception as e:
                    st.error(f"Error al generar el resumen: {e}")
