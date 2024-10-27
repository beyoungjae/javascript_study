async function fetchNotifications() {
   try {
      const response = await fetch('https://discord.com/api/webhooks/1295056404003950653/9deyJCnUkW8nLZUfvrI0tFDgZqQTYRDVNC8z8JThaw2LTi6RH49NE8SgVL8bpX05sl6y') // 웹훅 URL
      const data = await response.json()

      console.log(data)

      const notificationsDiv = document.getElementById('notifications')

      // 데이터가 배열인지 확인하고, 단일 객체일 경우 배열로 변환
      const messages = Array.isArray(data) ? data : [data]

      // 서버에서 받은 메시지 중 최근 10개만 남기기
      const recentMessages = messages.slice(0, 10)

      // 화면에 표시
      notificationsDiv.innerHTML = ''
      recentMessages.forEach((notification) => {
         const div = document.createElement('div')
         div.classList.add('notification')

         // Discord 메시지 구조에 맞게 데이터 파싱
         const time = document.createElement('span')
         time.classList.add('time')
         time.innerText = new Date(notification.timestamp || Date.now()).toLocaleString()

         const content = document.createElement('div')
         content.classList.add('content')
         content.innerHTML = `
                <p><strong>종목명:</strong> ${notification.stockName || '데이터 없음'}</p>
                <p><strong>신호:</strong> ${notification.signal || '데이터 없음'}</p>
                <p><strong>RSI:</strong> ${notification.rsi || '데이터 없음'}</p>
                <p><strong>MACD:</strong> ${notification.macd || '데이터 없음'} | <strong>Signal:</strong> ${notification.signalLine || '데이터 없음'}</p>
                <p><strong>종가:</strong> ${notification.close || '데이터 없음'}</p>
                <p><strong>MA50:</strong> ${notification.ma50 || '데이터 없음'} | <strong>MA200:</strong> ${notification.ma200 || '데이터 없음'}</p>
                <p><strong>볼린저 밴드:</strong> Upper ${notification.bollingerUpper || '데이터 없음'}, Lower ${notification.bollingerLower || '데이터 없음'}</p>
                <p><strong>감성 분석:</strong> ${notification.sentiment || '데이터 없음'}</p>
                <p><strong>뉴스 감성 분포:</strong></p>
                <ul>
                    <li>긍정 기사: ${notification.positiveNews || '데이터 없음'} (${notification.positivePercent || '데이터 없음'}%)</li>
                    <li>부정 기사: ${notification.negativeNews || '데이터 없음'} (${notification.negativePercent || '데이터 없음'}%)</li>
                    <li>중립 기사: ${notification.neutralNews || '데이터 없음'} (${notification.neutralPercent || '데이터 없음'}%)</li>
                </ul>
            `

         div.appendChild(time)
         div.appendChild(content)
         notificationsDiv.appendChild(div)
      })
   } catch (error) {
      console.error('알림을 가져오는 데 실패했습니다:', error)
   }
}

// 주기적으로 알림 수신
setInterval(fetchNotifications, 5000) // 5초마다 알림 체크

// 페이지 로드 시 기존 알림 표시
fetchNotifications()
