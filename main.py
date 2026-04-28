
import os
import subprocess
import time
from typing import Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from bot import TRT2Bot

def iniciar_tor():
    if os.getenv("USE_TOR") == "true":
        print("[*] Iniciando serviço Tor...")
        try:
            subprocess.Popen(["tor"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # Aguarda o Tor abrir a porta SOCKS 9050
            time.sleep(15)
            print("[*] Tor pronto.")
        except Exception as e:
            print(f"[!] Erro ao iniciar Tor: {e}")

iniciar_tor()

app = FastAPI(title="TRT2 Scraper")

# Configurações
URL_BASE = os.getenv("TRIBUNAL_URL_BASE", "https://pje.trt2.jus.br/pje-consulta-api/api/processos")
KEY_2CAP = os.getenv("API_KEY_2CAPTCHA", "")

bot = TRT2Bot(tribunal_url_base=URL_BASE, api_key_2captcha=KEY_2CAP)
ongoing: Dict[str, Dict] = {}

class Consulta(BaseModel):
    numero_processo: str

class Resolver(BaseModel):
    challenge_id: str
    resposta: str

@app.get("/")
async def health():
    return {"status": "online", "tor": os.getenv("USE_TOR") == "true"}

@app.post("/consultar_processo")
async def consultar(req: Consulta):
    res = bot.obter_dados_processo(req.numero_processo)
    if res["status"] == "captcha_required":
        ongoing[res["challenge_id"]] = {
            "num": req.numero_processo,
            "token": res["token_desafio"]
        }
    return res

@app.post("/resolver_captcha")
async def resolver(req: Resolver):
    data = ongoing.get(req.challenge_id)
    if not data: raise HTTPException(status_code=400, detail="ID expirado")
    
    res = bot.obter_dados_processo(data["num"], req.resposta, data["token"])
    if res["status"] == "success":
        del ongoing[req.challenge_id]
    return res
