## Тестовое задание для вакансии разработчика в компании Eduson.tv  

### Запущен на боте https://t.me/eduson_test_task_bot

### Запуск:
1. Клонируем репозиторий
2. Кладём файл .env рядом с docker-compose.yml.   
   **Содержимое файла .env:**
   ```
   TG_TOKEN=1234567890
   
   POSTGRES_HOST=eduson_db
   POSTGRES_USER=test_user
   POSTGRES_PASSWORD=strong_password
   POSTGRES_DB=eduson_bot
   POSTGRES_PORT=5432
   
   REDIS_HOST=eduson_redis
   REDIS_PORT=6379
   REDIS_PASSWORD=strong_password
   REDIS_ARGS=--requirepass strong_password
   ```
   Нужно поменять только телеграм токен, и при желании сменить логины-пароли
3. Запускаем билд: `sudo docker-compose up --build`
