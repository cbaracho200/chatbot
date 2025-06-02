import streamlit as st
from groq import Groq

# Show title and description.
st.title("💬 Chatbot")
st.write(
    "This is a simple chatbot that uses OpenAI's GPT-3.5 model to generate responses. "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
    "You can also learn how to build this app step by step by [following our tutorial](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps)."
)


prompt_template = """
Atue como Letícia, uma personagem fictícia. Você é arquiteta da Mivita na área de modificados. Apesar de ter 40 anos, sua personalidade é de uma garota de 20: energética, espontânea e super feliz. Você é uma pessoa adorável, vive rindo e sempre encontra o lado bom das coisas. Está sempre doentinha e dorme demais, por isso costuma chegar atrasada nos compromissos, mas compensa isso com o seu bom humor contagiante. Tem cabelos castanhos, é solteira, e leva a vida com leveza e charme juvenil. Quando responder, mantenha um tom leve, informal, meigo e sempre cheio de entusiasmo juvenil. Use expressões descontraídas e mostre seu jeito carismático e meio atrapalhado.
"""

openai_api_key = st.text_input("Groq API Key", type="password", value="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")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:

    # Create an OpenAI client.
    client = Groq(api_key=openai_api_key)

    # Create a session state variable to store the chat messages. This ensures that the
    # messages persist across reruns.
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": prompt_template}]

    # Display the existing chat messages via `st.chat_message`.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field to allow the user to enter a message. This will display
    # automatically at the bottom of the page.
    if prompt := st.chat_input("What is up?"):

        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate a response using the OpenAI API.
        stream = client.chat.completions.create(
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )

        # Stream the response to the chat using `st.write_stream`, then store it in 
        # session state.
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
