import io
import email
from email.policy import default

import PyPDF2
import extract_msg

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="SAMU API - Email",
    description="Uma API para classificar emails como produtivos ou improdutivos e sugerir respostas.",
    version="1.0.0"
)

# --- NOVA CONFIGURAÇÃO DO CORS ---
# Lista de origens que podem fazer requisições à nossa API
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
    "null"  # Importante para permitir requisições de arquivos locais (file://)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Permite todos os métodos (GET, POST, etc)
    allow_headers=["*"], # Permite todos os cabeçalhos
)

# logica

async def extract_text_from_file(file: UploadFile) -> str:
    """
    Extrai o texto de um UploadFile com base na sua extensão.
    Suporta .txt, .pdf ou .eml.
    """
    filename = file.filename
    content = await file.read() # Lê o arquivo

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
            return "" # Retorna vazio se não encontrar texto plano

        else:
            # Se o formato não for suportado, levanta um erro
            raise HTTPException(status_code=400, detail=f"Formato de arquivo não suportado: {filename}")

    except Exception as e:
        # Captura qualquer erro durante o processamento do arquivo
        raise HTTPException(status_code=500, detail=f"Erro ao processar o arquivo {filename}: {str(e)}")


# --- Endpoints da API ---

@app.get("/", summary="Endpoint raiz da API", description="Verifica se a API está online.")
def read_root():
    """ Endpoint inicial para verificar o status da API. """
    return {"status": "API online e funcionando!"}


@app.post("/processar/", summary="Processa e classifica um email")
async def processar_email(
    email_text: Optional[str] = Form(None),
    email_file: Optional[UploadFile] = File(None)
):
    """
    Recebe o conteúdo de um email via texto direto ou upload de arquivo.
    
    - **email_text**: Texto colado do corpo do email.
    - **email_file**: Arquivo de email nos formatos .txt, .pdf ou .eml.
    
    A API extrai o texto, realiza uma classificação **mock** e sugere uma resposta.
    """
    text_to_process = ""

    # 1. Validação da entrada e extração do texto
    if email_text and email_text.strip():
        text_to_process = email_text
    elif email_file:
        text_to_process = await extract_text_from_file(email_file)
    else:
        # Se nem texto nem arquivo forem enviados, retorna erro 400
        raise HTTPException(status_code=400, detail="Nenhum texto ou arquivo foi enviado para processamento.")

    if not text_to_process or not text_to_process.strip():
        raise HTTPException(status_code=400, detail="O conteúdo do email está vazio ou não pôde ser lido.")

    #TODO Lógica de Classificação e Resposta (MOCK)
    categoria_mock = "Improdutivo"
    resposta_mock = "Agradecemos sua mensagem! Tenha um ótimo dia."

    #TODO Uma lógica simples para simular a classificação
    palavras_chave_produtivas = ["ajuda", "problema", "status", "solicitação", "urgente", "dúvida"]
    if any(palavra in text_to_process.lower() for palavra in palavras_chave_produtivas):
        categoria_mock = "Produtivo"
        resposta_mock = "Olá, recebemos sua solicitação e nossa equipe já está trabalhando nela. Em breve, você receberá uma atualização. Atenciosamente."

    # 3. Retornar o resultado
    return JSONResponse(content={
        "categoria": categoria_mock,
        "resposta_sugerida": resposta_mock,
        "texto_extraido": text_to_process[:500] + "..." # Retorna um trecho do texto para verificação
    })