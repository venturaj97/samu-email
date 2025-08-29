from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import nltk

from app.api import router as api_router

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

app = FastAPI(
    title="SAMU API - Email",
    description="Samu é um sistema simples utilizado para ler emails, descarta o que nao é relevante e responder o que é necessário.",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui o roteador da nossa API
app.include_router(api_router, prefix="/api", tags=["Análise de Email"]) # Adicionamos um prefixo /api

# Monta a pasta 'static' para servir os arquivos de frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=FileResponse, tags=["Frontend"])
async def read_index(request: Request):
    """Serve o arquivo principal do frontend."""
    return "static/index.html"