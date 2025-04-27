# Используем официальный образ Node.js
FROM node:16

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем package.json и package-lock.json
COPY --chown=node:node package.json .
RUN cd /usr/src/app && npm install

COPY --chown=node:node . .
USER node
#RUN chmod 777 /app/node_modules

# Копируем исходный код
COPY . .

# Собираем приложение
RUN npm run build

# Указываем порт, который будет использовать приложение
EXPOSE 3000

# Запускаем приложение
CMD ["npm", "start"]
