FROM python:3.13-slim

# Create app directory
WORKDIR /app

COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD [ "python", "bot.py" ]