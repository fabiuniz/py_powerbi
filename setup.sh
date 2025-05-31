#docker build -t dashboard-app .
#docker run -p 8050:8050 dashboard-app
#ufw allow 8050/tcp
docker-compose up --build -d
#docker-compose logs dashboard
