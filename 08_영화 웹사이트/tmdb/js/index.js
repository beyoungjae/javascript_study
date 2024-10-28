// 서버한테 같이 전달하는 포스트잇 같은 느낌
const options = {
   method: 'GET', // RestFul 방식 중 GET방식으로 요청
   headers: {
      accept: 'application/json', // 저는 json 객체 형태로 데이터를 받을게요 라고 서버에게 요청
      // 보안을 위해서 서버에서 주는 인증키
      Authorization: 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5ZWYxY2NlNzQzOWNiOTU0ZDg4ODY3N2Y0NmNmOGNiMyIsIm5iZiI6MTcyOTgyNTU2OC4yMjIyOTUsInN1YiI6IjY3MWFlOTk4MjdiZDU3ZDkxZjYyODA3NCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.BVl9E28Z_4_3hqAgAI-HuSd1rGGu2LvWLDJB8ZdzBI0',
   },
}

// fetch: 서버에 request를 요청하는 자바스크립트에서 제공하는 함수
// fetch(request 주소, request 할때 서버에 같이 전달하는 옵션)
// 물음표 뒤에는 쿼리스트링: 서버에 보내는 값들

/*
왜? fetch는 promise를 사용할까?(왜 비동기일까?)

promise, async, await -> 비동기
request 해주는 과정을 비동기로 동작시키고 있다.

서버에 장애가 있거나 네트워크 문제가 있거나 했을때 동기적으로 실행이 된다면
사용자는 다른 작업을 할 수 없음 -> 따라서 request 작업은 비동기로 진행된다.
*/

const url = 'https://api.themoviedb.org/3/movie/now_playing?language=ko-KR&page=1&region=KR'

const getPlayingMovies = async (url) => {
   try {
      const response = await fetch(url, options) // 서버에서 데이터를 가져올때까지 기다린다.
      // console.log(response) // 기다렸다가 다 가지고 오면 await 밑에 있는 코드를 실행

      const data = await response.json() // await를 지정하는 이유 : fetch는 비동기적으로 실행되므로 서버에서 request 해오는 딜레이 시간 중에 실행 된다.
      const results = data.results
      const container = document.querySelector('main .container')
      let rowsHtml = '' // 모든 row를 담을 문자열 변수

      for (let i = 0; i < results.length; i += 4) {
         // 5번 반복 => row를 5개 만들어준다.
         let rowHtml = '<div class="row">'

         for (let j = 0; j < 4; j++) {
            // 4번 반복 => col을 4개 만들어준다
            const index = i + j
            if (index >= results.length) break // results 배열을 벗어나면 중단

            const movie = results[index]
            rowHtml += `
                    <div class="col-sm-3 p-3">
                        <div class="card">
                            <a href="./detail.html?movie_id=${movie.id}"><img src="https://image.tmdb.org/t/p/w500${movie.poster_path}" class="card-img-top poster" alt="${movie.title}" /></a>
                        <div class="card-body">
                           <p class="card-text title">${movie.title}</p>
                           <p class="card-text average">평점: ${movie.vote_average.toFixed(1)}점</p>
                        </div>
                     </div>
                     </div>
                     `
         }

         rowHtml += '</div>'
         rowsHtml += rowHtml
      }

      container.innerHTML = rowsHtml
   } catch (error) {
      console.log('에러 발생:', error)
   }
}
getPlayingMovies(url)

// getPlayingMovies(url)
//    .then((res) => {
//       console.log(res) // response 정보 + 데이터
//       return res.json() // 실제 데이터만 리턴
//    })
//    .then((res) => console.log(res))
//    .catch((err) => console.error(err)) // request할때 문제 발생시 실행
