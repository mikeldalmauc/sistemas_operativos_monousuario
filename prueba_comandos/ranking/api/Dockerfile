FROM node:20-alpine
WORKDIR /app
COPY server.js package.json ./
ENV DATOS=/datos PUERTO=3000
VOLUME ["/datos"]
EXPOSE 3000
CMD ["node", "server.js"]
