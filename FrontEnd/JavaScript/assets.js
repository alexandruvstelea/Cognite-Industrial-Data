function loadAssets() {
    fetch('http://127.0.0.1:5000/assets')
        .then(function (response) {
            return response.json()
        })
        .then(function (complete_response) {
            let data = ''
            complete_response.map((values) => {
                console.log(values)
                data += `
                <div class="card">
                    <img src="/FrontEnd/Images/asset.svg" alt="Avatar" style="width:100%">
                    <b>${values.name}</b>
                    <p><a href=/FrontEnd/HTML/data.html?${values.id}&${values.name}>${values.id}</a></p>
                    <p>Tracking data: ${values.used}</p>
                </div>
                `
                document.getElementById('cards').innerHTML = data
            })
        })
        .catch((err) => {
            console.log(err)
        })
}
async function getGraphData() {
    console.log("GATHERING CHART DATA")
    let id = queryString.split("&");
    let calendar_range = document.getElementById('date_range').value
    let interpolation_rate = document.getElementById('slider').value
    const url = 'http://127.0.0.1:5000/datapoints?' + new URLSearchParams({
        id: id[0],
        choice: "all",
        range: calendar_range,
        int_rate: interpolation_rate,
        outliers: 'YES'
    })
    const response = await fetch(url)
        .then(function (response) {
            return response.json()
        })
        .then(function (complete_response) {
            let data = []
            for (i in complete_response.value) {
                let value_date = []
                value_date.push(complete_response.value[i][0].substring(5, 16))
                value_date.push(complete_response.value[i][1])
                value_date.push(complete_response.value[i][2])
                data.push(value_date)
            }
            updateChart(data)
        })
}

function updateInterpolation(val) {
    document.getElementById('points').value = val + ' points';
    getGraphData()
}

function initInterpolation() {
    document.getElementById('points').value = '600 points';
}

function getData() {
    let queryString = decodeURIComponent(window.location.search);
    queryString = queryString.substring(1);
    let id = queryString.split("&");
    let calendar_range = document.getElementById('date_range').value
    let interpolation_rate = document.getElementById('slider').value
    let radio_choice = document.querySelector('input[name="choice"]:checked').value
    fetch('http://127.0.0.1:5000/datapoints?' + new URLSearchParams({
        id: id[0],
        choice: radio_choice,
        range: calendar_range,
        int_rate: interpolation_rate,
        outliers: 'NO'
    }))
        .then(
            function (response) {
                return response.json()
            }
        )
        .then(
            function (complete_response) {
                console.log(complete_response)
                document.getElementById('value').innerHTML = complete_response.value
            }
        )
        .catch((err) => {
            console.log(err)
        })
}