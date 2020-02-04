
function show_collection() {
  document.getElementById('input-bar').style.display = 'none';
  document.getElementById('route').style.display = 'none';
  document.getElementById('collection').style.display = 'block';
  document.getElementById('search-icon').style.backgroundColor = 'none';
  document.getElementById('tourist_bar').style.display = 'none';
}

function show_search() {
  document.getElementById('input-bar').style.display = 'block';
  document.getElementById('tourist_bar').style.display = 'none';
  document.getElementById('route').style.display = 'none';
  document.getElementById('collection').style.display = 'none';
}


function show_route() {
  document.getElementById('route').style.display = 'block';
}
function myFunction()
{
  document.getElementById("loader").style.display = "block";
  myVar = setTimeout(showPage, 18000);
}
function showPage() {
  document.getElementById("loader").style.display = "none";

}

function show_tourist() {
  document.getElementById('input-bar').style.display = 'none';
  document.getElementById('route').style.display = 'none';
  document.getElementById('collection').style.display = 'none';
  document.getElementById('search-icon').style.backgroundColor = 'none';
  document.getElementById('tourist_bar').style.display = 'block';
}

$(function () {
  $('.tvs a').click(function () {
      $('.current').removeClass('current');
      $(this).addClass('current');
  });
});


$(function(){

  var isOpen = true;

  $("#menu").click(function(){
    if(isOpen) {
       $('#menu').css("background-color","#FFCC02");
       $('#searchbar').animate({left:'-=400px'})
    }else{
       $('#menu').css("background-color","#6b8e23");
       $('#searchbar').animate({left:'+=400px'}); 
    }

    isOpen = !isOpen;
  });
  });





get_weather();

function get_weather() {
  //call weather API from openweathermap
  $.getJSON('http://api.openweathermap.org/data/2.5/weather?q=Dublin,ie&units=metric&appid=5508cb29a72478e8bc8021bbe590ee4e', function (data) {
      var weather = data.weather[0].description;
      var temp = data.main.temp;
      var windSpeed = data.wind.speed;
      var icon = data.weather[0].icon;
      var iconUrl = ("<img id='weather-icon' src='../static/images/" + icon + ".png'>");

      $("#weather-icon").html(iconUrl);
      $("#currentTemp").html("Temperature: " + temp + " °C");
      $("#windSpeed").html("Wind Speed: " + windSpeed + " m/s");

  });
}



function myMap()
{
var myCenter = {lat: 53.349605, lng:-6.264175 };  
var mapCanvas = document.getElementById("map");
var mapOptions = {center: myCenter, zoom: 14};
var map = new google.maps.Map(mapCanvas, mapOptions);
infowindow = new google.maps.InfoWindow({  
    maxWidth: 355
    });
}
function change_map(list_intermediate_bus_stops,list_bus_lines,direction_data,departure_date_time) {
var directionsDisplay = new google.maps.DirectionsRenderer;
var directionsService = new google.maps.DirectionsService;
var myCenter = {lat: 53.349605, lng:-6.264175 };  
var mapCanvas = document.getElementById("map");
var mapOptions = {center: myCenter, zoom: 14};
var map = new google.maps.Map(mapCanvas, mapOptions);
infowindow = new google.maps.InfoWindow({  
        maxWidth: 355
        }); 

directionsDisplay.setMap(map);
//myFunction();
//document.getElementById("loader").style.display = "block";
var flag = 0;
var onChangeHandler = function() {
  flag=1;
  calculateAndDisplayRoute(directionsService, directionsDisplay,flag,list_bus_lines,direction_data,list_intermediate_bus_stops,map,departure_date_time);
};
document.getElementById('select').addEventListener('change', onChangeHandler);

calculateAndDisplayRoute(directionsService, directionsDisplay,flag,list_bus_lines,direction_data,list_intermediate_bus_stops,map,departure_date_time);
}
var arr = new Array(4);
function calculateAndDisplayRoute(directionsService, directionsDisplay,flag,list_bus_lines,direction_data,list_intermediate_bus_stops,map,departure_date_time) {
var data = document.getElementById('select').value;
var selectedMode = "TRANSIT";
document.getElementById('select').style.display = 'block';  //Can be later used with CSS to unhide the drop_down bus line which was hidden on page load
       
var source = document.getElementById("searchTextField").value;
var dest  = document.getElementById("searchTextField2").value;
var selected_date = document.getElementById("mydate").value;
var selected_time = document.getElementById("mytime").value;
var date,date_list,hr_mins,departure_time;
if(selected_date=='' && selected_time=='')
{
  var departure_time = departure_date_time;
          //var departure_time = Math.round(+new Date()/1000);
  console.log("if no depart time selected..current time");
  console.log(departure_time);
}
else
{
  var departure_time = departure_date_time;
  console.log("if departure date and time selected");
  console.log(departure_time);
          
}
console.log(departure_time);
var origin = document.getElementById("searchTextField").value;
var destination = document.getElementById("searchTextField2").value;
directionsService.route({
        origin: origin,  
        destination: destination, 
        provideRouteAlternatives: true,
        travelMode: google.maps.TravelMode[selectedMode],
        transitOptions: {
          departureTime: new Date(departure_time*1000),
          modes: ['BUS']
        }
      }, function(response, status) {
        if (status == 'OK') {
        console.log("Google response",response);
        console.log("Data is",data);
        var arr1 = new Array();
        for(var i=0;i<response['routes'].length;i++)
        {
          for(var j=0;j<response['routes'][i]['legs'][0]['steps'].length;j++)
          {
            if(response['routes'][i]['legs'][0]['steps'][j]['travel_mode']=="TRANSIT")
            {
              if(j>1)
              {
                var bus_transfer = response['routes'][i]['legs'][0]['steps'][1]['transit']['line']['short_name'].toUpperCase()+"/"+response['routes'][i]['legs'][0]['steps'][j]['transit']['line']['short_name'].toUpperCase();
                arr1.pop();
                arr1.push(bus_transfer);
              }
              else{
                arr1.push(response['routes'][i]['legs'][0]['steps'][j]['transit']['line']['short_name'].toUpperCase());
              }
            }
          }
        }
        console.log(arr1);
        var intersection_result = arr1.filter(function(n) {
          return list_bus_lines.indexOf(n) > -1;
        });
        console.log(intersection_result);
       
       console.log("Flag is",flag);
       console.log("Data after Flag is",data);
       if(flag==0)
       {
        document.getElementById("select").innerHTML="";
        for(var i = 0; i <arr1.length; i++)
        {
          var option = document.createElement("OPTION"),
          txt = document.createTextNode(arr1[i]);
          option.appendChild(txt);
          option.setAttribute("value",i);
          select.insertBefore(option,select.lastChild);
          
        }
        directionsDisplay.setDirections(response);
      }
      else
      {
        data = parseInt(data);
        directionsDisplay.setRouteIndex(data); 
                    
      }
      if(data=="" || flag==0)
      {
        data=0;
      }
      console.log("Before checking if backend result has the bus lines or not",data);
      console.log("The bus line from the drop down is",arr1[data]);
      if(list_bus_lines.includes(arr1[data]))
      {
        var data2  = list_bus_lines.indexOf(arr1[data]);
        console.log("Chosen index of data",data2);
        console.log(data2);
        
        display_direction_data(direction_data,data,data2,list_intermediate_bus_stops,map);
      }
      else
      {
        //Note: Create display_direction_data_new to display direction data from front end itself and not backend
        display_direction_data_front_end(response,data);
      }
    } else {
      window.alert('Directions request failed due to ' + status);
    }
  });
}
var flag2 = 0;
var global_list = new Array();
var markers = [];
function display_direction_data(direction_data,data,data2,list_intermediate_bus_stops,map,directionsDisplay)
{
var directionsDisplay = new google.maps.DirectionsRenderer;
directionsDisplay.setMap(map);
var whiteCircle = {
  path: google.maps.SymbolPath.CIRCLE,
  fillOpacity: 1.0,
  fillColor: "black",
  strokeOpacity: 1.0,
  strokeColor: "white",
  strokeWeight: 1.0,
  scale: 3.5
};
var list = list_intermediate_bus_stops[data2];
console.log("List is");
console.log(list);
document.getElementById("test").innerHTML=data;
console.log("direction data length is",direction_data.length);
console.log(direction_data);
/*
if(direction_data.length==data)
{
  data = direction_data.length-1;
}
*/
console.log("Data Now is",data);
if(direction_data[data2].length==18) //This is to diplay single bus journey. The length of it is still 18. For bus transfer,length has increased by 1
//Note: in line 262 it was direction_data[data] previously now it has been changed
{
  deleteMarkers();
  for(var i =1;i<list.length-1;i++)
  {
    var myLatlng = new google.maps.LatLng(list[i][2],list[i][3]);
    var marker = new google.maps.Marker({
            position: myLatlng,
            icon: whiteCircle,
            stop_no: list[i][0],
            stop_name: list[i][4]
          });
          // To add the marker to the map, call setMap();
          //marker.setMap(map);
    markers.push(marker);
  }
  console.log("Markers length");
  console.log(markers.length);
  function setMapOnAll(map) {
    for (var i = 0; i < markers.length; i++) {
      markers[i].setMap(map);
      popupDirections(markers[i]);
    }
  }
  function deleteMarkers() {
        
    console.log("Flag 2 is");
    console.log(flag2);
    console.log(markers);
    if(flag2!=0)
    {
      console.log(markers.length);
      setMapOnAll(null);
      markers=[];

    }
  }
  setMapOnAll(map);
  function popupDirections(marker) {
  //This function created listener listens for click on a marker to show information specific to that marker
  google.maps.event.addListener(marker, 'click', function () {
  infowindow.setContent('<b>'+"Stop No:"+'</b>'+marker.stop_no+'<br>'+'<b>'+"Stop Name:"+'</b>'+marker.stop_name);  infowindow.open(map, marker); //This opens the infowindow at the marker
});
}
document.getElementById("demo1").innerHTML = "";
document.getElementById("demo2").innerHTML = direction_data[data2][2];
document.getElementById("demo3").innerHTML = "Distance to departure bus stop: "+ direction_data[data2][3];
document.getElementById("demo4").innerHTML = "Time to walk to bus stop: "+direction_data[data2][4];
document.getElementById("demo5").innerHTML = " "; //direction_data[data2][6]->Distance in km to be covered in bus
document.getElementById("demo6").innerHTML = "Departure Bus Stop: "+direction_data[data2][8]
document.getElementById("demo7").innerHTML = "Predicted time of bus arrival at departure bus stop: "+direction_data[data2][9];
document.getElementById("demo8").innerHTML = "Headsign: "+direction_data[data2][10];
document.getElementById("demo9").innerHTML = "Bus Number: "+direction_data[data2][11];   //
document.getElementById("demo10").innerHTML = "Number of stops to travel: "+direction_data[data2][12];
if(direction_data[data2][12]<4)
{
  document.getElementById("demo11").innerHTML = " Estimated Fare: €"+ 1.55;
}
if(direction_data[data2][12]>3 && direction_data[data2][12]<14)
{
   document.getElementById("demo11").innerHTML = " Estimated Fare: €"+ 2.25;
}
 if(direction_data[data2][12]>13)
{
   document.getElementById("demo11").innerHTML = " Estimated Fare: €"+ 2.50;
}
document.getElementById("demo12").innerHTML = "Arrival Bus Stop: "+direction_data[data2][13];
document.getElementById("demo13").innerHTML = "Predicted time of bus arrival at arrival bus stop: "+direction_data[data2][16];
document.getElementById("demo14").innerHTML = "Time to walk to your destination: "+direction_data[data2][17];
document.getElementById("demo15").innerHTML = " ";
document.getElementById("demo16").innerHTML = " ";
document.getElementById("demo17").innerHTML = " ";
flag2 = 1;
}
else
{  
deleteMarkers();
for(var i =0;i<list.length;i++)
{
  for(var j = 1;j<list[i].length-1;j++)
  {
    var myLatlng = new google.maps.LatLng(list[i][j][2],list[i][j][3]);
    var marker = new google.maps.Marker({
            position: myLatlng,
            icon: whiteCircle,
            stop_no: list[i][j][0],
            stop_name: list[i][j][4]
          });
    // To add the marker to the map, call setMap();
    markers.push(marker);
    //marker.setMap(map);
    //popupDirections(marker);
  }
}
function setMapOnAll(map) {
  for (var i = 0; i < markers.length; i++) {
    markers[i].setMap(map);
    popupDirections(markers[i]);
  }
}
function deleteMarkers() {
  console.log("Flag 2 is");
  console.log(flag2);
  console.log(markers);
  if(flag2!=0)
  {
    console.log(markers.length);
    setMapOnAll(null);
    markers=[];

  }
}
setMapOnAll(map);
function popupDirections(marker) {
  //This function created listener listens for click on a marker to show information specific to that marker
  google.maps.event.addListener(marker, 'click', function () {
  infowindow.setContent('<b>'+"Stop No:"+'</b>'+marker.stop_no+'<br>'+'<b>'+"Stop Name:"+'</b>'+marker.stop_name);  infowindow.open(map, marker); //This opens the infowindow at the marker
});
}
document.getElementById("demo1").innerHTML = "Departure Bus Stop: "+direction_data[data2][0];
document.getElementById("demo2").innerHTML = "Predicted Arrival Time at departure bus stop: "+ direction_data[data2][1];
document.getElementById("demo3").innerHTML = "Headsign: "+direction_data[data2][2];
document.getElementById("demo4").innerHTML = "Bus Number: "+direction_data[data2][3];
document.getElementById("demo5").innerHTML = "No. of stops to travel: "+direction_data[data2][4];
if(direction_data[data2][4]<4)
{
  document.getElementById("demo6").innerHTML = " Estimated Fare: €"+ 1.55;
}
if(direction_data[data2][4]>3 && direction_data[data2][4]<14)
{
   document.getElementById("demo6").innerHTML = " Estimated Fare: €"+ 2.25;
}
 if(direction_data[data2][4]>13)
{
   document.getElementById("demo6").innerHTML = " Estimated Fare: €"+ 2.50;
}

document.getElementById("demo7").innerHTML = "Transit arrival bus stop: "+direction_data[data2][5];
document.getElementById("demo8").innerHTML = "Predicted Arrival Time at intermediate arrival stop : "+direction_data[data2][8];
document.getElementById("demo9").innerHTML = "Transfer:"+direction_data[data2][6];
document.getElementById("demo10").innerHTML = "Transit Departure bus stop: "+direction_data[data2][7];
document.getElementById("demo11").innerHTML = "Predicted Arrival Time at intermediate departure stop: "+direction_data[data2][14];
document.getElementById("demo12").innerHTML = "Headsign: "+direction_data[data2][9];
document.getElementById("demo13").innerHTML = "Bus Number: "+direction_data[data2][10];
document.getElementById("demo14").innerHTML = "No. of stops to travel: "+direction_data[data2][11];
if(direction_data[data2][11]<4)
{
  document.getElementById("demo15").innerHTML = " Estimated Fare: €"+ 1.55;
}
if(direction_data[data2][11]>3 && direction_data[data2][11]<14)
{
   document.getElementById("demo15").innerHTML = " Estimated Fare: €"+ 2.25;
}
 if(direction_data[data2][11]>13)
{
   document.getElementById("demo15").innerHTML = " Estimated Fare: €"+ 2.50;
}
document.getElementById("demo16").innerHTML = "Arrival bus stop: "+direction_data[data2][12];
document.getElementById("demo17").innerHTML = "Predicted Arrival time at final bus stop:" + direction_data[data2][13] ;
flag2 = 1;
}
}
function display_direction_data_front_end(response,data)
{
if(data!='default')
{
  deleteMarkers();
  function setMapOnAll(map) {
    for (var i = 0; i < markers.length; i++) {
      markers[i].setMap(map);
    }
  }
  function deleteMarkers() {
    console.log(markers);
    console.log(markers.length);
    setMapOnAll(null);
    markers=[];
  }
  console.log("data is",data);
  if(response['routes'][data]['legs'][0]['steps'].length==3)
  {
    console.log(data);
    console.log(response['routes'][data]['legs'][0]['steps'][1]['transit']['line']['short_name']);
    document.getElementById("demo1").innerHTML = response['routes'][data]['legs'][0]['steps'][0]['instructions'];
    document.getElementById("demo2").innerHTML = "Time to bus stop: "+ response['routes'][data]['legs'][0]['steps'][0]['duration']['text'];
    document.getElementById("demo3").innerHTML = "Departure Bus Stop: "+ response['routes'][data]['legs'][0]['steps'][1]['transit']['departure_stop']['name'];
    document.getElementById("demo4").innerHTML = "Arrival Time (from Google): " + response['routes'][data]['legs'][0]['steps'][1]['transit']['departure_time']['text'];
    document.getElementById("demo5").innerHTML = "Headsign: "+ response['routes'][data]['legs'][0]['steps'][1]['transit']['headsign'];
    document.getElementById("demo6").innerHTML = "Bus Number: "+ response['routes'][data]['legs'][0]['steps'][1]['transit']['line']['short_name'];
    document.getElementById("demo7").innerHTML = "No. of stops: " + response['routes'][data]['legs'][0]['steps'][1]['transit']['num_stops'];
    document.getElementById("demo8").innerHTML = "Arrival bus stop name: " + response['routes'][data]['legs'][0]['steps'][1]['transit']['arrival_stop']['name'];
    document.getElementById("demo9").innerHTML = "Arrival time (from Google):"+ response['routes'][data]['legs'][0]['steps'][1]['transit']['arrival_time']['text'];
    document.getElementById("demo10").innerHTML = "Walking time to the destination: " + response['routes'][data]['legs'][0]['steps'][2]['duration']['text'];
    document.getElementById("demo11").innerHTML =" ";
    document.getElementById("demo12").innerHTML =" ";
    document.getElementById("demo13").innerHTML =" ";
    document.getElementById("demo14").innerHTML  = " ";
    document.getElementById("demo15").innerHTML = " ";
    document.getElementById("demo16").innerHTML = " ";
    document.getElementById("demo17").innerHTML = " ";
  }
  else
  {
    if(response['routes'][data]['legs'][0]['steps'].length==4)
    {
      document.getElementById("demo1").innerHTML = "Departure Stop: "+response['routes'][data]['legs'][0]['steps'][1]['transit']['departure_stop']['name'];
      document.getElementById("demo2").innerHTML = "Arrival Time (from Google):: "+response['routes'][data]['legs'][0]['steps'][1]['transit']['departure_time']['text'];
      document.getElementById("demo3").innerHTML = "Headsign: "+response['routes'][data]['legs'][0]['steps'][1]['transit']['headsign'];
      document.getElementById("demo4").innerHTML = "Bus Number: "+response['routes'][data]['legs'][0]['steps'][1]['transit']['line']['short_name'];
      document.getElementById("demo5").innerHTML = "No. of stops: "+response['routes'][data]['legs'][0]['steps'][1]['transit']['num_stops'];
      document.getElementById("demo6").innerHTML = "Arrival Stop Transit: "+response['routes'][data]['legs'][0]['steps'][1]['transit']['arrival_stop']['name'];
      document.getElementById("demo7").innerHTML = "Transfer";
      if(response['routes'][data]['legs'][0]['steps'][2]["travel_mode"]=="TRANSIT")
      {
        document.getElementById("demo8").innerHTML = "Departure Stop: "+response['routes'][data]['legs'][0]['steps'][2]['transit']['departure_stop']['name'];
        document.getElementById("demo9").innerHTML = "Arrival Time (From Google): "+response['routes'][data]['legs'][0]['steps'][2]['transit']['departure_time']['text'];
        document.getElementById("demo10").innerHTML = "Headsign: "+response['routes'][data]['legs'][0]['steps'][2]['transit']['headsign'];
        document.getElementById("demo11").innerHTML = "Bus Number: "+response['routes'][data]['legs'][0]['steps'][2]['transit']['line']['short_name'];
        document.getElementById("demo12").innerHTML = "Number of Stops: "+response['routes'][data]['legs'][0]['steps'][2]['transit']['num_stops'];
        document.getElementById("demo13").innerHTML = "Final Arrival Stop: "+response['routes'][data]['legs'][0]['steps'][2]['transit']['arrival_stop']['name'];
        document.getElementById("demo14").innerHTML = "Arrival Time (From Google):"+response['routes'][data]['legs'][0]['steps'][2]['transit']['arrival_time']['text'];
        document.getElementById("demo15").innerHTML = " ";
        document.getElementById("demo16").innerHTML = " ";
        document.getElementById("demo17").innerHTML = " ";
      }
      else
      {
        document.getElementById("demo8").innerHTML = "Departure Stop: "+response['routes'][data]['legs'][0]['steps'][3]['transit']['departure_stop']['name'];
        document.getElementById("demo9").innerHTML = "Arrival Time (From Google): "+response['routes'][data]['legs'][0]['steps'][3]['transit']['departure_time']['text'];
        document.getElementById("demo10").innerHTML = "Headsign: "+response['routes'][data]['legs'][0]['steps'][3]['transit']['headsign'];
        document.getElementById("demo11").innerHTML = "Bus Number: "+response['routes'][data]['legs'][0]['steps'][3]['transit']['line']['short_name'];
        document.getElementById("demo12").innerHTML = "Number of Stops: "+response['routes'][data]['legs'][0]['steps'][3]['transit']['num_stops'];
        document.getElementById("demo13").innerHTML = "Final Arrival Stop: "+response['routes'][data]['legs'][0]['steps'][3]['transit']['arrival_stop']['name'];
        document.getElementById("demo14").innerHTML = "Arrival Time (From Google):"+response['routes'][data]['legs'][0]['steps'][3]['transit']['arrival_time']['text'];
        document.getElementById("demo15").innerHTML = " ";
        document.getElementById("demo16").innerHTML = " ";
        document.getElementById("demo17").innerHTML = " ";
      }
    }
    if(response['routes'][data]['legs'][0]['steps'].length==5)
    {
      document.getElementById("demo1").innerHTML = "Departure Stop: "+response['routes'][data]['legs'][0]['steps'][1]['transit']['departure_stop']['name'];
      document.getElementById("demo2").innerHTML = "Arrival Time (from Google):: "+response['routes'][data]['legs'][0]['steps'][1]['transit']['departure_time']['text'];
      document.getElementById("demo3").innerHTML = "Headsign: "+response['routes'][data]['legs'][0]['steps'][1]['transit']['headsign'];
      document.getElementById("demo4").innerHTML = "Bus Number: "+response['routes'][data]['legs'][0]['steps'][1]['transit']['line']['short_name'];
      document.getElementById("demo5").innerHTML = "No. of stops: "+response['routes'][data]['legs'][0]['steps'][1]['transit']['num_stops'];
      document.getElementById("demo6").innerHTML = "Arrival Stop Transit: "+response['routes'][data]['legs'][0]['steps'][1]['transit']['arrival_stop']['name'];
      document.getElementById("demo7").innerHTML = "Transfer";

      document.getElementById("demo8").innerHTML = "Departure Stop: "+response['routes'][data]['legs'][0]['steps'][3]['transit']['departure_stop']['name'];
      document.getElementById("demo9").innerHTML = "Arrival Time (From Google): "+response['routes'][data]['legs'][0]['steps'][3]['transit']['departure_time']['text'];
      document.getElementById("demo10").innerHTML = "Headsign: "+response['routes'][data]['legs'][0]['steps'][3]['transit']['headsign'];
      document.getElementById("demo11").innerHTML = "Bus Number: "+response['routes'][data]['legs'][0]['steps'][3]['transit']['line']['short_name'];
      document.getElementById("demo12").innerHTML = "Number of Stops: "+response['routes'][data]['legs'][0]['steps'][3]['transit']['num_stops'];
      document.getElementById("demo13").innerHTML = "Final Arrival Stop: "+response['routes'][data]['legs'][0]['steps'][3]['transit']['arrival_stop']['name'];
      document.getElementById("demo14").innerHTML = "Arrival Time (From Google):"+response['routes'][data]['legs'][0]['steps'][3]['transit']['arrival_time']['text'];
      //document.getElementById("demo14").innerHTML="";
      document.getElementById("demo15").innerHTML = " ";
      document.getElementById("demo16").innerHTML = " ";
      document.getElementById("demo17").innerHTML = " ";
    }
  }
}
}
function initialize() {
var options = {
  componentRestrictions: { country: 'ie' }
};
var input = document.getElementById('searchTextField');
var autocomplete = new google.maps.places.Autocomplete(input,options);
google.maps.event.addListener(autocomplete, 'place_changed', function () {
  var place = autocomplete.getPlace();
  var latitude1 = place.geometry.location.lat();
  var longitude1=place.geometry.location.lng();
  arr[0] = latitude1;
  arr[1] = longitude1;
});
}
function initialize2() {
var options = {
  componentRestrictions: { country: 'ie' }
};
var input = document.getElementById('searchTextField2');
var autocomplete = new google.maps.places.Autocomplete(input,options);
google.maps.event.addListener(autocomplete, 'place_changed', function () {
  var place = autocomplete.getPlace();
  var latitude2 = place.geometry.location.lat();
  var longitude2=place.geometry.location.lng();
  arr[2] = latitude2;
  arr[3] = longitude2;
});
}
function test_func()
{
var source = document.getElementById("searchTextField").value;
var dest  = document.getElementById("searchTextField2").value;
//console.log(typeOf(source));
if(source==null || source==""|| dest==null || dest=="")
{
  alert("Both source and destination is required");
}
else
{
  var selected_date = document.getElementById("mydate").value;
  var selected_time = document.getElementById("mytime").value;
  var depart_time,datetime_UTC,hr_mins,hr,mins,hr_mins,mins_ms;
  var origin = source;
  var destination = dest;
  var departure_date = selected_date;
  var departure_time = selected_time;
  $.ajax({
    type: "POST",
    url:  '/my-ajax-test/' ,
    data: { csrfmiddlewaretoken: '{{ csrf_token }}', origin: origin, destination:destination,departure_date: departure_date,departure_time: departure_time },
    success: function(response){
      console.log(response);
      //var myObj = JSON.parse("response".replace(/&quot;/g,"\""));
      if(response=="Error")
      {
        alert("Currently no nearby bus stops seems to be operating...kindly try again in some time")
      }
      else
      {
        var myObj =  JSON.parse(response);
        var direction_data = myObj.list_with_alternate_routes;
        var list_intermediate_bus_stops = myObj.list_intermediate_bus_stops_alternate_stops;
        var list_bus_lines =  myObj.list_bus_lines;
        var departure_date_time = parseInt(myObj.departure_date_time);
        console.log(direction_data);
        console.log(list_intermediate_bus_stops);
        console.log(list_bus_lines);
        change_map(list_intermediate_bus_stops,list_bus_lines,direction_data,departure_date_time);
      }
    }
  });
  return false;
}
}

var map, infoWindow;
function show_closest_bus_stops(closest_3_stops,closest_3_stops_bus_info,current_latitude,current_longitude) {
var myCenter = {lat: 53.349605, lng:-6.264175 };  
var mapCanvas = document.getElementById("map");
var mapOptions = {center: myCenter, zoom: 14};
var map = new google.maps.Map(mapCanvas, mapOptions);
infowindow = new google.maps.InfoWindow({  
                  maxWidth: 355
                  }); 
infoWindow = new google.maps.InfoWindow;
var pos = {
            lat: current_latitude,
            lng: current_longitude
          };

infoWindow.setPosition(pos);
infoWindow.setContent('My Location');
infoWindow.open(map);
map.setCenter(pos);
for(var i = 0;i<closest_3_stops.length;i++)
{
  x = closest_3_stops_bus_info[i].length;
  var z=" ";
  for(var j=0;j<x;j++)
  {
    z = z+closest_3_stops_bus_info[i][j][0]+" "+"("+closest_3_stops_bus_info[i][j][1]+")"+","+" ";
  }
  var myLatlng = new google.maps.LatLng(closest_3_stops[i][1],closest_3_stops[i][3]);
  var marker = new google.maps.Marker({
            position: myLatlng,
            stop_no: closest_3_stops[i][7],
            stop_name: closest_3_stops[i][5],
            bus_list_headsigns: z
          });
  marker.setMap(map);
  popupDirections(marker);
}
function popupDirections(marker) {
  //This function created listener listens for click on a marker to show information specific to that marker
  google.maps.event.addListener(marker, 'click', function () {
  infowindow.setContent('<b>'+"Stop No: "+'</b>'+marker.stop_no+'<br>'+'<b>'+"Stop Name: "+'</b>'+marker.stop_name+'<br>'+'<b>'+"Buses and Headsigns: "+'</b>'+marker.bus_list_headsigns);  infowindow.open(map, marker); //This opens the infowindow at the marker
});
}
}
function getLocation() {
if (navigator.geolocation) {
  navigator.geolocation.getCurrentPosition(showPosition);
}
else
{ 
  alert("Geolocation is not supported by this browser");
}
}
function showPosition(position) {
var current_latitude = parseFloat(position.coords.latitude);
var current_longitude = parseFloat(position.coords.longitude);
// The below ajax call is for finding nearest bus stops to a user's location
$.ajax({
  type: "POST",
  url: 'my-nearest-bus-stop/' ,
  data: { csrfmiddlewaretoken: '{{ csrf_token }}', current_latitude: current_latitude, current_longitude:current_longitude },
  success: function(response){
    console.log(response);
    if(response=="Error")
    {
      alert("No nearby bus stops found..try after some time/from different place");
    }
    else
    {
      var myObj =  JSON.parse(response);
      var closest_3_stops_bus_info = myObj.closest_3_stops_bus_info;
      var closest_3_stops = myObj.closest_3_stops;
      show_closest_bus_stops(closest_3_stops,closest_3_stops_bus_info,current_latitude,current_longitude);
    }
  }
});
}
var k=0;
var save_favourites = new Array();
// localStorage.removeItem("array"); //Refreshing/Clearing the web storage for evry ctrl+f5

function savetrip()
{
var source = document.getElementById("searchTextField").value;
var dest  = document.getElementById("searchTextField2").value;
        // Check browser support
if (typeof(Storage) !== "undefined") {
  // Store
  save_favourites.push(source);
  save_favourites.push('/');
  save_favourites.push(dest);
  save_favourites.push('/');
  //localStorage.setItem("source"+k, source);
  localStorage.setItem("array",save_favourites);
} else
 {
  alert("Sorry, Information cannot be saved at the moment") ;
}
}
function fetchsavedtrips()
{
// Retrieve
var list_fave_trips = localStorage.getItem("array");
list_fave_trips = list_fave_trips.slice(0,list_fave_trips.length-2);
list_fave_trips = list_fave_trips.split(",/,");
document.getElementById("myTable").innerHTML="";
var table = document.getElementById("myTable");//can be put inside the for-loop also
for(var i= 0;i<(list_fave_trips.length)-1;i=i+2)
{
  var row = table.insertRow(0);
  var cell1 = row.insertCell(0);
  var cell2 = row.insertCell(1);
  var cell3 = row.insertCell(2);
  var cell4 = row.insertCell(3);
  var first_letter = list_fave_trips[i].charAt(0);
  if(first_letter==',' )
  {
    list_fave_trips[i] = list_fave_trips[i].replace(",", "");

  }
  //From here till line 1239, its dealing with special characters in a address like ST. Patrick's Cathedral where apostrophe will be a delimieter so here we just add a \ to escape that if its present in a string
  insert = function insert(main_string, ins_string, pos) 
  {
    if(typeof(pos) == "undefined") {
      pos = 0;
    }
    if(typeof(ins_string) == "undefined") {
      ins_string = '';
    }
    return main_string.slice(0, pos) + ins_string + main_string.slice(pos);
  }
  var str1= list_fave_trips[i];
  var indices1 = [];
  for(var j=0; j<str1.length;j++) 
  {
    if (str1[j] === "'") indices1.push(j);
  }
  console.log(indices1);
  if(indices1.length!=0)
  {
   var count=0;
   for(var j=0;j<indices1.length;j++)
   {
    if(count==0)
    {
      str1 = insert(str1,'\\',indices1[j]);
      console.log("Escape character added",str1);
    }
    else
    {
      str1 = insert(str1,'\\',indices1[j]+count);
      console.log("Escape character added",str1);
    }
    count++;
  }
}
var str2 = list_fave_trips[i+1];
var indices2 = [];
for(var j=0; j<str2.length;j++) {
  if (str2[j] === "'") indices2.push(j);
}
console.log(indices2);
if(indices2.length!=0)
{
  var count=0;
  for(var j=0;j<indices2.length;j++)
  {
    if(count==0)
    {
      str2 = insert(str2,'\\',indices2[j]);
      console.log("Escape character added",str2);
    }
    else
    {
      str2 = insert(str2,'\\',indices2[j]+count);
      console.log("Escape character added",str2);

    }
    count++;
  }
}
cell1.innerHTML = list_fave_trips[i];
cell2.innerHTML = list_fave_trips[i+1];
cell3.innerHTML = '<input type="button" value="Use this trip" onClick="show_search();Selected(\''+str1+"/"+str2+'\')"/>' ;
cell4.innerHTML = '<input type="button" value="Delete" onClick="Delete(\''+str1+"/"+str2+'\')"/>' ;
}
}
function Selected(value)
{
var source_destination = value.split("/");
var source = source_destination[0];
var destination = source_destination[1];
document.getElementById("searchTextField").value = source;
document.getElementById("searchTextField2").value = destination;
}
function Delete(value)
{
console.log("Inside Delete");
var list_all_trips = localStorage.getItem("array");
var source_destination = value.split("/");
var source = source_destination[0];
var destination = source_destination[1];
var string = source+',/,'+destination+',/';
list_all_trips = list_all_trips.replace(string,"");
var position = save_favourites.indexOf(source);
if(save_favourites[position+2]==destination && position%2==0)
{
  save_favourites.splice(position,4);
}
else
{
  for(var i=position;i<save_favourites.length;i=i+4)
  {
    var new_position = save_favourites.indexOf(source,i);
    
    if(new_position%2==0 && save_favourites[new_position+2]==destination)
    {

      save_favourites.splice(new_position,4);
      break;

    }
    
  }
}
localStorage.setItem("array",save_favourites);
fetchsavedtrips();
}
function show_tourist_places_and_create_drop_down(list_tourist_places) {
//Will create a drop_down of all the tourist destinations in Dublin
document.getElementById("select2").style.display = "block";
document.getElementById("select2").innerHTML = "";  
document.getElementById("tourist_info").style.display = "block";
var select = document.getElementById("select2");
for(var i=0;i<list_tourist_places.length;i++)
{
  var option = document.createElement("OPTION");
  var txt = document.createTextNode(list_tourist_places[i][0]);
  option.appendChild(txt);
  option.setAttribute("value",list_tourist_places[i][4]);
  select.insertBefore(option,select.lastChild);
}
var myCenter = {lat: 53.349605, lng:-6.264175 };  
var mapCanvas = document.getElementById("map");
var mapOptions = {center: myCenter, zoom: 12};
var map = new google.maps.Map(mapCanvas, mapOptions);
infowindow = new google.maps.InfoWindow({  
    maxWidth: 355
    }); 
var image = 'https://developers.google.com/maps/documentation/javascript/examples/full/images/beachflag.png';       
for(var i=0;i<list_tourist_places.length;i++)
{     
  var myLatlng = new google.maps.LatLng(list_tourist_places[i][1],list_tourist_places[i][2]);
  var marker = new google.maps.Marker({
    position: myLatlng,
    icon: image,
    place_name: list_tourist_places[i][0],
    place_description: list_tourist_places[i][3]
  });
  // To add the marker to the map, call setMap();
  marker.setMap(map);
  popupDirections(marker);
}
function popupDirections(marker) {
  google.maps.event.addListener(marker, 'click', function () {
  infowindow.setContent('<b>'+"Place Name: "+'</b>'+marker.place_name+'<br>'+'<b>'+"Legend: "+'</b>'+marker.place_description);  infowindow.open(map, marker); //This opens the infowindow at the marker
});
}
}
function TouristMode()
{
var x = document.getElementById("tourist").checked;
console.log(x);
if(x==true)
{
  // The below ajax call is for finding all tourist places in Dublin
  $.ajax({
    type: "POST",
    url:  'my-tourist-places/' ,
    data: { csrfmiddlewaretoken: '{{ csrf_token }}' },
    success: function(response){
      console.log(response);
      if(response=="Error")
      {
        alert("Tourist Mode is having some issue...please try again in some time");
      }
      else
      {
        var myObj =  JSON.parse(response);
        var list_tourist_places = myObj.list_tourist_places;
        show_tourist_places_and_create_drop_down(list_tourist_places);
      }
    }
  });
}
else
{
  //clear the output
  document.getElementById("tourist_info").style.display = "none";
  document.getElementById("select2").style.display = "none";
  myMap();
}
}
//This function is to assign user's current location as the source in case tourist mode is on and the user selects any tourist places option from dropdown which is the destination. It is called from getSelectedValue()
function showPosition2(position) {
var current_latitude = parseFloat(position.coords.latitude);
var current_longitude = parseFloat(position.coords.longitude);
var google_map_pos = new google.maps.LatLng( current_latitude, current_longitude );

/* Use Geocoder to get address */
var google_maps_geocoder = new google.maps.Geocoder();
google_maps_geocoder.geocode(
  { 'latLng': google_map_pos },
  function( results, status ) {
    if ( status == google.maps.GeocoderStatus.OK && results[0] ) {
      console.log( results[0].formatted_address );
      alert("Default: Your Current Location is used as the origin...You can change it manually in the source bar");
      document.getElementById("searchTextField").value = results[0].formatted_address;
    }
  }
  );
}
//This function is to get the value to see which tourist place has been chsoen by the user from drop-down menu
function getSelectedValue()
{
var selected_tourist_place = document.getElementById("select2").value;
console.log("selected tourist place is",selected_tourist_place);
document.getElementById("searchTextField2").value = selected_tourist_place;
if (navigator.geolocation) {
  navigator.geolocation.getCurrentPosition(showPosition2);
} else { 
  alert("Geolocation is not supported by this browser");
}
}

//Commenting it to prevent api calls to open weather, later uncomment it

/*
function myTimer()
{
$.ajax({
  type: "POST",
  url: '{{ 'my-weather-data/' }}',
  data: { csrfmiddlewaretoken: '{{ csrf_token }}', data:0 },
  success: function(response){
    console.log(response);
  }
});
}
*/

google.maps.event.addDomListener(window, 'load', initialize);