setInterval(fetchData, 500)

function fetchData() {
    fetch("/long_poll")
        .then((response) => {
            return response.json()
        })
        .then((response) => {
            
            console.log(response)
        })
}