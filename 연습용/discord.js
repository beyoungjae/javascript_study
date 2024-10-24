const express = require('express')
const bodyParser = require('body-parser')
const admin = require('firebase-admin')

const app = express()
app.use(bodyParser.json())

// Firebase Admin SDK 초기화
const serviceAccount = require('./path/to/your/firebase-adminsdk.json')
admin.initializeApp({
   credential: admin.credential.cert(serviceAccount),
   databaseURL: 'https://YOUR_PROJECT_ID.firebaseio.com',
})

app.post('/webhook', (req, res) => {
   const message = req.body.content // 디스코드 메시지 내용
   admin
      .database()
      .ref('messages')
      .push(message)
      .then(() => res.sendStatus(200))
      .catch((error) => res.sendStatus(500))
})

app.listen(3000, () => {
   console.log('서버가 3000 포트에서 실행 중입니다.')
})
