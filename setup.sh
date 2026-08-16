#!/bin/bash
#
#docker build -t dashboard-app .
#docker run -p 8050:8050 dashboard-app
#ufw allow 8050/tcp
#############docker-compose up --build -d
#docker-compose logs dashboard
#docker logs -f powerbi_dashboard_1
#pip install --upgrade -r requirements.txt
#pip freeze > requirements_novo.txt




# =================================================================
# SCRIPT DE SETUP - DASHBOARD APP
# =================================================================

# 1. Corrigir quebras de linha caso o arquivo tenha vindo do Windows
#!/bin/bash

# =================================================================
# SCRIPT DE SETUP - DASHBOARD APP (CORRIGIDO)
# =================================================================

# 1. Destravar pacotes e atualizar dependências básicas
apt-get install -f -y
apt-get clean
apt-get update && apt-get install -y curl

# Garante o Docker moderno (que já vem com buildx e compose integrados)
apt-get install -y docker.io docker-compose-plugin

# 2. Atualizar repositórios
echo "Refrescando índices de pacotes..."
apt-get update

# 3. Configuração de Firewall
echo "Configurando portas no firewall..."
if command -v ufw &> /dev/null; then
    ufw allow 8050/tcp
else
    echo "UFW não encontrado, pulando regra de firewall."
fi

# 4. Subir o Container
echo "Iniciando build e deploy do container..."

# Usando o comando moderno "docker compose" (sem hífen)
if docker compose up --build -d; then
    echo "------------------------------------------"
    echo "Dashboard iniciado com sucesso na porta 8050!"
    echo "Acesse em: http://vmlinuxd:8050"
    echo "Para ver os logs, use: docker compose logs -f"
    echo "------------------------------------------"
else
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo "ERRO: Falha ao subir o container."
    echo "Verifique o Dockerfile ou o docker-compose.yml"
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    exit 1
fi