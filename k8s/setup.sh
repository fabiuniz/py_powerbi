#!/bin/bash

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' 

echo -e "${BLUE}🚀 Iniciando o setup completo no vmlinuxd...${NC}"

# --- 1. INSTALAÇÃO AUTOMÁTICA DE REQUISITOS ---
install_requirements() {
    if ! command -v docker &> /dev/null; then
        echo -e "${YELLOW}Instalando Docker...${NC}"
        sudo apt-get update && sudo apt-get install -y docker.io
        sudo usermod -aG docker $USER
    fi

    if ! command -v kubectl &> /dev/null; then
        echo -e "${YELLOW}Instalando Kubectl...${NC}"
        curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
        sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
        rm kubectl
    fi

    if ! command -v minikube &> /dev/null; then
        echo -e "${YELLOW}Instalando Minikube...${NC}"
        curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
        sudo install minikube-linux-amd64 /usr/local/bin/minikube
        rm minikube-linux-amd64
    fi
}

install_requirements

# --- 2. INICIALIZAÇÃO DOS SERVIÇOS ---
echo -e "${BLUE}⚙️ Verificando serviços...${NC}"
sudo service docker start

if ! minikube status > /dev/null 2>&1; then
    echo -e "${YELLOW}☸️ Iniciando Minikube ...${NC}"
    FORCE_FLAG=""
    [ "$USER" == "root" ] && FORCE_FLAG="--force"
    minikube start --driver=docker $FORCE_FLAG --memory=1700mb
fi

# --- 3. O PULO DO GATO: ESPERAR O API SERVER ---
echo -e "${YELLOW}⏳ Aguardando o servidor Kubernetes responder...${NC}"
until kubectl cluster-info > /dev/null 2>&1; do
    echo -n "."
    sleep 3
done
echo -e "${GREEN} OK!${NC}"

# --- 4. DEPLOY DO PROJETO ---
echo -e "${BLUE}🔗 Sincronizando Docker com Minikube...${NC}"
eval $(minikube docker-env)

echo -e "${BLUE}📦 Buildando imagem diretamente no Minikube...${NC}"
# Usamos o caminho absoluto ou garantimos o contexto do Dockerfile
docker build -t powerbi_dashboard_1:latest ..

echo -e "${BLUE}☸️ Aplicando Kubernetes...${NC}"
kubectl apply -f powerbi-dep.yaml
kubectl apply -f powerbi-svc.yaml

echo -e "${YELLOW}⏳ Aguardando Pod ficar pronto...${NC}"
# Tentativa de wait mais flexível usando o seletor de app
kubectl wait --for=condition=ready pod -l app=powerbi --timeout=60s || {
    echo -e "${RED}❌ O Pod demorou muito para iniciar. Verifique com 'kubectl describe pod'${NC}"
    exit 1
}

echo -e "${GREEN}✅ TUDO PRONTO!${NC}"
IP_WSL=$(hostname -I | awk '{print $1}')
echo -e "${BLUE}🔗 Link: ${GREEN}http://vmlinuxd:8888${NC}"
echo -e "${YELLOW}Dica: No Windows, adicione no C:\Windows\System32\drivers\etc\hosts:${NC}"
echo -e "${WHITE}      $IP_WSL vmlinuxd${NC}"

# --- 5. PORT FORWARD ---
echo -e "${BLUE}📡 Iniciando Port-Forward (mantenha este terminal aberto)...${NC}"
kubectl port-forward svc/powerbi-service 8888:8050 --address 0.0.0.0