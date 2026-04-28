# Instruções de Configuração - Easypanel (Nixpacks)

Para garantir que o sistema funcione com **Tor**, **curl_cffi** e **ddddocr** sem erros de build, siga estas etapas:

### 1. Configuração de Pacotes (Essencial)
No Easypanel, na aba de configuração do serviço, adicione:

- **Pacotes APT**: `tor build-essential python3-dev libgl1 libglib2.0-0 libsm6 libxext6 libxrender-dev`
- **Pacotes Nix**: (deixe vazio)

### 2. Comando de Início
- **Comando**: `PYTHONPATH=. python -m uvicorn main:app --host 0.0.0.0 --port 8000`

### 3. Variáveis de Ambiente
| Variável | Valor |
| :--- | :--- |
| `USE_TOR` | `true` |
| `API_KEY_2CAPTCHA` | (Sua chave, se tiver) |
| `TRIBUNAL_URL_BASE` | `https://pje.trt2.jus.br/pje-consulta-api/api/processos` |
| `NIXPACKS_PYTHON_VERSION` | `3.11` |

### 4. Notas
- O `ddddocr` tentará resolver o captcha localmente. Se o build dele falhar por falta de memória no servidor, o bot continuará funcionando usando o 2Captcha ou o modo manual.
- O Tor garante o bypass do erro 403.
