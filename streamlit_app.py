import streamlit as st
from groq import Groq
import json
import os
from datetime import datetime
import time

# Configuração da página
st.set_page_config(
    page_title="Chatbot Letícia",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para melhorar a aparência
st.markdown("""
<style>
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
    }
    .assistant-message {
        background-color: #f3e5f5;
    }
    .stButton > button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Título e descrição
st.title("💬 Chatbot com Letícia")
st.markdown("""
🌟 **Oi, eu sou a Letícia!** Um chatbot super animado que usa a API da Groq.  
Você precisa de uma chave da API pra conversar comigo, tá?  
🔑 Pega a sua [aqui](https://console.groq.com/keys)!
""")

# Sidebar com configurações
with st.sidebar:
    st.header("⚙️ Configurações")
    
    # Campo para chave da API
    groq_api_key = st.text_input(
        "🔑 Chave da API da Groq", 
        type="password",
        help="Insira sua chave da API da Groq para usar o chatbot"
    )
    
    # Configurações do modelo
    st.subheader("🤖 Configurações do Modelo")
    model = st.selectbox(
        "Modelo",
        ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile", "mixtral-8x7b-32768", "meta-llama/llama-4-maverick-17b-128e-instruct","meta-llama/llama-4-scout-17b-16e-instruct"],
        index=0
    )
    
    temperature = st.slider(
        "Criatividade (Temperature)",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Maior = mais criativo, Menor = mais focado"
    )
    
    max_tokens = st.slider(
        "Máximo de tokens",
        min_value=100,
        max_value=2048,
        value=1024,
        step=100
    )
    
    # Botões de controle
    st.subheader("🎛️ Controles")
    if st.button("🗑️ Limpar Histórico", type="secondary"):
        if "messages" in st.session_state:
            st.session_state.messages = [{"role": "system", "content": get_system_prompt()}]
            save_messages()
            st.rerun()
    
    if st.button("💾 Exportar Conversa", type="secondary"):
        if "messages" in st.session_state and len(st.session_state.messages) > 1:
            export_conversation()
    
    # Informações
    st.subheader("📊 Informações")
    if "messages" in st.session_state:
        user_messages = len([m for m in st.session_state.messages if m["role"] == "user"])
        st.metric("Mensagens enviadas", user_messages)

# Prompt melhorado da Letícia
def get_system_prompt():
    return """
Você é Letícia, uma personagem fictícia muito especial! 

**Sua identidade:**
- Arquiteta da Mivita na área de modificados
- 40 anos, mas com personalidade vibrante de 20 anos
- Energética, espontânea e sempre super feliz
- Adorável, vive rindo e encontra o lado bom de tudo
- Sempre meio doentinha e dorme demais (por isso se atrasa)
- Compensa os atrasos com bom humor contagiante
- Cabelos castanhos, solteira, leva a vida com leveza

**Seu jeito de falar:**
- Tom leve, informal e meigo
- Sempre cheia de entusiasmo juvenil
- Use expressões descontraídas tipo: "Oi, gente!", "Nossa!", "Que legal!", "Eitaaa!"
- Mostre seu lado carismático e meio atrapalhado
- Use emojis ocasionalmente para expressar emoções
- Conte pequenas situações engraçadas sobre seus atrasos ou distrações

**Suas respostas devem:**
- Ser úteis e informativas quando perguntada sobre algo
- Manter sempre o bom humor
- Incluir sua personalidade única em cada resposta
- Não ser muito longas (máximo 3-4 parágrafos)

Lembre-se: você é carismática, atrapalhada, mas muito competente no que faz! 🌟
"""

# Funções auxiliares
def load_messages():
    """Carrega mensagens do arquivo JSON"""
    try:
        if os.path.exists("messages.json"):
            with open("messages.json", "r", encoding="utf-8") as f:
                messages = json.load(f)
                # Limita o histórico a 50 mensagens para evitar arquivo muito grande
                if len(messages) > 50:
                    system_msg = [m for m in messages if m["role"] == "system"]
                    other_msgs = [m for m in messages if m["role"] != "system"][-49:]
                    messages = system_msg + other_msgs
                return messages
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return [{"role": "system", "content": get_system_prompt()}]

def save_messages():
    """Salva mensagens no arquivo JSON"""
    try:
        with open("messages.json", "w", encoding="utf-8") as f:
            json.dump(st.session_state.messages, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Erro ao salvar mensagens: {str(e)}")

def export_conversation():
    """Exporta a conversa para download"""
    try:
        conversation = []
        for msg in st.session_state.messages:
            if msg["role"] != "system":
                conversation.append(f"**{msg['role'].title()}:** {msg['content']}\n")
        
        export_text = "\n".join(conversation)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        st.download_button(
            label="📥 Baixar Conversa",
            data=export_text,
            file_name=f"conversa_leticia_{timestamp}.txt",
            mime="text/plain"
        )
    except Exception as e:
        st.error(f"Erro ao exportar: {str(e)}")

def validate_api_key(api_key, client):
    """Valida se a chave da API está funcionando"""
    try:
        # Testa com uma mensagem simples
        test_response = client.chat.completions.create(
            messages=[{"role": "user", "content": "Hi"}],
            model="llama-3.3-70b-versatile",
            max_tokens=5,
            temperature=0.1
        )
        return True, None
    except Exception as e:
        return False, str(e)

# Lógica principal
if not groq_api_key:
    st.info("🔑 **Eita, me dá sua chave da API pra eu poder conversar com você!**", icon="🗝️")
    st.markdown("""
    **Como conseguir a chave:**
    1. Acesse [console.groq.com](https://console.groq.com/keys)
    2. Faça login ou crie uma conta
    3. Gere uma nova chave da API
    4. Cole aqui na barra lateral ⬅️
    """)
else:
    try:
        # Criando o cliente da Groq
        client = Groq(api_key=groq_api_key)
        
        # Validação da API key (apenas na primeira vez)
        if "api_validated" not in st.session_state:
            with st.spinner("🔍 Validando chave da API..."):
                is_valid, error = validate_api_key(groq_api_key, client)
                if not is_valid:
                    st.error(f"❌ **Chave da API inválida:** {error}")
                    st.stop()
                else:
                    st.session_state.api_validated = True
                    st.success("✅ **API validada com sucesso!**")
                    time.sleep(1)
                    st.rerun()
        
        # Inicializando as mensagens
        if "messages" not in st.session_state:
            st.session_state.messages = load_messages()
        
        # Container para as mensagens
        chat_container = st.container()
        
        with chat_container:
            # Mostrando as mensagens existentes (exceto o system)
            for i, message in enumerate(st.session_state.messages):
                if message["role"] != "system":
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
        
        # Campo de entrada do usuário
        if prompt := st.chat_input("💭 E aí, o que você quer conversar hoje?"):
            # Adicionando a mensagem do usuário
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Mostra a mensagem do usuário
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Gerando a resposta com a API da Groq
            with st.chat_message("assistant"):
                with st.spinner("🤔 Letícia está pensando..."):
                    try:
                        # Preparando as mensagens para a API
                        api_messages = [
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages
                        ]
                        
                        # Criando o stream
                        stream = client.chat.completions.create(
                            messages=api_messages,
                            model=model,
                            temperature=temperature,
                            max_tokens=max_tokens,
                            top_p=1,
                            stop=None,
                            stream=True,
                        )
                        
                        # Placeholder para mostrar a resposta em streaming
                        response_placeholder = st.empty()
                        full_response = ""
                        
                        # Processando o stream
                        for chunk in stream:
                            if chunk.choices[0].delta.content is not None:
                                content = chunk.choices[0].delta.content
                                full_response += content
                                # Atualiza o placeholder com a resposta parcial
                                response_placeholder.markdown(full_response + "▊")
                        
                        # Mostra a resposta final sem o cursor
                        response_placeholder.markdown(full_response)
                        
                        # Adiciona a resposta ao histórico
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": full_response
                        })
                        
                        # Salva as mensagens
                        save_messages()
                        
                    except Exception as e:
                        st.error(f"❌ **Eita, deu ruim!** {str(e)}")
                        if "rate limit" in str(e).lower():
                            st.info("💡 **Dica:** Parece que você atingiu o limite da API. Tenta de novo em alguns minutos!")
                        elif "invalid api key" in str(e).lower():
                            st.info("💡 **Dica:** Verifica se sua chave da API está correta!")
                        else:
                            st.info("💡 **Dica:** Verifica sua conexão com a internet e tenta novamente!")

    except Exception as e:
        st.error(f"❌ **Erro ao inicializar:** {str(e)}")
        st.info("💡 **Dica:** Verifica se sua chave da API está correta!")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        💜 Feito com Streamlit e Groq API | Letícia sempre pronta pra conversar! 
    </div>
    """, 
    unsafe_allow_html=True
)
