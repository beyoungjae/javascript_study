// 성적 배열
const scores = [85, 90, 78, 92, 88]

// 성적의 합산을 구하는 함수
function sumScores(scores) {
   let sum = 0
   for (let score of scores) {
      sum += score
   }
   return sum
}

// 성적의 평균을 구하는 함수
function averageScore(scores) {
   if (scores.length === 0) return 0 // 배열이 비어있을 경우
   const total = sumScores(scores)
   return total / scores.length
}

// 성적의 합과 평균 계산
const totalScores = sumScores(scores)
const avgScore = averageScore(scores)

// 결과 출력
console.log(`성적의 합: ${totalScores}`)
console.log(`성적의 평균: ${avgScore.toFixed(2)}`) // 소수점 2자리까지 표시
