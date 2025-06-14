# Estágio 1: Build da aplicação React
FROM node:18-alpine AS build

WORKDIR /app

# Copia os arquivos de configuração e instala as dependências
COPY package.json ./
COPY package-lock.json ./
RUN npm install

# Copia todo o código-fonte
COPY . .

# Constrói a aplicação para produção
RUN npm run build

# Estágio 2: Servir os arquivos construídos com Nginx
FROM nginx:1.21.3-alpine

# Remove a configuração padrão do Nginx
RUN rm /etc/nginx/conf.d/default.conf

# Copia a nossa configuração do Nginx
COPY nginx.conf /etc/nginx/conf.d/

# Copia os arquivos estáticos construídos no estágio anterior
COPY --from=build /app/dist /usr/share/nginx/html

# Expõe a porta 80
EXPOSE 80

# Inicia o Nginx
CMD ["nginx", "-g", "daemon off;"]
