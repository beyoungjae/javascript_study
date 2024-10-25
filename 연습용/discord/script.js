// script.js
async function fetchNotifications() {
   const response = await fetch('https://discord.com/api/webhooks/1295056404003950653/9deyJCnUkW8nLZUfvrI0tFDgZqQTYRDVNC8z8JThaw2LTi6RH49NE8SgVL8bpX05sl6y') // 웹훅 URL
   const data = await response.json()

   const notificationsDiv = document.getElementById('notifications')
   notificationsDiv.innerHTML = '' // 기존 내용 지우기

   data.forEach((notification) => {
      const div = document.createElement('div')
      div.classList.add('notification')
      div.innerText = notification.content // 알림 내용 표시
      notificationsDiv.appendChild(div)
   })
}

// 주기적으로 알림 수신
setInterval(fetchNotifications, 5000) // 5초마다 알림 체크
