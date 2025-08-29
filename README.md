# 🚀 Analisador e Classificador Inteligente de Emails - SAMU

## 📄 Descrição do Projeto

Este projeto é uma solução digital desenvolvida para automatizar a triagem e resposta de emails. Utilizando Inteligência Artificial, a aplicação classifica os emails recebidos em categorias predefinidas (`Produtivo` ou `Improdutivo`), gera uma sugestão de resposta contextual e permite o envio dessa resposta diretamente da interface.

O objetivo é otimizar o tempo da equipe, eliminando a necessidade de análise manual de cada email e permitindo que se concentrem em tarefas que exigem ação imediata.

## ✨ Funcionalidades Principais

* **Análise de Conteúdo:** Permite a análise de emails colando o texto diretamente ou fazendo o upload de arquivos (`.txt`, `.pdf`, `.eml`).
* **Classificação com IA:** Utiliza o modelo GPT-3.5-turbo da OpenAI para classificar os emails com base em seu conteúdo e contexto.
* **Geração Dinâmica de Respostas:** A IA gera uma resposta automática relevante e apropriada para a categoria identificada.
* **Envio de Email Integrado:** Funcionalidade para enviar a resposta gerada para um destinatário especificado, diretamente da aplicação.
* **Interface Web Intuitiva:** Um frontend limpo e interativo construído com HTML, CSS e JavaScript puro, com design responsivo graças ao Bootstrap.

## 🛠️ Tecnologias Utilizadas

* **Backend:**
    * Python 3.10+
    * FastAPI
    * Uvicorn (Servidor ASGI)
    * Pydantic (Validação de dados)
* **Frontend:**
    * HTML5
    * CSS3 (Bootstrap 5)
    * JavaScript (Fetch API para comunicação com o backend)
* **Inteligência Artificial & NLP:**
    * OpenAI (GPT-3.5-turbo)
    * NLTK (para pré-processamento de texto)
* **Envio de Email:**
    * `smtplib` (Biblioteca padrão do Python)
* **Dependências Principais:**
    * `fastapi`, `uvicorn`, `python-dotenv`, `openai`, `pypdf2`, `nltk`

