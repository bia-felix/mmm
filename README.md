# Graças Aventais - sistema de encomendas (protótipo local)

## O que já funciona
- Login com três perfis (administrador, cortador e bordador).
- Administrador cadastra pedidos de jaleco ou pijama cirúrgico.
- Formulário com medidas, modelo feminino/masculino, gola tradicional/padre, tecido, cor, bolsos, punhos e detalhes de pijamas.
- Bordado condicional, texto, local (inclusive bolso), cor, fonte, símbolo e upload de referência.
- Cortador vê somente dados de corte; bordador vê somente dados de bordado; administrador vê tudo.
- Status separado por setor, banco de dados SQLite e layout responsivo.

## Como executar
1. Instale Python 3.10+.
2. No terminal, entre nesta pasta.
3. Execute: `python -m pip install -r requirements.txt`
4. Execute: `python app.py`
5. Abra http://127.0.0.1:5000 no navegador.

## Logins iniciais (ALTERE AS SENHAS ANTES DE USAR DADOS REAIS)
- admin / Admin@2026!
- cortador / Corte@2026!
- bordador / Bordado@2026!

Cada perfil pode mudar sua própria senha em "Senha".

## Importante antes de usar na loja
Este é um MVP para teste local, NÃO um sistema pronto para expor publicamente. Ainda é necessário: HTTPS, hospedagem com backups, proteção CSRF, gerenciamento administrativo de usuários, recuperação de senhas, controles de privacidade e LGPD, validação mais rigorosa dos uploads, auditoria e testes de segurança. O banco SQLite é criado automaticamente e fica na pasta do projeto. Não compartilhe o banco ou a pasta uploads. A chave SECRET_KEY deve ser persistente e secreta em produção. Para uso simultâneo em diferentes aparelhos, implante em um servidor seguro.
