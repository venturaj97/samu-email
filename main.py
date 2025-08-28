import os
import io
import email
from email.policy import default

import PyPDF2
import nltk
from dotenv import load_dotenv

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from openai import AsyncOpenAI

load_dotenv()


try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

from nltk.tokenize import sent_tokenize


app = FastAPI(
    title="SAMU API - Email",
    description="Samu é um sistema simples utilizado para ler emails, descarta o que nao é relevante e responder o que é necessário.",
    version="1.0.0"
)


# Lista de origens que podem fazer requisições à nossa API
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
    "null"  # para permitir requisições de arquivos locais (file://)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.get("/")
def read_root():
    return {"status": "API online e funcionando!"}

def nlp_pre_texto(text: str) -> str:
    """
    Técnica de NLP: Limpa e prepara o texto.
    Para modelos modernos de IA, a limpeza pesada (remover stopwords, stemming)
    muitas vezes não é necessária e pode até prejudicar, pois eles entendem o contexto.
    Vamos focar em uma limpeza leve e segmentação.
    """
    # Segmenta o texto em sentenças para garantir que não seja longo demais
    # e remove espaços em branco excessivos.
    sentences = sent_tokenize(text, language='portuguese')
    clean_text = " ".join(sentence.strip() for sentence in sentences)
    return clean_text


async def get_ai_classification(text: str) -> str:
    """
    Usa a API da OpenAI (GPT) com um prompt específico para classificar o texto.
    Esta abordagem é muito mais robusta para diferentes idiomas e contextos.
    """
    if not client.api_key:
        raise HTTPException(status_code=500, detail="Chave da API da OpenAI não configurada.")  

    # Este é o nosso "prompt". Estamos dando instruções claras para a IA.
    system_prompt = """
    Você é um assistente de IA especialista em classificar emails.
    Sua tarefa é analisar o email fornecido e classificá-lo em uma de duas categorias: 'Produtivo' ou 'Improdutivo'.
    Um email 'Produtivo' é aquele que requer uma ação, resposta ou atenção, como uma solicitação, um problema, uma dúvida ou uma tarefa.
    Um email 'Improdutivo' é social, informativo, um agradecimento ou spam, e não requer uma ação imediata.
    Responda APENAS com a palavra 'Produtivo' ou 'Improdutivo', sem nenhuma outra explicação.
    """

    try:
        # Nova sintaxe para chamar a API com o cliente
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0,
            max_tokens=5
        )
        classification = response.choices[0].message.content.strip()

        # Uma verificação final para garantir que a resposta é válida
        if classification in ["Produtivo", "Improdutivo"]:
            return classification
        else:
            # Se a IA responder algo inesperado, retornamos um fallback seguro
            return "Produtivo"

    except Exception as e:
        # Captura erros de API, autenticação, etc.
        print(f"====== ERRO DETALHADO DA API OPENAI ======")
        print(e)
        print(f"==========================================")
        raise HTTPException(status_code=503, detail=f"Erro na comunicação com a API da OpenAI: {str(e)}")



async def extract_texto_arquivo(file: UploadFile) -> str:
    filename = file.filename
    content = await file.read()
    try:
        if filename.endswith(".txt"):
            return content.decode("utf-8")
        elif filename.endswith(".pdf"):
            pdf_stream = io.BytesIO(content)
            reader = PyPDF2.PdfReader(pdf_stream)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
        elif filename.endswith(".eml"):
            msg = email.message_from_bytes(content, policy=default)
            # Tenta pegar o corpo do email em texto plano
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        return part.get_payload(decode=True).decode()
            else:
                # Se não for multipart, pega o payload principal
                return msg.get_payload(decode=True).decode()
            return "" 
        else:
            raise HTTPException(status_code=400, detail=f"Formato de arquivo não suportado: {filename}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar o arquivo {filename}: {str(e)}")
    
@app.post("/processar/", summary="Processa e classifica um email")
async def processar_email(
    email_text: Optional[str] = Form(None),
    email_file: Optional[UploadFile] = File(None)
):
    text_to_process = ""

    if email_text and email_text.strip():
        text_to_process = email_text
    elif email_file:
        text_to_process = await extract_texto_arquivo(email_file)
    else:
        raise HTTPException(status_code=400, detail="Nenhum texto ou arquivo foi enviado para processamento.")
    
    if not text_to_process or not text_to_process.strip():
        raise HTTPException(status_code=400, detail="O conteúdo do email está vazio ou não pôde ser lido.")

# ===================== DEBUGGING - INÍCIO =====================
    print("\n--- INICIANDO DEBUG ---")
    print(f"1. Texto bruto recebido (text_to_process): >>{text_to_process}<<")
    
    # 1. Aplicar a técnica de NLP (pré-processamento)
    cleaned_text = nlp_pre_texto(text_to_process)
    
    print(f"2. Texto limpo enviado para a IA (cleaned_text): >>{cleaned_text}<<")
    print("--- FIM DO DEBUG ---\n")
    # ====================== DEBUGGING - FIM =======================
    # 2. Conectar com a API de IA para obter a classificação
    #    >>> A LÓGICA MOCK FOI SUBSTITUÍDA AQUI <<<
    categoria = await get_ai_classification(cleaned_text)

    # 3. Gerar a resposta sugerida com base na classificação da IA
    if categoria == "Produtivo":
        resposta_sugerida = "Olá, recebemos sua solicitação e nossa equipe já está trabalhando nela. Em breve, você receberá uma atualização. Atenciosamente."
    elif categoria == "Improdutivo":
        resposta_sugerida = "Agradecemos sua mensagem! Tenha um ótimo dia."
    else: # Fallback para o caso de a API retornar algo inesperado
        resposta_sugerida = "Agradecemos o contato. Sua mensagem foi recebida."

    # 4. Retornar o resultado
    return JSONResponse(content={
        "categoria": categoria,
        "resposta_sugerida": resposta_sugerida
    })
