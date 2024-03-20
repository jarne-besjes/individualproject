FROM node:latest

COPY package*.json ./

RUN npm i
COPY . .

CMD [ "npm", "start" ]
