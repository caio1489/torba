
import os
import time
import uuid
import base64
import random
from typing import Optional, Dict

# Tenta importar ddddocr de forma segura
try:
    import ddddocr
    HAS_DDDDOCR = True
except ImportError:
    HAS_DDDDOCR = False

from curl_cffi import requests

class TRT2Bot:
    def __init__(self, tribunal_url_base: str, api_key_2captcha: str):
        self.tribunal_url_base = tribunal_url_base.rstrip('/')
        self.api_key_2captcha = api_key_2captcha
        self.impersonate = "chrome120"
        
        # Inicializa OCR local se disponível
        self.ocr = None
        if HAS_DDDDOCR:
            try:
                self.ocr = ddddocr.DdddOcr(show_ad=False)
            except Exception as e:
                print(f"[!] Erro ao inicializar ddddocr: {e}")

        # Configuração de Proxy via Tor
        self.proxy = None
        if os.getenv("USE_TOR") == "true":
            self.proxy = "socks5://127.0.0.1:9050"

    def _get_headers(self, numero_processo: str) -> Dict[str, str]:
        """Headers otimizados para simular Chrome Real e evitar 403"""
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": f"https://pje.trt2.jus.br/pje-consulta/detalhe-processo/{numero_processo}/1/",
            "Origin": "https://pje.trt2.jus.br",
            "X-Grau-Instancia": "1",
            "sec-ch-ua": "\"Not_A Brand\";v=\"8\", \"Chromium\";v=\"120\", \"Google Chrome\";v=\"120\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
        }

    def _resolver_captcha_local(self, imagem_b64: str) -> Optional[str]:
        if not self.ocr: return None
        try:
            img_bytes = base64.b64decode(imagem_b64)
            return self.ocr.classification(img_bytes)
        except: return None

    def _resolver_captcha_2captcha(self, imagem_b64: str) -> Optional[str]:
        if not self.api_key_2captcha or len(self.api_key_2captcha) < 10: return None
        try:
            import requests as req_std
            res = req_std.post("http://2captcha.com/in.php", data={
                "key": self.api_key_2captcha, "method": "base64", "body": imagem_b64, "json": 1
            }, timeout=15)
            rid = res.json().get("request")
            if not rid: return None
            for _ in range(20):
                time.sleep(5)
                res_res = req_std.get(f"http://2captcha.com/res.php?key={self.api_key_2captcha}&action=get&id={rid}&json=1")
                if res_res.json().get("status") == 1: return res_res.json().get("request")
            return None
        except: return None

    def obter_dados_processo(self, numero_processo: str, captcha_resposta: Optional[str] = None, token_desafio: Optional[str] = None) -> Dict:
        headers = self._get_headers(numero_processo)
        proxies = {"http": self.proxy, "https": self.proxy} if self.proxy else None

        try:
            # 1. Obter ID interno
            url_id = f"{self.tribunal_url_base}/dadosbasicos/{numero_processo}"
            resp_id = requests.get(url_id, headers=headers, impersonate=self.impersonate, proxies=proxies, timeout=30)
            
            if resp_id.status_code == 403:
                return {"status": "error", "message": "Bloqueio 403 detectado pelo Tribunal."}
            
            data_id = resp_id.json()
            # Trata retorno como lista ou objeto
            proc_id = data_id[0].get("id") if isinstance(data_id, list) and data_id else data_id.get("id")
            
            if not proc_id:
                return {"status": "error", "message": "Processo não localizado."}

            url_api = f"{self.tribunal_url_base}/{proc_id}"

            # 2. Se já temos resposta, validar
            if captcha_resposta and token_desafio:
                url_val = f"{url_api}?tokenDesafio={token_desafio}&resposta={captcha_resposta}"
                resp_val = requests.get(url_val, headers=headers, impersonate=self.impersonate, proxies=proxies, timeout=30)
                
                # O token de sucesso vem no header 'captchaToken'
                final_token = resp_val.headers.get("captchaToken")
                if not final_token:
                    return {"status": "error", "message": "Captcha inválido. Tente novamente."}
                
                # Com o token, faz a chamada final para pegar os dados
                headers["captchaToken"] = final_token
                resp_final = requests.get(url_api, headers=headers, impersonate=self.impersonate, proxies=proxies, timeout=30)
                return {"status": "success", "data": resp_final.json()}

            # 3. Senão, solicitar desafio
            resp_c = requests.get(url_api, headers=headers, impersonate=self.impersonate, proxies=proxies, timeout=30)
            data_c = resp_c.json()
            
            img_b64 = data_c.get("imagem") or data_c.get("imagemCaptcha")
            tk_desafio = resp_c.headers.get("captchaToken") or data_c.get("tokenDesafio")

            # Tentativa automática
            auto_res = self._resolver_captcha_local(img_b64) or self._resolver_captcha_2captcha(img_b64)
            if auto_res:
                # Tenta validar auto
                url_v = f"{url_api}?tokenDesafio={tk_desafio}&resposta={auto_res}"
                rv = requests.get(url_v, headers=headers, impersonate=self.impersonate, proxies=proxies, timeout=30)
                ft = rv.headers.get("captchaToken")
                if ft:
                    headers["captchaToken"] = ft
                    rf = requests.get(url_api, headers=headers, impersonate=self.impersonate, proxies=proxies, timeout=30)
                    return {"status": "success", "data": rf.json()}

            # Fallback manual
            return {
                "status": "captcha_required",
                "challenge_id": str(uuid.uuid4()),
                "imagem_captcha_base64": img_b64,
                "token_desafio": tk_desafio
            }

        except Exception as e:
            return {"status": "error", "message": f"Erro: {str(e)}"}
