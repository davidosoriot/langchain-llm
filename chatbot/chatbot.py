import streamlit as st
import openai

def obtain_answer(question, conversation_history):
    try:
        # read api key
        with open('apikeycash.txt', 'r') as f:
            api_key = f.read().strip()
        
        openai.api_key = api_key
        
        if not question:
            st.error("ask me a question.")
            return
        
        # historial
        messages = [{"role": "system", "content": "you are a helpful conversational assistant."}]
        for q, a in conversation_history:
            messages.append({"role": "user", "content": q})
            messages.append({"role": "assistant", "content": a})
        
        messages.append({"role": "user", "content": question})
        
        # openAI model
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        
        answer = response['choices'][0]['message']['content']
        return answer
    
    except Exception as e:
        st.error(f"A problem ocurred: {e}")
        return None

# Streamlit
st.title("Chatbot")

question = st.text_area("ask me a question:")

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if st.button("send"):
    if question:
        answer = obtain_answer(question, st.session_state.conversation_history)
        if answer:
            st.session_state.conversation_history.append((question, answer))
            
            st.text_area("answer:", value=answer, height=100, max_chars=500, disabled=True)
            
            st.subheader("conversation record:")
            for i, (preg, resp) in enumerate(st.session_state.conversation_history):
                st.text(f"question {i+1}: {preg}")
                st.text(f"answer {i+1}: {resp}")
                st.text("-" * 50)
    else:
        st.warning("Please make me a question.")
