function searchPlaces() {
    var query = document.getElementById('searchInput').value;

    fetch('/search_places?query=' + query)
        .then(response => response.json())
        .then(data => {
            // Получаем список мест и API_KEY из ответа
            var places = data.places;
            var API_KEY = data.API_KEY;

            // Обновляем карту и добавляем маркеры для найденных мест
            updateMap(places, API_KEY);
        })
        .catch(error => console.error('Ошибка:', error));
}

function updateMap(places, API_KEY) {
    var firstPlace = places[0];

    // Обновляем ссылку на карту с новыми координатами и API_KEY
    var mapUrl = 'https://static-maps.yandex.ru/v1?pt=' + firstPlace.longitude + ',' + firstPlace.latitude + ',pm2rdm&lang=ru_RU&size=450,450&z=13&&apikey=' + API_KEY;
    document.getElementById('map').innerHTML = '<img src="' + mapUrl + '" alt="' + firstPlace.name + '">';

    // Добавляем варианты найденных мест в список для выбора
    var datalist = document.getElementById('placesList');
    datalist.innerHTML = '';
    places.forEach(place => {
        var option = document.createElement('option');
        option.value = place.name;
        datalist.appendChild(option);
    });
}


document.getElementById('searchInput').addEventListener('input', searchPlaces);
