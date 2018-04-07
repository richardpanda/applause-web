FROM node:9-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY package.json yarn.lock /usr/src/app/
RUN yarn install

COPY . .

RUN yarn build
RUN yarn global add serve

CMD ["serve", "-s", "build"]
