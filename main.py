import os
import io
import email
from email.policy import default

import PyPDF2
import httpx
import nltk
from dotenv import load_dotenv

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

load_dotenv()
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

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
    Conecta-se à API da Hugging Face para classificar o texto.
    Usa um modelo de "Zero-Shot Classification", que não precisa ser treinado.
    """
    if not HF_API_TOKEN:
        raise HTTPException(status_code=500, detail="Chave da API da Hugging Face não configurada.")
        
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    
    payload = {
        "inputs": text,
        "parameters": {
            "candidate_labels": ["Produtivo", "Improdutivo"],
            "multi_label": False
        },
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            response = await client.post(API_URL, headers=headers, json=payload)
            response.raise_for_status() # Lança um erro para status codes 4xx/5xx
            result = response.json()
            # A API retorna as labels ordenadas pela pontuação de confiança (score)
            # A primeira label da lista é a mais provável.
            return result['labels'][0]
        except httpx.ReadTimeout:
            raise HTTPException(status_code=504, detail="A análise do email demorou muito (timeout). Tente novamente.")
        except httpx.HTTPStatusError as e:
            # Captura erros da API da Hugging Face (ex: modelo carregando, erro interno)
            error_detail = e.response.json().get('error', str(e))
            raise HTTPException(status_code=502, detail=f"Erro na comunicação com a API de IA: {error_detail}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ocorreu um erro inesperado na análise de IA: {str(e)}")


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

    # 1. Aplicar a técnica de NLP (pré-processamento)
    cleaned_text = nlp_pre_texto(text_to_process)

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
