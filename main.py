from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from bot import TRT2Bot

app = FastAPI()
bot = TRT2Bot()

class ConsultaRequest(BaseModel):
    numero_processo: str

class ResolverRequest(BaseModel):
    challenge_id: str
    resposta: str

@app.get("/")
async def health_check():
    return {"status": "online", "engine": "selenium"}

@app.post("/consultar_processo")
async def consultar_processo(req: ConsultaRequest):
    result = bot.iniciar_consulta(req.numero_processo)
    return result

@app.post("/resolver_captcha")
async def resolver_captcha(req: ResolverRequest):
    result = bot.resolver_e_obter_dados(req.challenge_id, req.resposta)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
