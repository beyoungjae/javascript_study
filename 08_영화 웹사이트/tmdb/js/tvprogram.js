const options = {
   method: 'GET',
   headers: {
      accept: 'application/json',
      Authorization: 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5ZWYxY2NlNzQzOWNiOTU0ZDg4ODY3N2Y0NmNmOGNiMyIsIm5iZiI6MTczMDA3NjA2Ny4wNDc5NDUsInN1YiI6IjY3MWFlOTk4MjdiZDU3ZDkxZjYyODA3NCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.0PAtZsXmyjUikPahLBmha3w_PZvUrL0ANb5fry9iMhM',
   },
}

const url = 'https://api.themoviedb.org/3/tv/popular?language=ko-KR&page=1'

const getTvprograms = async (url) => {
   try {
      const response = await fetch(url, options)

      const data = await response.json()
      const results = data.results.slice(0, 10) // tv프로그램 데이터 추출해서 results 변수에 저장
      const container = document.querySelector('main .container')
      let rowsHtml = ''
      for (let i = 0; i < results.length; i += 2) {
         let rowhtml = '<div class="row">'
         for (let j = 0; j < 2; j++) {
            const index = i + j
            if (index >= results.length) break

            const Tvprogram = results[index]
            rowhtml += `
                 <div class="col-sm-6 d-flex align-items-stretch p-3">
                     <div class="card" style="display: flex; flex-direction: row; align-items: flex-start; padding: 20px; gap: 20px; width: 100%; border: 1px solid #ddd; box-shadow: 0px 4px 8px rgba(0,0,0,0.1);">
                        <a href="./tvprodetail.html?movie_id=${Tvprogram.id}">
                           <img src="https://image.tmdb.org/t/p/w500${Tvprogram.poster_path}" class="card-img-top poster" alt="${Tvprogram.name}" style="width: 200px; height: auto; border-radius: 5px;" />
                        </a>
                        <div class="card-body" style="text-align: left;">
                           <h4>${Tvprogram.name}</h4>
                           <p class="card-text average">평점: ${Tvprogram.vote_average > 0 ? Tvprogram.vote_average.toFixed(1) : '평점 없음'}점</p>
                           <p>줄거리: ${Tvprogram.overview.length > 10 ? Tvprogram.overview.slice(0, 10) + '...' : Tvprogram.overview ? Tvprogram.overview : '줄거리 없음'}</p>
                        </div>
                     </div>
               </div>
               `
         }

         rowhtml += '</div>'
         rowsHtml += rowhtml
      }

      container.innerHTML += rowsHtml
   } catch (error) {
      console.log('에러 발생:', error)
   }
}

getTvprograms(url)
