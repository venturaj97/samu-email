from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from . import services
from . schemas import AnaliseResponse, EmailRequest
from . import email_sender

router = APIRouter()

@router.post("/processar/", response_model=AnaliseResponse, summary="Processa e classifica um email")
async def processar_email(
    email_text: Optional[str] = Form(None),
    email_file: Optional[UploadFile] = File(None)
) -> AnaliseResponse:
    """
    Recebe o conteúdo de um email, o classifica e gera uma resposta sugerida.
    """
    text_to_process = ""

    if email_text and email_text.strip():
        text_to_process = email_text
    elif email_file:
        text_to_process = await services.extract_text_from_file(email_file)
    else:
        raise HTTPException(status_code=400, detail="Nenhum texto ou arquivo foi enviado para processamento.")

    if not text_to_process or not text_to_process.strip():
        raise HTTPException(status_code=400, detail="O conteúdo do email está vazio ou não pôde ser lido.")

    cleaned_text = services.preprocess_text_for_nlp(text_to_process)
    
    # Chama o serviço de IA e obtém o resultado
    ai_result = await services.get_ai_classification(cleaned_text)

    return AnaliseResponse(
        categoria=ai_result.get("categoria", "Indefinido"),
        resposta_sugerida=ai_result.get("resposta_sugerida", "Não foi possível gerar uma resposta.")
    )


@router.post("/enviar-email/", summary="Envia a resposta por email")
async def enviar_resposta_email(request: EmailRequest):
    """
    Recebe um destinatário e uma mensagem, e envia o email.
    """
    sucesso = await email_sender.send_email(
        destinatario=request.destinatario,
        assunto="Resposta à sua solicitação",
        corpo=request.mensagem
    )
    if sucesso:
        return {"status": "Email enviado com sucesso!"}
    else:
        raise HTTPException(status_code=500, detail="Ocorreu um erro interno ao tentar enviar o email.")
