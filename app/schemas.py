from pydantic import BaseModel, Field

class AnaliseResponse(BaseModel):
    """
    Define a estrutura da resposta da análise de email.
    """
    categoria: str = Field(..., example="Produtivo", description="A categoria classificada para o email.")
    resposta_sugerida: str = Field(..., example="Olá, recebemos sua solicitação...", description="A sugestão de resposta gerada pela IA.")
    

class EmailRequest(BaseModel):
    destinatario: str
    mensagem: str