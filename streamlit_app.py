import streamlit as st
from groq import Groq
import json
import os
from datetime import datetime
import time

# Configuração da página
st.set_page_config(
    page_title="Assistente Virtual",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personalizado mais discreto
st.markdown("""
<style>
    .chat-message {
        padding: 0.8rem;
        border-radius: 0.3rem;
        margin-bottom: 0.5rem;
    }
    .user-message {
        background-color: #f8f9fa;
    }
    .assistant-message {
        background-color: #f1f3f4;
    }
    .stButton > button {
        width: 100%;
        border-radius: 0.3rem;
    }
    .main-header {
        font-size: 1.8rem;
        color: #333;
        margin-bottom: 1rem;
    }
    .subtitle {
        font-size: 1rem;
        color: #666;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Funções auxiliares (definidas primeiro para evitar NameError)
def get_system_prompt():
    """Retorna o prompt do sistema para a Letícia"""
    return """
Você é Letícia, uma assistente virtual prestativa e amigável.

**Sua personalidade:**
- Profissional mas calorosa e acessível
- Sempre disposta a ajudar de forma eficiente
- Comunicação clara e direta
- Ligeiramente descontraída, mas mantém o foco
- Usa linguagem brasileira natural

**Seu estilo de comunicação:**
- Tom amigável mas profissional
- Respostas concisas e úteis
- Ocasionalmente usa expressões brasileiras sutis
- Foca em resolver problemas e fornecer informações
- Evita ser excessivamente animada ou informal

**Diretrizes:**
- Mantenha respostas entre 1-3 parágrafos
- Seja prestativa e eficiente
- Use emojis moderadamente (máximo 1-2 por resposta)
- Foque no que o usuário precisa
"""

def load_messages():
    """Carrega mensagens do arquivo JSON"""
    try:
        if os.path.exists("chat_history.json"):
            with open("chat_history.json", "r", encoding="utf-8") as f:
                messages = json.load(f)
                # Limita o histórico a 50 mensagens
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
        with open("chat_history.json", "w", encoding="utf-8") as f:
            json.dump(st.session_state.messages, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Erro ao salvar histórico: {str(e)}")

def save_request_log(user_input, response):
    """Salva log das solicitações dos usuários"""
    try:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_request": user_input,
            "response_preview": response[:100] + "..." if len(response) > 100 else response,
            "response_length": len(response)
        }
        
        # Carrega logs existentes
        log_file = "requests_log.json"
        logs = []
        if os.path.exists(log_file):
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    logs = json.load(f)
            except json.JSONDecodeError:
                logs = []
        
        # Adiciona novo log
        logs.append(log_entry)
        
        # Mantém apenas os últimos 1000 logs
        if len(logs) > 1000:
            logs = logs[-1000:]
        
        # Salva logs atualizados
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        # Falha silenciosa no log para não interromper o chat
        pass

def export_conversation():
    """Exporta a conversa para download"""
    try:
        if "messages" not in st.session_state or len(st.session_state.messages) <= 1:
            st.warning("⚠️ Nenhuma conversa para exportar.")
            return
            
        conversation = []
        for msg in st.session_state.messages:
            if msg["role"] != "system":
                role_name = "Usuário" if msg["role"] == "user" else "Assistente"
                conversation.append(f"**{role_name}:** {msg['content']}\n")
        
        export_text = "\n".join(conversation)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        st.download_button(
            label="📥 Baixar Conversa",
            data=export_text,
            file_name=f"conversa_{timestamp}.txt",
            mime="text/plain",
            key="download_btn"
        )
    except Exception as e:
        st.error(f"Erro ao exportar: {str(e)}")

def export_requests_log():
    """Exporta o log de solicitações"""
    try:
        log_file = "requests_log.json"
        if not os.path.exists(log_file):
            st.warning("⚠️ Nenhum log de solicitações encontrado.")
            return
            
        with open(log_file, "r", encoding="utf-8") as f:
            logs = json.load(f)
        
        if not logs:
            st.warning("⚠️ Log de solicitações vazio.")
            return
        
        # Converte para texto legível
        export_lines = ["=== LOG DE SOLICITAÇÕES ===\n"]
        for i, log in enumerate(logs, 1):
            export_lines.append(f"#{i} - {log['timestamp']}")
            export_lines.append(f"Solicitação: {log['user_request']}")
            export_lines.append(f"Resposta (preview): {log['response_preview']}")
            export_lines.append(f"Tamanho da resposta: {log['response_length']} chars")
            export_lines.append("-" * 50)
        
        export_text = "\n".join(export_lines)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        st.download_button(
            label="📊 Baixar Log de Solicitações",
            data=export_text,
            file_name=f"log_solicitacoes_{timestamp}.txt",
            mime="text/plain",
            key="download_log_btn"
        )
        
        # Mostra estatísticas
        st.info(f"📈 **Estatísticas:** {len(logs)} solicitações registradas")
        
    except Exception as e:
        st.error(f"Erro ao exportar log: {str(e)}")

def validate_api_key(api_key, client):
    """Valida se a chave da API está funcionando"""
    try:
        test_response = client.chat.completions.create(
            messages=[{"role": "user", "content": "Hi"}],
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
            max_tokens=5,
            temperature=0.1
        )
        return True, None
    except Exception as e:
        return False, str(e)

def clear_all_data():
    """Limpa todos os dados (histórico e logs)"""
    try:
        # Limpa session state
        if "messages" in st.session_state:
            st.session_state.messages = [{"role": "system", "content": get_system_prompt()}]
        
        # Remove arquivos
        files_to_remove = ["chat_history.json", "requests_log.json"]
        for file in files_to_remove:
            if os.path.exists(file):
                os.remove(file)
        
        st.success("✅ Todos os dados foram limpos!")
        time.sleep(1)
        st.rerun()
    except Exception as e:
        st.error(f"Erro ao limpar dados: {str(e)}")

# Interface principal
st.markdown('<h1 class="main-header">🤖 Assistente Virtual</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Assistente inteligente powered by Groq AI</p>', unsafe_allow_html=True)

# Sidebar com configurações (mais discreta)
with st.sidebar:
    st.header("Configurações")
    
    # Campo para chave da API
    groq_api_key = st.text_input(
        "Chave da API Groq", 
        type="password",
        help="Insira sua chave da API da Groq",
        value="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"
    )
    
    # Configurações do modelo
    with st.expander("⚙️ Configurações Avançadas"):
        model = st.selectbox(
            "Modelo",
            ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile", "mixtral-8x7b-32768","meta-llama/llama-4-maverick-17b-128e-instruct"],
            index=0
        )
        
        temperature = st.slider(
            "Criatividade",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1
        )
        
        max_tokens = st.slider(
            "Máximo de tokens",
            min_value=100,
            max_value=2048,
            value=1024,
            step=100
        )
    
    # Controles
    st.subheader("Controles")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Limpar", type="secondary", help="Limpar histórico"):
            if "messages" in st.session_state:
                st.session_state.messages = [{"role": "system", "content": get_system_prompt()}]
                save_messages()
                st.rerun()
    
    with col2:
        if st.button("🔄 Reset", type="secondary", help="Limpar tudo"):
            clear_all_data()
    
    # Exportações
    st.subheader("Exportar")
    
    if st.button("💬 Conversa", help="Exportar conversa atual"):
        export_conversation()
    
    if st.button("📊 Logs", help="Exportar log de solicitações"):
        export_requests_log()
    
    # Informações
    if "messages" in st.session_state:
        user_msgs = len([m for m in st.session_state.messages if m["role"] == "user"])
        st.metric("Mensagens", user_msgs)
        
        # Mostra estatísticas do log
        try:
            if os.path.exists("requests_log.json"):
                with open("requests_log.json", "r", encoding="utf-8") as f:
                    logs = json.load(f)
                    st.metric("Solicitações registradas", len(logs))
        except:
            pass

# Lógica principal
if not groq_api_key:
    st.info("🔑 **Configure sua chave da API na barra lateral para começar.**")
    with st.expander("ℹ️ Como obter a chave da API"):
        st.markdown("""
        **Passos para obter a chave:**
        1. Acesse [console.groq.com](https://console.groq.com/keys)
        2. Faça login ou crie uma conta
        3. Gere uma nova chave da API
        4. Cole na barra lateral
        """)
else:
    try:
        # Criando o cliente da Groq
        client = Groq(api_key=groq_api_key)
        
        # Validação da API key (apenas na primeira vez)
        if "api_validated" not in st.session_state:
            with st.spinner("Validando API..."):
                is_valid, error = validate_api_key(groq_api_key, client)
                if not is_valid:
                    st.error(f"❌ **API inválida:** {error}")
                    st.stop()
                else:
                    st.session_state.api_validated = True
                    st.success("✅ **API configurada com sucesso!**")
                    time.sleep(1)
                    st.rerun()
        
        # Inicializando as mensagens
        if "messages" not in st.session_state:
            st.session_state.messages = load_messages()
        
        # Container para as mensagens
        chat_container = st.container()
        
        with chat_container:
            # Mostrando as mensagens existentes (exceto o system)
            for message in st.session_state.messages:
                if message["role"] != "system":
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
        
        # Campo de entrada do usuário
        if prompt := st.chat_input("Digite sua mensagem..."):
            # Adicionando a mensagem do usuário
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Mostra a mensagem do usuário
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Gerando a resposta com a API da Groq
            with st.chat_message("assistant"):
                with st.spinner("Processando..."):
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
                        
                        # Salva as mensagens e registra a solicitação
                        save_messages()
                        save_request_log(prompt, full_response)
                        
                    except Exception as e:
                        error_msg = str(e).lower()
                        st.error(f"❌ **Erro:** {str(e)}")
                        
                        if "rate limit" in error_msg:
                            st.info("💡 Limite de API atingido. Tente novamente em alguns minutos.")
                        elif "invalid api key" in error_msg:
                            st.info("💡 Verifique se sua chave da API está correta.")
                        else:
                            st.info("💡 Verifique sua conexão e tente novamente.")

    except Exception as e:
        st.error(f"❌ **Erro de inicialização:** {str(e)}")

# Footer discreto
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #999; font-size: 0.8rem;">Powered by Groq AI</div>', 
    unsafe_allow_html=True
)
