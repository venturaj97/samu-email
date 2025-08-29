import smtplib
from email.message import EmailMessage
from . import config

async def send_email(destinatario: str, assunto: str, corpo: str):
    """
    Envia um email usando as credenciais do ambiente.
    """
    email_address = config.EMAIL_ADDRESS
    email_password = config.EMAIL_APP_PASSWORD

    if not email_address or not email_password:
        print("ERRO: Credenciais de email não configuradas no .env")
        return False

    msg = EmailMessage()
    msg['Subject'] = assunto
    msg['From'] = email_address
    msg['To'] = destinatario
    msg.set_content(corpo)

    try:
        # Conecta-se ao servidor SMTP do Gmail
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(email_address, email_password)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print(f"Falha ao enviar email: {e}")
        return False