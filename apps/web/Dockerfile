FROM node:20-alpine
WORKDIR /app
COPY package.json tsconfig.json next.config.ts ./
COPY app ./app
COPY components ./components
COPY public ./public
RUN npm install
EXPOSE 3000
CMD ["npm", "run", "dev"]
