import streamlit as st
import openai

def obtain_answer(question):
    try:
        # read api key
        with open('apikeycash.txt', 'r') as f:
            api_key = f.read().strip()
        
        openai.api_key = api_key
        
        if not question:
            st.error("Please ask a question.")
            return
        
        # model
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  
            messages=[
                {"role": "user", "content": question}
            ]
        )
        
        answer = response['choices'][0]['message']['content']
        
        return answer
    
    except Exception as e:
        st.error(f"A problem occurred: {e}")
        return None

# streamlit
st.title("Chatbot")

question = st.text_area("Ask me a question:")

if st.button("Send"):
    if question:
        answer = obtain_answer(question)
        if answer:
            st.text_area("Answer:", value=answer, height=100, max_chars=500, disabled=True)

            if "historial" not in st.session_state:
                st.session_state.historial = []

            st.session_state.historial.append((question, answer))

            st.subheader("Conversation History:")
            for i, (preg, resp) in enumerate(st.session_state.historial):
                st.text(f"Q{i+1}: {preg}")
                st.text(f"A{i+1}: {resp}")
                st.text("-" * 50)

    else:
        st.warning("Please enter a question.")

