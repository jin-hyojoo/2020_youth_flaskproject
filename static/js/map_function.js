
var cur_lat = 37.56580431969397, // 위도
    cur_lon = 126.9780719633559; // 경도


var mapContainer = document.getElementById('map'), // 지도를 표시할 div
    mapOption = {
        center: new kakao.maps.LatLng(cur_lat, cur_lon), // 지도의 중심좌표
        level: 4 // 지도의 확대 레벨
    };

var map = new kakao.maps.Map(mapContainer, mapOption); // 지도를 생성합니다

var mapdata;
$.getJSON("../static/전국_도서관표준데이터.json", function(data) {
    var html = [];
    var aJsonArray = new Array();

    $.each(data, function(i, item) {
        var jsondata = JSON.stringify(item);
        var parse_data = JSON.parse(jsondata); // parse 함수를 통한 객체화

        var aJson = new Object();

        aJson.lat = parse_data['latitude'];
        aJson.lng = parse_data['longitude'];
        aJsonArray.push(aJson);

        mapdata = aJsonArray;
    })

    if (navigator.geolocation) {

    // GeoLocation을 이용해서 접속 위치를 얻어옵니다
        navigator.geolocation.getCurrentPosition(function(position) {

            var cur_lat = position.coords.latitude, // 위도
                cur_lon = position.coords.longitude; // 경도
            $('#latitude').val(cur_lat);
            $('#longitude').val(cur_lon);
           // var cur_lat = 37.56580431969397,
           //     cur_lon = 126.9780719633559;

            var locPosition = new kakao.maps.LatLng(cur_lat, cur_lon); // 마커가 표시될 위치를 geolocation으로 얻어온 좌표로 생성합니다
                message = '<div style="padding:5px;">현위치</div>'; // 인포윈도우에 표시될 내용입니다

            var radius = 2500;

            var coordsArr = mapdata;
            var path = coordsArr.map(function(coords) {
                // 마커가 표시될 위치입니다
                var markerPosition  = new kakao.maps.LatLng(coords.lat, coords.lng);

//                console.log(markerPosition);
//                console.log(locPosition);

                // 마커를 생성합니다
                var marker = new kakao.maps.Marker({
                    position: markerPosition
                });

                var poly = new kakao.maps.Polyline({
                    path: [locPosition, markerPosition]
                });

                var dist = poly.getLength();

                if (dist < radius) {
                    //console.log(dist);
                    marker.setMap(map);
                } else {
                    marker.setMap(null);
                }

                // 마커가 지도 위에 표시되도록 설정합니다
//                marker.setMap(map);
            });
        // 마커와 인포윈도우를 표시합니다
        displayMarker(locPosition, message);

        });

    } else { // HTML5의 GeoLocation을 사용할 수 없을때 마커 표시 위치와 인포윈도우 내용을 설정합니다

        var locPosition = new kakao.maps.LatLng(cur_lat, cur_lon),
            message = 'geolocation을 사용할수 없어요..'

        displayMarker(locPosition, message);
    }

    // 지도에 마커와 인포윈도우를 표시하는 함수입니다
    function displayMarker(locPosition, message) {

        // 마커를 생성합니다
        var marker = new kakao.maps.Marker({
            map: map,
            position: locPosition
        });

        var iwContent = message, // 인포윈도우에 표시할 내용
            iwRemoveable = true;

        // 인포윈도우를 생성합니다
        var infowindow = new kakao.maps.InfoWindow({
            content : iwContent,
            removable : iwRemoveable
        });

        // 인포윈도우를 마커위에 표시합니다
        infowindow.open(map, marker);

        // 지도 중심좌표를 접속위치로 변경합니다
        map.setCenter(locPosition);
    }

})
