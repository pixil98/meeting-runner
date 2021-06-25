FROM python:3.7-slim

# Create app directory
WORKDIR /app

COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD [ "python", "bot.py" ]