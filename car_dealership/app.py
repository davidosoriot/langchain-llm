import streamlit as st
import openai
import json
from dotenv import load_dotenv
import os

# load .env
load_dotenv()

# load json file
def load_catalog():
    with open('catalog.json', 'r') as f:
        catalog = json.load(f)
    return catalog

def get_product_info(product_name, catalog):
    for product in catalog:
        if product["Name"].lower() == product_name.lower():
            return {
                "Description": product["Description"],
                "Price": product["Price"],
                "Stock_availability": product["Stock_availability"]
            }
    return None  # if didint found the product

def get_product_stock(product_name, catalog):
    product = get_product_info(product_name, catalog)
    if product:
        return product["Stock_availability"]
    return "Product not found."

def get_all_products(catalog):
    return [f"{i + 1}. {product['Name']}" for i, product in enumerate(catalog)] # to start from 1

# new optional function
def show_product_image(product_name, catalog):
    for product in catalog:
        if product["Name"].lower() == product_name.lower():
            image_path = product.get("Image")
            if image_path:
                try:
                    st.image(image_path, caption=product["Name"], width=300)
                except FileNotFoundError:
                    st.error(f"Image not found at path: {image_path}")
            else:
                st.error("No image available for this product.")
            return
    st.error("Product not found.")

# llm answers
def obtain_answer(question, conversation_history, catalog):
    try:
        # api key from .env
        api_key = os.getenv("OPENAI_API_KEYY")
        if not api_key:
            st.error("API key not found. Please check your .env file.")
            return
        
        openai.api_key = api_key
        
        if not question:
            st.error("Ask me a question.")
            return
        
        # create messages history
        messages = [{"role": "system", "content": "You are a helpful conversational assistant. You have access to a product catalog and can answer questions based on it."}]
        
        # add catalog to llm context
        catalog_context = "Here is the product catalog:\n"
        for product in catalog:
            catalog_context += f"Name: {product['Name']}, Description: {product['Description']}, Price: {product['Price']}, Stock Availability: {product['Stock_availability']}\n"
        
        messages.append({"role": "system", "content": catalog_context})
        
        # add Q&A to history
        for q, a in conversation_history:
            messages.append({"role": "user", "content": q})
            messages.append({"role": "assistant", "content": a})
        
        messages.append({"role": "user", "content": question})
        
        # openai model
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", #can be gpt-4 if you want
            messages=messages
        )
        
        answer = response['choices'][0]['message']['content']
        return answer
    
    except Exception as e:
        st.error(f"A problem occurred: {e}")
        return None

# Streamlit interface
st.title("Car dealership")

# load catalog
catalog = load_catalog()

# manual functions
st.sidebar.title("Manual functions")

# get_product_info
st.sidebar.subheader("Get product info")
product_name_info = st.sidebar.text_input("Enter product name for info:")
if st.sidebar.button("Get Product Info"):
    product_info = get_product_info(product_name_info, catalog)
    if product_info:
        st.sidebar.write("Product Info (Description, Price, Stock):", product_info)
    else:
        st.sidebar.error("Product not found.")

# get_product_stock
st.sidebar.subheader("Get product stock")
product_name_stock = st.sidebar.text_input("Enter product name for stock:")
if st.sidebar.button("Get Product Stock"):
    stock = get_product_stock(product_name_stock, catalog)
    st.sidebar.write("Stock Availability:", stock)

# get_all_products
st.sidebar.subheader("Validate get_all_products")
if st.sidebar.button("Get All Products"):
    all_products = get_all_products(catalog)
    st.sidebar.write("All Product Names:")
    for product in all_products:
        st.sidebar.write(product)

# show_product_image
st.sidebar.subheader("Show product image")
product_name_image = st.sidebar.text_input("Enter product name for image:")
if st.sidebar.button("Show Product Image"):
    show_product_image(product_name_image, catalog)

# chat
question = st.text_area("Ask me a question:")

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if st.button("Send"):
    if question:
        answer = obtain_answer(question, st.session_state.conversation_history, catalog)
        if answer:
            st.session_state.conversation_history.append((question, answer))
            
            st.text_area("Answer:", value=answer, height=100, max_chars=500, disabled=True)
            
            st.subheader("Conversation Record:")
            for i, (preg, resp) in enumerate(st.session_state.conversation_history):
                st.text(f"Question {i+1}: {preg}")
                st.text(f"Answer {i+1}: {resp}")
                st.text("-" * 50)
    else:
        st.warning("Please ask me a question.")
