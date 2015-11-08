function scrollToPage1(){
	$('html, body').animate({
	    scrollTop: $("#page1").offset().top
	}, 1000);
}

function scrollToPage2(){
	$('html, body').animate({
	    scrollTop: $("#page2").offset().top
	}, 1000);
}

function scrollToPage3(){
	$('html, body').animate({
	    scrollTop: $("#page3").offset().top
	}, 1000);
}

var map;
var geocoder;
var marker;
var infowindow;
var address;
var imageselected = false;
var pinImage;
var pinColor;
var pinShadow
function initMap() {
  geocoder = new google.maps.Geocoder();
  infowindow = new google.maps.InfoWindow()
  navigator.geolocation.getCurrentPosition(setupMap)
  pinColor = "009000";
pinImage = new google.maps.MarkerImage("http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|" + pinColor,
new google.maps.Size(21, 34),
new google.maps.Point(0,0),
new google.maps.Point(10, 34));
pinShadow = new google.maps.MarkerImage("http://chart.apis.google.com/chart?chst=d_map_pin_shadow",
new google.maps.Size(40, 37),
new google.maps.Point(0, 0),
new google.maps.Point(12, 35));
}

function setupMap(coords){
   map = new google.maps.Map(document.getElementById('map'), {
    center: {lat: coords.coords.latitude, lng: coords.coords.longitude},
    zoom: 20
  });
   map.addListener('click', geocode);

}

function geocode(e){
  var latlng=e.latLng
  geocoder.geocode({'location': latlng}, function(results, status) {
    if (status === google.maps.GeocoderStatus.OK) {
      if (results[1]) {
        infowindow.setContent(results[0].formatted_address);
        if(marker!=undefined){marker.setMap(null);}
        marker = new google.maps.Marker({
          position: latlng,
          map: map
        });
        infowindow.open(map, marker);
        $("#lat").val(latlng.lat);
        $("#lon").val(latlng.lng);
        $("#userlat").val(latlng.lat);
        $("#userlon").val(latlng.lng);
        $("#address").val(results[0].formatted_address);
        address=results[0].formatted_address;
      } else {
        window.alert('No results found');
      }
    } else {
      window.alert('Geocoder failed due to: ' + status);
    }
  });
}

function initBindings(){
	$("#upload-button").click(function(){$("#hidden-upload-field").click();});
	$("#hidden-upload-field").change(scrollToPage3);
  $('#rating').raty({number:10});
  $('#candy').raty({number:10});
}

function submitData(){
  var candies=[];
  if($("#hersheys")[0].checked){
    candies.push("Hersheys");
  }
  if($("#fshersheys")[0].checked){
    candies.push("Full size Hersheys");
  }
  if($("#twizzlers")[0].checked){
    candies.push("Twizzlers");
  }
  if($("#rpeices")[0].checked){
    candies.push("Reeses Peices");
  }
  if($("#snickers")[0].checked){
    candies.push("Snickers");
  }
  if($("#3musketeers")[0].checked){
    candies.push("3 Musketeers");
  }
  if($("#nerds")[0].checked){
    candies.push("Nerds");
  }
  if($("#gum")[0].checked){
    candies.push("Gum");
  }
  console.log(candies);
  var data = {
    note:$("#note").val(),
    rating:$("#rating").raty('score'),
    candy:$("#candy").raty('score'),
    address:$("#address").val(),
    lat:$("#lat").val(),
    lon:$("#lon").val(),
    placeid:$("#address").val(),
    candies:candies
  };

  $.ajax({
    url: "/submit",
    type: "POST",
    dataType:"json",
    data: JSON.stringify(data),
    contentType: "application/json; charset=utf-8",
    success:function(d){console.log(d);if(d.success==false){alert("FAIL:"+d.error);}else{if($("#hidden-upload-field")[0].files.length>0){uploadImage();}}}
  });

	scrollToPage1();
  $("#note").val("");
  $("#address").val("");
  $("#lat").val("");
  $("#lon").val("");
  $("#hersheys").prop('checked', false);
  $("#fshersheys").prop('checked', false);
  $("#twizzlers").prop('checked', false);
  $("#rpeices").prop('checked', false);
  $("#snickers").prop('checked', false);
  $("#3musketeers").prop('checked', false);
  $("#nerds").prop('checked', false);
  $("#gum").prop('checked', false);
  $('#rating').raty({number:10});
  $('#candy').raty({number:10});
}

function uploadImage(){
  var formData = new FormData();
  var file = $("#hidden-upload-field")[0].files[0];
  formData.append('image', file, file.name);
  var xhr = new XMLHttpRequest();
  xhr.open('POST', '/upload?'+address, true);
  xhr.onload = function () {
    if (xhr.status === 200) {
      // File(s) uploaded.
      
      console.log("XHR finished");
      console.log(this.responseText);
    } else {
      alert('An error occurred!');
    }
  };
  xhr.send(formData);
  console.log("XHR sent");
  $("#hidden-upload-field")[0].files=[];
}

function search(){
  $.ajax({
    url: "/request",
    type: "POST",
    dataType:"json",
    data: JSON.stringify({
      lat:$("#userlat").val(),
      lon:$("#userlon").val(),
      dist:$("#maxdist").val(),
      rating:$("#minrating").val(),
      candy:$("#mincandy").val(),
      required:$("#required").val().split(","),
      disallowed:$("#disallowed").val().split(",")
    }),
    contentType: "application/json; charset=utf-8",
    success:function(d){console.log(d);if(d.success==false){alert("FAIL:"+d.error);}else{processRequestResults(d);}}
  });
}

var markers=[];

function killAllMarkers(){
  for (i=0; i<markers.length;i++){
    markers[i].setMap(null);
  }
}

function generateContent(house){
  var r= house.address+"<br/><div class=\"lightbox-launcher-container\">";;
  for (i=0; i<house.photos.length;i++){
    r+="<img src=\"/static/uploads/"+house.photos[i]+"\"/>";
  }
  r+="</div><br/>Notes:<br/>";
  for (i=0; i<house.notes.length;i++){
    r+="<code>"+house.notes[i]+"</code><br/>";
  }
  if(house.rating>0){r+="<b>Avg Rating:"+house.calc_rating+"</b>";}
  else{r+="<b>(Noone has rated this house)</b>";}
  r+="<br/>";
  if(house.avgcandy>0){r+="<b>Candy Rating:"+house.calc_avgcandy+"</b>";}
  else{r+="<b>(Noone has rated this house's candy output)</b>";}
  r+="<br/><i>"+house.visits+" visits</i>";
  return r;
}

function processRequestResults(d){
  killAllMarkers();
  for (j=0; j<d.houses.length;j++){
    var ayy=d.houses[j];
    var m = new google.maps.Marker({
      position: {lat:ayy.lat, lng:ayy.lon},
      map: map,
      icon: pinImage,
      shadow:pinShadow
    });
    markers.push(m);
    attachListner(m, generateContent(ayy));
  }
  var bounds = new google.maps.LatLngBounds();
  for(i=0;i<markers.length;i++) {
   bounds.extend(markers[i].getPosition());
  }
  infowindow.close();

  map.fitBounds(bounds);
  scrollToPage1();
  marker.setMap(null);
}

function attachListner(marker, msg){
  console.log("ivkd");
  var l_infowindow = new google.maps.InfoWindow({
    content: msg
  });
  console.log("ctd");
   marker.addListener('click', function(){l_infowindow.open(map, marker);});
}