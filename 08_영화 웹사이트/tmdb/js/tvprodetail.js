const options = {
   method: 'GET',
   headers: {
      accept: 'application/json',
      Authorization: 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5ZWYxY2NlNzQzOWNiOTU0ZDg4ODY3N2Y0NmNmOGNiMyIsIm5iZiI6MTczMDA3NjA2Ny4wNDc5NDUsInN1YiI6IjY3MWFlOTk4MjdiZDU3ZDkxZjYyODA3NCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.0PAtZsXmyjUikPahLBmha3w_PZvUrL0ANb5fry9iMhM',
   },
}

const urlparmas = new URLSearchParams(window.location.search)

const tvid = urlparmas.get('movie_id')

const tvdetail = `https://api.themoviedb.org/3/tv/${tvid}?language=ko-KR`
const mainContainer = document.querySelector('main .container')

const getDetailTv = async (tvdetail) => {
   try {
      const response = await fetch(tvdetail, options)
      const data = await response.json()
      const tvimg = `https://image.tmdb.org/t/p/w300${data.poster_path}`

      const rowHtml = `
        <div class="row">
        <div class="col-sm-3" style="text-align:center">
        <img src="${tvimg}" alt="${data.name}" class="poster-detail" style="max-width: 100%" />
        </div>
        <div class="col-sm-9">
        <h2>${data.name}</h2>
        <ul class="movie-info">
        <li>원제목: ${data.original_name}, ${data.original_language}</li>
        <li>평점: ${data.vote_average.toFixed(1)}</li>
        <li>최근 방영일: ${data.last_air_date}</li>
        <li>처음 방영일: ${data.first_air_date}</li>
        <li>줄거리: ${data.overview ? data.overview : '줄거리 없음'}</li>
        </ul>
        </div>
        </div>
       `
      mainContainer.innerHTML += rowHtml

      await getseasonTv(seasons)
   } catch (error) {
      console.log('에러 내용:', error)
   }
}
getDetailTv(tvdetail)

const seasons = tvdetail

const getseasonTv = async (seasons) => {
   try {
      const response = await fetch(seasons, options)
      const data2 = await response.json()
      console.log(data2)

      let seasonRowHtml = `
       <div class="row" style="margin-top:30px">
        <div class="col-sm-3 p-3">
            <div class="season">
      `

      data2.seasons.forEach((season, index) => {
         if (index < 7) {
            seasonRowHtml += `
    <a href="#">
        <p>
            ${season.name} 
            (평점 ${season.vote_average > 0.0 ? season.vote_average.toFixed(1) : '없음'})
            보러가기 - 
            ${season.air_date !== null ? season.air_date : '방영일자 조회되지 않음'}
        </p>
    </a>
`
         }
      })

      seasonRowHtml += `
       </div>
       </div>
       </div>
       `

      mainContainer.innerHTML += seasonRowHtml
   } catch (error) {
      console.log('에러내용:', error)
   }
}
