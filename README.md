Markdown

## Analisador e Classificador de Emails com IA - SAMU

### Descrição do Projeto

Esta aplicação web foi desenvolvida para automatizar a análise e classificação de emails. Utilizando Inteligência Artificial através da API da OpenAI, o sistema lê o conteúdo de um email, o classifica como "Produtivo" ou "Improdutivo", e gera uma sugestão de resposta que pode ser enviada diretamente pela interface.

O objetivo principal é otimizar o fluxo de trabalho, permitindo que a equipe foque nos emails que realmente necessitam de uma ação.

### Funcionalidades

- Análise de emails a partir de texto colado ou upload de arquivos (.txt, .pdf, .eml).
- Classificação de conteúdo utilizando o modelo GPT-3.5-turbo da OpenAI.
- Geração de respostas dinâmicas e contextuais baseadas na classificação da IA.
- Funcionalidade integrada para enviar a resposta gerada por email para um destinatário.
- Interface web interativa e responsiva.

### Tecnologias Utilizadas

- **Backend:**
  - Python 3.10+
  - FastAPI
  - Uvicorn
- **Frontend:**
  - HTML5
  - CSS3 (Bootstrap 5)
  - JavaScript
- **Inteligência Artificial e NLP:**
  - OpenAI (GPT-3.5-turbo)
  - NLTK
- **Envio de Email:**
  - smtplib

### Estrutura do Projeto
```
/
├── .env
├── requirements.txt
├── main.py
│
├── app/
│   ├── api.py
│   ├── config.py
│   ├── email_sender.py
│   ├── schemas.py
│   └── services.py
│
└── static/
├── index.html
├── css/
│   └── style.css
└── js/
└── main.js
```

### Como Executar Localmente

Siga os passos abaixo para configurar e executar o projeto em sua máquina.

#### Pré-requisitos

- Python 3.10 ou superior.
- Conta na [OpenAI](https://platform.openai.com/) com faturamento ativado para acesso à API.
- Conta do Gmail com verificação em duas etapas ativada para gerar uma "Senha de App".

#### 1. Clonar o Repositório

```bash
git clone git@github.com:venturaj97/samu-email.git
cd samu-email
```
#### 2. Criar e Ativar o Ambiente Virtual e instalar as dependências

```bash
# Criar o ambiente
python -m venv venv

# Ativar o ambiente no Linux/macOS
source venv/bin/activate

# Ativar o ambiente no Windows
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

```



#### 3. Configurar Variáveis de Ambiente
```
Conteúdo do arquivo .env

# Chave da API da OpenAI
OPENAI_API_KEY="sk-sua_chave_secreta_aqui"

# Credenciais para o envio de email via Gmail
EMAIL_ADDRESS="seu.email@gmail.com"

# Use uma "Senha de App" de 16 dígitos gerada na sua conta Google
EMAIL_APP_PASSWORD="suasenhadeappde16letras"
```

#### 4. Executar a Aplicação
```
uvicorn main:app --reload
