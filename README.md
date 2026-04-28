# Guia de Implementação: TRT2 Selenium no Easypanel

Para rodar o Selenium no seu servidor via Nixpacks, você precisa garantir que o Google Chrome e as dependências do sistema estejam instalados.

## 1. Configuração do Nixpacks

No seu painel do Easypanel, vá em **General > Build Settings** e adicione ou edite o arquivo `nixpacks.toml` na raiz do projeto:

```toml
[phases.setup]
nixPkgs = ["python311", "google-chrome", "chromedriver"]

[phases.install]
cmds = ["pip install fastapi uvicorn selenium undetected-chromedriver pydantic"]
```

## 2. Dependências Adicionais (Importante)

O Chrome no Linux precisa de bibliotecas específicas para rodar em modo headless. Se o Nixpacks padrão não as incluir, você pode precisar forçar a instalação via comandos de setup.

## 3. Arquivos do Projeto

Certifique-se de que os arquivos `main.py` e `bot.py` enviados estão na raiz do seu repositório.

## 4. Notas Técnicas

- **Seletores de ID**: No arquivo `bot.py`, deixei comentários como `# Substituir pelo ID real`. Você precisará inspecionar o site do TRT2 para pegar os IDs exatos do elemento de imagem do captcha, do campo de texto e do botão de busca.
- **Headless Mode**: O código já está configurado para `--headless`, essencial para servidores sem monitor.
- **Undetected Chromedriver**: Esta biblioteca baixa automaticamente o driver compatível com a versão do Chrome instalada no sistema.
```
