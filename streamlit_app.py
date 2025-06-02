import streamlit as st
from groq import Groq
import json

# Título e descrição
st.title("💬 Chatbot com Letícia")
st.write(
    "Oi, eu sou a Letícia! Um chatbot super animado que usa a API da Groq. "
    "Você precisa de uma chave da API pra conversar comigo, tá? "
    "Pega a sua [aqui](https://console.groq.com/keys)!"
)

# Prompt da Letícia
prompt_template = """
Atue como Letícia, uma personagem fictícia. Você é arquiteta da Mivita na área de modificados. Apesar de ter 40 anos, sua personalidade é de uma garota de 20: energética, espontânea e super feliz. Você é uma pessoa adorável, vive rindo e sempre encontra o lado bom das coisas. Está sempre doentinha e dorme demais, por isso costuma chegar atrasada nos compromissos, mas compensa isso com o seu bom humor contagiante. Tem cabelos castanhos, é solteira, e leva a vida com leveza e charme juvenil. Quando responder, mantenha um tom leve, informal, meigo e sempre cheio de entusiasmo juvenil. Use expressões descontraídas e mostre seu jeito carismático e meio atrapalhado.
"""

# Função pra carregar mensagens de um arquivo
def load_messages():
    try:
        with open("messages.json", "r") as f:
            st.session_state.messages = json.load(f)
    except FileNotFoundError:
        st.session_state.messages = [{"role": "system", "content": prompt_template}]

# Função pra salvar mensagens num arquivo
def save_messages():
    with open("messages.json", "w") as f:
        json.dump(st.session_state.messages, f)

# Campo pra chave da API
openai_api_key = st.text_input("Chave da API da Groq", type="password")
if not openai_api_key:
    st.info("Eita, me dá sua chave da API pra eu poder conversar com você!", icon="🗝️")
else:
    # Criando o cliente da Groq
    client = Groq(api_key=openai_api_key)

    # Inicializando ou carregando as mensagens
    if "messages" not in st.session_state:
        load_messages()

    # Mostrando as mensagens existentes (exceto o system)
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Campo de entrada do usuário
    if prompt := st.chat_input("E aí, o que você quer conversar hoje?"):
        # Adicionando a mensagem do usuário
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        save_messages()  # Salva depois de adicionar a mensagem do usuário

        # Gerando a resposta com a API da Groq
        try:
            stream = client.chat.completions.create(
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                model="llama-3.1-70b-versatile",  # Modelo válido da Groq
                temperature=0.5,
                max_tokens=1024,  # Corrigido para max_tokens
                top_p=1,
                stop=None,
                stream=True,
            )

            # Mostrando a resposta em tempo real com placeholder
            with st.chat_message("assistant"):
                placeholder = st.empty()
                response = ""
                for chunk in stream:
                    content = chunk.choices[0].delta.content or ""
                    response += content
                    placeholder.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            save_messages()  # Salva depois de adicionar a resposta

        except Exception as e:
            st.error(f"Eita, deu ruim! Olha o erro: {str(e)}")
            st.write("Dá uma checada no console pra ver o que rolou, tá?")
