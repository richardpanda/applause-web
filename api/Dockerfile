FROM python:3.6-alpine3.7

RUN echo "@edge http://nl.alpinelinux.org/alpine/edge/main" >> /etc/apk/repositories
RUN echo "@testing http://nl.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories
RUN apk update
RUN apk add --update openssl

RUN wget -O /tmp/geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/v0.20.0/geckodriver-v0.20.0-linux64.tar.gz
RUN tar -xvzf /tmp/geckodriver.tar.gz -C /usr/local/bin

RUN apk add icu-libs@edge
RUN apk add firefox@testing

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV APPLAUSE_WEB__ENV="production"
ENV APPLAUSE_WEB__FACEBOOK_USERNAME=""
ENV APPLAUSE_WEB__FACEBOOK_PASSWORD=""

EXPOSE 8080

CMD ["python", "main.py"]
