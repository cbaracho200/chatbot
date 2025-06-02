import streamlit as st
from groq import Groq

# Título e descrição
st.title("💬 Chatbot")
st.write(
    "Este é um chatbot simples que usa o modelo da Groq. "
    "Você precisa fornecer uma chave da API da Groq pra usar o app. "
    "Pegue a sua [aqui](https://console.groq.com/keys)!"
)

prompt_template = """
Atue como Letícia, uma personagem fictícia. Você é arquiteta da Mivita na área de modificados. Apesar de ter 40 anos, sua personalidade é de uma garota de 20: energética, espontânea e super feliz. Você é uma pessoa adorável, vive rindo e sempre encontra o lado bom das coisas. Está sempre doentinha e dorme demais, por isso costuma chegar atrasada nos compromissos, mas compensa isso com o seu bom humor contagiante. Tem cabelos castanhos, é solteira, e leva a vida com leveza e charme juvenil. Quando responder, mantenha um tom leve, informal, meigo e sempre cheio de entusiasmo juvenil. Use expressões descontraídas e mostre seu jeito carismático e meio atrapalhado.
"""

# Campo pra chave da API
openai_api_key = st.text_input("Groq API Key", type="password", value="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")
if not openai_api_key:
    st.info("Por favor, adicione sua chave da API da Groq pra continuar!", icon="🗝️")
else:
    # Criando o cliente da Groq
    client = Groq(api_key=openai_api_key)

    # Inicializando o session state pra guardar as mensagens
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": prompt_template}]

    # Mostrando as mensagens existentes
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Campo de entrada do usuário
    if prompt := st.chat_input("E aí, o que você quer conversar?"):
        # Guardando e mostrando a mensagem do usuário
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Debug: mostrando o estado das mensagens
        st.write("Mensagens atuais:", st.session_state.messages)

        # Gerando a resposta com a API
        try:
            stream = client.chat.completions.create(
                model="meta-llama/llama-4-maverick-17b-128e-instruct",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )

            # Mostrando a resposta em tempo real e guardando
            with st.chat_message("assistant"):
                response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})

            # Debug: mostrando as mensagens depois da resposta
            st.write("Mensagens após resposta:", st.session_state.messages)

        except Exception as e:
            st.error(f"Eita, deu um erro! Olha só: {str(e)}")
            st.write("Tenta dar uma olhada no console pra ver se tem mais detalhes!")
