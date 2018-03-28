FROM python:3.6-jessie

RUN apt-get update

RUN wget -O /tmp/google-chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i /tmp/google-chrome.deb; apt-get -fy install

RUN apt-get install unzip
RUN wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/2.37/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip -d /usr/local/bin

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV APPLAUSE_WEB__ENV="production"
ENV APPLAUSE_WEB__FACEBOOK_USERNAME=""
ENV APPLAUSE_WEB__FACEBOOK_PASSWORD=""
ENV APPLAUSE_WEB__SERVER_PORT="80"

EXPOSE 80

CMD ["python", "main.py"]
