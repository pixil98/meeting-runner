FROM python:3.7-slim

# Create app directory
WORKDIR /app

COPY . .
#RUN apt-get update && \
#    apt-get -y install gcc pkg-config
RUN pip install --no-cache-dir -r requirements.txt
CMD [ "python", "bot.py" ]