// Initialize and add the map
function initMap() {
            $.ajax({
                type: "GET",
                url: "/district",
                data: {},
                success: function (response) {
                    let rows = response['locations']
                    for (let i = 0; i < rows.length; i++) {
                        let name = rows[i]['name']
                        let X = rows[i]['X_WGS84']
                        let Y = rows[i]['Y_WGS84']




    const uluru = {lat: , lng:  };
    // The map, centered at Uluru
    const map = new google.maps.Map(document.getElementById("map"), {
        zoom: 4,
        center: uluru,
    });
    // The marker, positioned at Uluru
    const marker = new google.maps.Marker({
        position: uluru,
        map: map,
    });
}