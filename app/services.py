import io
import email
from email.policy import default

import PyPDF2
from nltk.tokenize import sent_tokenize
from fastapi import UploadFile, HTTPException
from openai import AsyncOpenAI

from . import config

client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)


def preprocess_text_for_nlp(text: str) -> str:
    """Limpa e prepara o texto."""
    sentences = sent_tokenize(text, language='portuguese')
    clean_text = " ".join(sentence.strip() for sentence in sentences)
    return clean_text


async def get_ai_classification(text: str) -> dict:
    """Usa a API da OpenAI (GPT) para classificar o texto e gerar uma resposta."""
    # A verificação agora usa o objeto client diretamente
    if not client.api_key:
        raise HTTPException(status_code=500, detail="Chave da API da OpenAI não configurada.")


    system_prompt = """
    Você é um assistente de IA especialista em analisar e responder emails.
    Sua tarefa é:
    1. Classificar o email como 'Produtivo' ou 'Improdutivo'. Um email 'Produtivo' requer uma ação. Um email 'Improdutivo' é social, informativo ou um agradecimento.
    2. Gerar uma resposta curta e profissional baseada no conteúdo do email.
    3. Sua resposta final DEVE ser um objeto JSON com duas chaves: "categoria" e "resposta_sugerida".
    """
    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            response_format={"type": "json_object"}, # Garante que a resposta seja JSON
            temperature=0.2,
        )
        # Retornamos o dicionário diretamente
        import json
        result = json.loads(response.choices[0].message.content.strip())
        return result
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Erro na comunicação com a API da OpenAI: {str(e)}")


async def extract_text_from_file(file: UploadFile) -> str:
    """Extrai o texto de um arquivo com base na sua extensão."""
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
        
        # --- LÓGICA CORRIGIDA AQUI ---
        elif filename.endswith(".eml"):
            msg = email.message_from_bytes(content, policy=default)
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        return part.get_payload(decode=True).decode()
            else: # Se não for multipart, pega o payload principal
                return msg.get_payload(decode=True).decode()
            return "" # Retorna vazio se não encontrar texto plano no multipart

        else:
            raise HTTPException(status_code=400, detail=f"Formato de arquivo não suportado: {filename}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar o arquivo {filename}: {str(e)}")