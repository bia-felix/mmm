# Graças Aventais: demonstração no Render

**Somente para testes com dados fictícios.** No Render gratuito, o banco SQLite em /tmp é temporário e pode ser apagado. Não use para pedidos reais.

## Como publicar
1. Envie os **arquivos dentro da pasta gracas_aventais** para a raiz do repositório GitHub. `app.py` e `requirements.txt` devem aparecer na raiz.
2. Render > New > Web Service > GitHub > selecione o repositório.
3. Runtime: Python 3. Build Command: `pip install -r requirements.txt`. Start Command: `gunicorn app:app`. Root Directory: vazio.
4. Environment: `DEMO_MODE=1`, `SECRET_KEY` (valor aleatório forte), `ADMIN_PASSWORD`, `CUTTER_PASSWORD`, `EMBROIDERER_PASSWORD` (três senhas fortes diferentes). Não coloque senhas no GitHub.
5. Selecione Free se disponível e Deploy.
6. Logins: admin, cortador, bordador, cada um com a senha configurada no Render.

**Importante:** a demonstração não é uma versão pronta para produção. Antes de uso real, implantar armazenamento persistente, backups, auditoria, proteção contra tentativas de login, controles LGPD, revisão de segurança e uploads. Não use dados reais de clientes.
