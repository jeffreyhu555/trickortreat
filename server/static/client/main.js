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
function initMap() {
  geocoder = new google.maps.Geocoder();
  infowindow = new google.maps.InfoWindow()
  navigator.geolocation.getCurrentPosition(setupMap)
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
        $("#address").val(results[0].formatted_address);
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
    success:function(d){console.log(d);if(d.success==false){alert("FAIL:"+d.error);}}
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