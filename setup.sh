#docker build -t dashboard-app .
#docker run -p 8050:8050 dashboard-app
#ufw allow 8050/tcp
#############docker-compose up --build -d
#docker-compose logs dashboard
#docker logs -f powerbi_dashboard_1
#pip install --upgrade -r requirements.txt
#pip freeze > requirements_novo.txt



#!/bin/bash

# =================================================================
# SCRIPT DE SETUP - DASHBOARD APP
# =================================================================

# 1. Corrigir quebras de linha caso o arquivo tenha vindo do Windows
sed -i 's/\r//' "$0"
apt-get update && apt-get install -y curl
apt-get install -y docker.io
apt-get install -y docker-buildx
# 2. Atualizar repositórios
echo "Refrescando índices de pacotes..."
apt-get update

# 3. Instalar/Verificar Docker Compose
# Tentativa via apt primeiro
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "Instalando Docker Compose via binário direto (GitHub)..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
fi

# 4. Configuração de Firewall
echo "Configurando portas no firewall..."
if command -v ufw &> /dev/null; then
    ufw allow 8050/tcp
else
    echo "UFW não encontrado, pulando regra de firewall."
fi

# 5. Subir o Container
echo "Iniciando build e deploy do container..."

# Exportamos a variável para que o docker-compose a enxergue
export DOCKER_BUILDKIT=0
export COMPOSE_DOCKER_CLI_BUILD=0

if docker-compose up --build -d; then
    echo "------------------------------------------"
    echo "Dashboard iniciado com sucesso na porta 8050!"
    echo "Acesse em: http://seu-ip:8050"
    echo "Para ver os logs, use: docker-compose logs -f"
    echo "------------------------------------------"
else
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo "ERRO: Falha ao subir o container."
    echo "Verifique o Dockerfile ou o docker-compose.yml"
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    exit 1
fi