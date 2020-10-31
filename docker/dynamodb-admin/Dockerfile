FROM aaronshaf/dynamodb-admin

ADD . .

RUN npm install

EXPOSE 8001
CMD ["node", "bin/dynamodb-admin.js"]
