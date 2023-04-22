FROM node:lts-slim

WORKDIR /app

COPY package.json .
COPY package-lock.json .
RUN npm ci

COPY . .

EXPOSE 4200

ENTRYPOINT ["npm"]
CMD ["start"]
