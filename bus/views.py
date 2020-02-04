from django.shortcuts import render
from django.http import HttpResponse
import pymysql,json
from operator import itemgetter
from . import machine_learning_tester  
from .machine_learning_tester import ml_model
from datetime import datetime
from calendar import timegm
import joblib
import _pickle as cPickle
import os
from django.views.decorators.csrf import csrf_exempt
CURRENT_DIR = os.path.dirname(__file__)

#When the application is launched, render the index.html page before any other operation
def home(request):
	return render(request,'bus/index.html')


def find_correct_stop(bus_number,headsign,closest_15_stops):
	'''
	The function is called from extract_correct_depart_arrival_stop_id() to find the actual bus stop that a bus line passes through
	from the array of 15 bus stops that was fetched by the calling function. For every bus line this function is called twice, once to
	get the correct departure bus stop id (among the 15 bus stops) and once to get the correct arrival bus stop id  
	'''
	for data in closest_15_stops:
		print("Data is",data)
		stop_id_check = data[2]
		print("Stop id is",stop_id_check)
		sql_3 = """ select distinct mydbservlet.stops_times.bus_number  from mydbservlet.stops_times 
            where mydbservlet.stops_times.bus_number=%s
            and mydbservlet.stops_times.bus_stop_number=%s and mydbservlet.stops_times.headsign=%s """
		db = pymysql.connect(host="127.0.0.1", user="root", passwd="Ganesha-46", db="mydbservlet")
		cursor = db.cursor()
		cursor.execute(sql_3,(bus_number,stop_id_check,headsign))
		query_result = cursor.fetchall()
		print("Query_result is",query_result)
		print(len(query_result))
		if(len(query_result)==1):
			break
	return list(data)


def extract_correct_depart_arrival_stop_id(departure_stop,arrival_stop,bus_number,headsign,lat1,long1,lat2,long2,result):
	'''
	The function is called from findroutedetails() to find correct stop id of the source and destination bus stop of a particular bus line
	and headsign. Google Maps API in many cases returns bus stop names that do not match with the bus stop name in the database. So correct stop
	id cannot be generated from the bus stop name. Using latitude and longitude of a bus stop (provided from Google route), we find the nearest
	15 stops (using bus stop coordinates in our database ) closest to that suggested stop.   
	'''
	try:
		#For departure bus stop
		from geopy import distance
		import numpy as np
		departure_bus_stop_location = (lat2,long2)
		distances_dept = []
		for i in result:
			stop_location = (i[0],i[1])
			dist = distance.distance(departure_bus_stop_location, stop_location).km
			distances_dept.append(dist)

    	#For departure bus stop
		closest_15_indexes = np.argsort(distances_dept)[:15] #Change 15 to any number as much as we want for nearest bus numbers
		closest_15_stops_dept = []
		for i in closest_15_indexes:
			closest_15_stops_dept.append(result[i])
		print("closest stops to your location is: ",closest_15_stops_dept)

		#For arrival bus stop
		arrival_bus_stop_location = (lat1,long1)
		distances_arrival = []
		for i in result:
			stop_location = (i[0],i[1])
			dist = distance.distance(arrival_bus_stop_location, stop_location).km
			distances_arrival.append(dist)
    	#For arrival bus stop
		closest_15_indexes = np.argsort(distances_arrival)[:15] #Change 15 to any number as much as we want for nearest bus numbers
		closest_15_stops_arrival = []
		for i in closest_15_indexes:
			closest_15_stops_arrival.append(result[i])
		print("closest stops to your location is: ",closest_15_stops_arrival)
		
		actual_departure_stop_info = find_correct_stop(bus_number,headsign,closest_15_stops_dept)
		actual_arrival_stop_info = find_correct_stop(bus_number,headsign,closest_15_stops_arrival)
		arrival_stop_id = actual_arrival_stop_info[2]
		departure_stop_id = actual_departure_stop_info[2]

				

		print("arrival_stop_id",arrival_stop_id)
		print("departure_stop_id",departure_stop_id)
		list_arrive_depart_stop_id = []
		list_arrive_depart_stop_id.append(arrival_stop_id)
		list_arrive_depart_stop_id.append(departure_stop_id)

		return list_arrive_depart_stop_id
	
	except:
		return 0



def extract_seq_numbers_bus_stops(headsign,bus_number,arrival_stop_id,departure_stop_id,number_of_stops,bus_at_departure_stop,bus_at_arrival_stop,departure_date):
	'''
	The function is called from findroutedetails() to find the sequence number of the departure and arrival bus stop for a particular bus line
	and also using the sequence number to find the intermediate bus stops between source and destination which is used to display as markers on the map
	'''

			
	sql_2 = """select mydbservlet.stops_times.bus_stop_number,mydbservlet.stops_times.stop_sequence,mydbservlet.trips_info_bus_number.direction_id,mydbservlet.stops_times.headsign,mydbservlet.stops_times.bus_number,
		mydbservlet.stops_times.trip_id from mydbservlet.stops_times,
		mydbservlet.trips_info_bus_number where stops_times.trip_id = trips_info_bus_number.trip_id and stops_times.headsign=%s
		and stops_times.bus_number = %s and (bus_stop_number=%s or bus_stop_number=%s) """
	db = pymysql.connect(host="127.0.0.1", user="root", passwd="Ganesha-46", db="mydbservlet")
	cursor = db.cursor()
	cursor.execute(sql_2,(headsign,bus_number,arrival_stop_id,departure_stop_id,))
	seq_numbers = cursor.fetchall()
	print(seq_numbers)
	seq_numbers = list(seq_numbers)
	print("length of sequence numbers is",len(seq_numbers))
	if(len(seq_numbers)>2): #It is possible for a bus line having same headsign returning different tuple of sequence numbers (Eg:-(40,60),(48,68)). This is because of different trips that a bus line can cover where the sequence number of the same bus stop changes. 
		i = 0
		while(i<len(seq_numbers)-1): # To find the correct combination of sequence numbers for departure and arrrival bus stop id 
			if( seq_numbers[i+1][1]-seq_numbers[i][1]==number_of_stops):
				departure_bus_seq = seq_numbers[i][1]
				arrival_bus_seq = seq_numbers[i+1][1]
				headsign_seq = seq_numbers[i][3]
				direction_id = seq_numbers[i][2]
				trip_id = seq_numbers[i][5]
				print("departure_bus_seq",departure_bus_seq)
				print("arrival_bus_seq",arrival_bus_seq)
				print("headsign",headsign_seq)
				print("trip id", trip_id)
				break
			else:
				departure_bus_seq = seq_numbers[0][1]
				arrival_bus_seq = seq_numbers[1][1]
				headsign_seq = seq_numbers[0][3]
				direction_id = seq_numbers[0][2]
				trip_id = seq_numbers[0][5]
				print("inside while-else")
				print("departure_bus_seq",departure_bus_seq)
				print("arrival_bus_seq",arrival_bus_seq)
				print("headsign",headsign_seq)
				print("trip id", trip_id)
				i+=1


	else:
		departure_bus_seq = seq_numbers[0][1]
		arrival_bus_seq = seq_numbers[1][1]
		headsign_seq = seq_numbers[0][3]
		direction_id = seq_numbers[0][2]
		trip_id = seq_numbers[0][5]
		print("departure_bus_seq",departure_bus_seq)
		print("arrival_bus_seq",arrival_bus_seq)
		print("headsign",headsign_seq)
		print("trip id", trip_id)

	if(departure_bus_seq>arrival_bus_seq):
		exchange = departure_bus_seq
		departure_bus_seq = arrival_bus_seq
		arrival_bus_seq = exchange

	sql_intermed_bus_stops = """select distinct mydbservlet.stops_times.bus_stop_number,mydbservlet.stops_times.stop_sequence,
						mydbservlet.stops_2ttest_bus_stops.﻿stop_lat,
						mydbservlet.stops_2ttest_bus_stops.stop_lon,mydbservlet.stops_2ttest_bus_stops.stop_name,mydbservlet.stops_times.bus_number from mydbservlet.stops_2ttest_bus_stops,
						mydbservlet.stops_times,mydbservlet.trips_info_bus_number where mydbservlet.stops_2ttest_bus_stops.stop_id = mydbservlet.stops_times.bus_stop_number and stops_times.trip_id = trips_info_bus_number.trip_id and  stops_times.bus_number=%s 
						and stops_times.headsign = %s and stops_times.stop_sequence between %s and %s and trips_info_bus_number.direction_id=%s and mydbservlet.stops_times.trip_id=%s  order by mydbservlet.stops_times.stop_sequence"""

	cursor = db.cursor()
	cursor.execute(sql_intermed_bus_stops,(bus_number,headsign_seq,int(departure_bus_seq),int(arrival_bus_seq),int(direction_id),trip_id,))
	intermediate_bus_stops = cursor.fetchall()

	print("intermediate bus stops",intermediate_bus_stops)
	seen = set()  # To handle duplicates in case if the same bus stop id has been returned more than once with a different sequence number
	seen_add = seen.add
	remove_duplicates = [x for x in intermediate_bus_stops if not (x[0] in seen or seen_add(x[0]))]

	print("Length of intermediate_bus_stops",len(intermediate_bus_stops))
	remove_duplicates = [x for x in remove_duplicates if not (x[1] in seen or seen_add(x[1]))] #Contains the fileterd bus stop id's with their sequence number after removing duplicates if any that were present
	print("Length of intermediate_bus_stops remove duplicates",len(remove_duplicates))
	
	print("List of sequence bus stops after removing duplicates",remove_duplicates)

	return(remove_duplicates)


def get_transit_details(transit_route):
	'''
	To store the information specific to a trip involving one/multiple bus transfers suggested by Google Directions API in a list. 
	The function is called from the Else block of findroutedetails() function indicating the journey may involve bus transfers. 

	'''
	if(len(transit_route['legs'][0]['steps'])==4):

		departure_stop = transit_route['legs'][0]['steps'][1]['transit_details']['departure_stop']['name']
		bus_at_departure_stop = transit_route['legs'][0]['steps'][1]['transit_details']['departure_time']['text']
		headsign_first = transit_route['legs'][0]['steps'][1]['transit_details']['headsign']
		bus_number_first = transit_route['legs'][0]['steps'][1]['transit_details']['line']['short_name']
		number_of_stops_first = transit_route['legs'][0]['steps'][1]['transit_details']['num_stops']
		arrival_stop_transit = transit_route['legs'][0]['steps'][1]['transit_details']['arrival_stop']['name']
		bus_at_intermediate_transfer_stop = transit_route['legs'][0]['steps'][1]['transit_details']['arrival_time']['text'] #Added 17-07 appended end of the list_with_direction
		
		lat1 = transit_route['legs'][0]['steps'][1]['transit_details']['arrival_stop']['location']['lat']
		long1 = transit_route['legs'][0]['steps'][1]['transit_details']['arrival_stop']['location']['lng']
		lat2 = transit_route['legs'][0]['steps'][1]['transit_details']['departure_stop']['location']['lat']
		long2 = transit_route['legs'][0]['steps'][1]['transit_details']['departure_stop']['location']['lng']
		transit = "Transfer"
		if(transit_route['legs'][0]['steps'][2]["travel_mode"]=="TRANSIT"):
			departure_stop_transit = transit_route['legs'][0]['steps'][2]['transit_details']['departure_stop']['name']
			bus_at_transit_departure_stop = transit_route['legs'][0]['steps'][2]['transit_details']['departure_time']['text']
			headsign_second = transit_route['legs'][0]['steps'][2]['transit_details']['headsign']
			bus_number_second = transit_route['legs'][0]['steps'][2]['transit_details']['line']['short_name']
			number_of_stops_second = transit_route['legs'][0]['steps'][2]['transit_details']['num_stops']
			arrival_stop_final = transit_route['legs'][0]['steps'][2]['transit_details']['arrival_stop']['name']
			bus_at_final_destination_stop = transit_route['legs'][0]['steps'][2]['transit_details']['arrival_time']['text']
			lat3 = transit_route['legs'][0]['steps'][2]['transit_details']['arrival_stop']['location']['lat']
			long3 = transit_route['legs'][0]['steps'][2]['transit_details']['arrival_stop']['location']['lng']
			lat4 = transit_route['legs'][0]['steps'][2]['transit_details']['departure_stop']['location']['lat']
			long4 = transit_route['legs'][0]['steps'][2]['transit_details']['departure_stop']['location']['lng']

			list_with_direction = [departure_stop,bus_at_departure_stop,headsign_first,bus_number_first,number_of_stops_first,arrival_stop_transit,transit,departure_stop_transit,bus_at_transit_departure_stop,headsign_second,bus_number_second,number_of_stops_second,arrival_stop_final,bus_at_final_destination_stop,bus_at_intermediate_transfer_stop,lat1,long1,lat2,long2,lat3,long3,lat4,long4]
		else:
			departure_stop_transit = transit_route['legs'][0]['steps'][3]['transit_details']['departure_stop']['name']
			bus_at_transit_departure_stop = transit_route['legs'][0]['steps'][3]['transit_details']['departure_time']['text']
			headsign_second = transit_route['legs'][0]['steps'][3]['transit_details']['headsign']
			bus_number_second = transit_route['legs'][0]['steps'][3]['transit_details']['line']['short_name']
			number_of_stops_second = transit_route['legs'][0]['steps'][3]['transit_details']['num_stops']
			arrival_stop_final = transit_route['legs'][0]['steps'][3]['transit_details']['arrival_stop']['name']
			bus_at_final_destination_stop = transit_route['legs'][0]['steps'][3]['transit_details']['arrival_time']['text'];
			lat3 = transit_route['legs'][0]['steps'][3]['transit_details']['arrival_stop']['location']['lat']
			long3 = transit_route['legs'][0]['steps'][3]['transit_details']['arrival_stop']['location']['lng']
			lat4 = transit_route['legs'][0]['steps'][3]['transit_details']['departure_stop']['location']['lat']
			long4 = transit_route['legs'][0]['steps'][3]['transit_details']['departure_stop']['location']['lng']
			list_with_direction = [departure_stop,bus_at_departure_stop,headsign_first,bus_number_first,number_of_stops_first,arrival_stop_transit,transit,departure_stop_transit,bus_at_transit_departure_stop,headsign_second,bus_number_second,number_of_stops_second,arrival_stop_final,bus_at_final_destination_stop,bus_at_intermediate_transfer_stop,lat1,long1,lat2,long2,lat3,long3,lat4,long4]

		

	if(len(transit_route['legs'][0]['steps'])==5):

		departure_stop = transit_route['legs'][0]['steps'][1]['transit_details']['departure_stop']['name']
		bus_at_departure_stop = transit_route['legs'][0]['steps'][1]['transit_details']['departure_time']['text']
		headsign_first = transit_route['legs'][0]['steps'][1]['transit_details']['headsign']
		bus_number_first = transit_route['legs'][0]['steps'][1]['transit_details']['line']['short_name']
		number_of_stops_first = transit_route['legs'][0]['steps'][1]['transit_details']['num_stops']
		arrival_stop_transit = transit_route['legs'][0]['steps'][1]['transit_details']['arrival_stop']['name']
		bus_at_intermediate_transfer_stop = transit_route['legs'][0]['steps'][1]['transit_details']['arrival_time']['text']

		lat1 = transit_route['legs'][0]['steps'][1]['transit_details']['arrival_stop']['location']['lat']
		long1 = transit_route['legs'][0]['steps'][1]['transit_details']['arrival_stop']['location']['lng']
		lat2 = transit_route['legs'][0]['steps'][1]['transit_details']['departure_stop']['location']['lat']
		long2 = transit_route['legs'][0]['steps'][1]['transit_details']['departure_stop']['location']['lng']

		transit = "Transfer"
		departure_stop_transit = transit_route['legs'][0]['steps'][3]['transit_details']['departure_stop']['name']
		bus_at_transit_departure_stop = transit_route['legs'][0]['steps'][3]['transit_details']['departure_time']['text']
		headsign_second = transit_route['legs'][0]['steps'][3]['transit_details']['headsign']
		bus_number_second = transit_route['legs'][0]['steps'][3]['transit_details']['line']['short_name']
		number_of_stops_second = transit_route['legs'][0]['steps'][3]['transit_details']['num_stops']
		arrival_stop_final = transit_route['legs'][0]['steps'][3]['transit_details']['arrival_stop']['name']
		bus_at_final_destination_stop = transit_route['legs'][0]['steps'][3]['transit_details']['arrival_time']['text'];

		lat3 = transit_route['legs'][0]['steps'][3]['transit_details']['arrival_stop']['location']['lat']
		long3 = transit_route['legs'][0]['steps'][3]['transit_details']['arrival_stop']['location']['lng']
		lat4 = transit_route['legs'][0]['steps'][3]['transit_details']['departure_stop']['location']['lat']
		long4 = transit_route['legs'][0]['steps'][3]['transit_details']['departure_stop']['location']['lng']
		list_with_direction = [departure_stop,bus_at_departure_stop,headsign_first,bus_number_first,number_of_stops_first,arrival_stop_transit,transit,departure_stop_transit,bus_at_transit_departure_stop,headsign_second,bus_number_second,number_of_stops_second,arrival_stop_final,bus_at_final_destination_stop,bus_at_intermediate_transfer_stop,lat1,long1,lat2,long2,lat3,long3,lat4,long4]

	return list_with_direction





def unix_time(dttm=None):
	'''
	The function is called from findroutedetails() to convert the user submitted date and time format to UTC time, since Google Maps
	API take input in UTC time

	'''
	from datetime import datetime
	from calendar import timegm
	if dttm is None:
		dttm = datetime.utcnow()
	return timegm(dttm.utctimetuple())

	
@csrf_exempt
def findroutedetails(request):
	'''
	On Clicking the 'Depart Now' button in the web-page, information/request submitted by the user (Eg: Departure date, Source and Destination) 
	is receieved by this function to extract the equivalent information from the request. Based on the source and destination, and the bus line
	(from Google routes), it is checked if a bus line is operated by 'Dublin Bus', in that case we find the intermediate stops for that line (to
	display as markers on the Map)and also the sequence number of source and destination bus stop for a particular bus line goes in as an input 
	to the machine learning model. In case if a bus line is not operated by Dublin Bus, the information from Google route itself is displayed to
	the user  
	'''
	source = request.POST['origin']
	destination = request.POST['destination']
	departure_date = request.POST.get('departure_date', False)  #Default to False in case, user has not chosen any departure date/time
	departure_time = request.POST.get('departure_time', False)
	
	print(source)
	print(destination)
	print("Departure date is",departure_date)
	print("Departure time  is",departure_time)
	url = "http://api.openweathermap.org/data/2.5/weather?id=7778677&APPID=a4822db1b5634c2e9e25209d1837cc69&units=metric"
	
	import requests	
	#if(departure_date==False and departure_time==False):
	if(departure_date=='' and departure_time==''):  #This has been commented for Load Testing where it takes default value of date and time as False instead of ''
		departure_date_time = unix_time()
		url = "http://api.openweathermap.org/data/2.5/weather?id=7778677&APPID=a4822db1b5634c2e9e25209d1837cc69&units=metric"
		r = requests.get(url)
		weather_data = r.json() 
		precip_prob = weather_data["weather"][0]["id"]
		temp = weather_data["main"]["temp"]
		print(weather_data["weather"][0]["id"])
		print(weather_data["main"]["temp"])
	#elif(departure_date==False and departure_time!=False): 
	elif(departure_date=='' and departure_time!=''): #This has been commented for Load Testing where it takes default value of date and time as False instead of ''
		x = str(datetime.now())
		date_today = x[0:10].split('-')
		time_hr_min = str(departure_time).split(':')
		departure_date_time = unix_time(datetime(int(date_today[0]),int(date_today[1]),int(date_today[2]),int(time_hr_min[0])-1,int(time_hr_min[1])))
		url = "http://api.openweathermap.org/data/2.5/weather?id=7778677&APPID=a4822db1b5634c2e9e25209d1837cc69&units=metric"
		r = requests.get(url)
		weather_data = r.json() 
		precip_prob = weather_data["weather"][0]["id"]
		temp = weather_data["main"]["temp"]
		print(weather_data["weather"][0]["id"])
		print(weather_data["main"]["temp"])

	else:
		date_requested = str(departure_date).split('-')
		time_hr_min = str(departure_time).split(':')

		departure_date_time = unix_time(datetime(int(date_requested[0]),int(date_requested[1]),int(date_requested[2]),int(time_hr_min[0])-1,int(time_hr_min[1])))
		url = "http://api.openweathermap.org/data/2.5/forecast?id=7778677&APPID=a4822db1b5634c2e9e25209d1837cc69&units=metric"
		r = requests.get(url)
		departure_date_used_weather = departure_date+" "+"00:00:00"
		# Parse the JSON
		data = r.json()
		for i in range(0,len(data['list'])):
			date=data['list'][i]['dt_txt']
			type(date)
			if(departure_date_used_weather==date):
				temp=data['list'][i]['main']['temp']
				cloud=data['list'][i]['weather'][0]['main']
				speed=data['list'][i]['wind']['speed']
				precip_prob = data['list'][i]["weather"][0]["id"]
				list_data=(temp,cloud,speed)
				print(temp)
				print(cloud)
				print(speed)
			else:
				precip_prob = 0
				temp = 0
	if(precip_prob>=500 and precip_prob<=622):
		precip_prob = 1
	else:
		precip_prob = 0
        


	# importing required libraries 
	
	import googlemaps
	

	gmaps = googlemaps.Client(key='AIzaSyBi-bH5_sngxNibrgygRZDhmAv2fK5hzus')

	x = gmaps.directions(origin=source,
                                     destination=destination,
                                     alternatives="true",
                                     mode="transit",
                                     transit_mode="bus",
                                     departure_time=departure_date_time
                                  	)  #Sending the request to Google MAPS DIRECTIONS API 
	

	if(len(x)!=0): #Check if Google MAPS API has not return Error as a response, otherwise the Else block returns 'Error' as response to the Ajax call
		
		sql_2 = """select distinct mydbservlet.stops_times.bus_number from mydbservlet.stops_times"""
		db = pymysql.connect(host="127.0.0.1", user="root", passwd="Ganesha-46", db="mydbservlet")
		cursor = db.cursor()
		cursor.execute(sql_2,)
		list_all_bus_numbers = cursor.fetchall()
		list_all_bus_numbers = list(list_all_bus_numbers)
		print("List of all Bus Lines in Dublin",list_all_bus_numbers)
		list_with_alternate_routes = []    #List of lists where direction information specific to all bus lines is stored, with information specific to a bus line stored as an indiviudal list 
		list_intermediate_bus_stops_alternate_stops = []  #List of lists where intermediate bus stops specific to a bus line is stored as a list
		sql = """select ﻿stop_lat,stop_lon,stop_id,stop_name,STOP_ID_LAST_4 from mydbservlet.stops_2ttest_bus_stops""" 
		db = pymysql.connect(host="127.0.0.1", user="root", passwd="Ganesha-46", db="mydbservlet")
		cursor = db.cursor()
		cursor.execute(sql,)
		result = list(cursor.fetchall())
		for i in x:
			if(len(i['legs'][0]['steps'])==3 ):  #Check if a journey is a single trip i.e., without requiring any bus transfer

				total_duration = i['legs'][0]['duration']['text']
				total_time = i['legs'][0]['distance']['text']
				html_inst1 = i['legs'][0]['steps'][0]['html_instructions']
				dist_bus_stop_walk = i['legs'][0]['steps'][0]['distance']['text']
				time_to_bus_stop_walk = i['legs'][0]['steps'][0]['duration']['text']
				html_inst2 = i['legs'][0]['steps'][1]['html_instructions']
				bus_distance = i['legs'][0]['steps'][1]['distance']['text']
				bus_time = i['legs'][0]['steps'][1]['duration']['text']
				departure_stop = i['legs'][0]['steps'][1]['transit_details']['departure_stop']['name']
				bus_at_departure_stop = i['legs'][0]['steps'][1]['transit_details']['departure_time']['text']
				headsign = i['legs'][0]['steps'][1]['transit_details']['headsign']
				bus_number = i['legs'][0]['steps'][1]['transit_details']['line']['short_name']
				number_of_stops = i['legs'][0]['steps'][1]['transit_details']['num_stops']
				arrival_stop = i['legs'][0]['steps'][1]['transit_details']['arrival_stop']['name']
				html_inst3 = i['legs'][0]['steps'][2]['html_instructions']
				distance_to_dest = i['legs'][0]['steps'][2]['distance']['text']
				time_by_walk_dest = i['legs'][0]['steps'][2]['duration']['text']
				bus_at_arrival_stop = i['legs'][0]['steps'][1]['transit_details']['arrival_time']['text']
				list_with_direction = [total_duration, total_time,html_inst1,dist_bus_stop_walk,time_to_bus_stop_walk,html_inst2,bus_distance,bus_time,departure_stop,bus_at_departure_stop,headsign,bus_number,number_of_stops,arrival_stop,html_inst3,distance_to_dest,bus_at_arrival_stop,time_by_walk_dest]
				list_with_alternate_routes.append(list_with_direction)

				lat1 = i['legs'][0]['steps'][1]['transit_details']['arrival_stop']['location']['lat']
				long1 = i['legs'][0]['steps'][1]['transit_details']['arrival_stop']['location']['lng']
				lat2 = i['legs'][0]['steps'][1]['transit_details']['departure_stop']['location']['lat']
				long2 = i['legs'][0]['steps'][1]['transit_details']['departure_stop']['location']['lng']

				#Check if the bus line suggested by Google direction API is available in our Dublin Bus database
				if(i['legs'][0]['steps'][1]['transit_details']['line']['short_name'].upper() in list(map(itemgetter(0),list_all_bus_numbers))):

					departure_stop ='%'+departure_stop+'%'
					arrival_stop ='%'+arrival_stop+'%'

					list_arrive_depart_stop_id = extract_correct_depart_arrival_stop_id(departure_stop,arrival_stop,bus_number,headsign,lat1,long1,lat2,long2,result)
					print("Return of extract_correct_depart_arrival_stop_id",list_arrive_depart_stop_id)
					if(list_arrive_depart_stop_id!=0):
						arrival_stop_id = list_arrive_depart_stop_id[0]
						departure_stop_id = list_arrive_depart_stop_id[1]			
						number_of_stops = int(number_of_stops)
						print("Bus Number is",bus_number)
						remove_duplicates = extract_seq_numbers_bus_stops(headsign,bus_number,arrival_stop_id,departure_stop_id,number_of_stops,bus_at_departure_stop,bus_at_arrival_stop,departure_date)
						list_intermediate_bus_stops_alternate_stops.append(remove_duplicates)
						departure_bus_seq = remove_duplicates[0][1]
						arrival_bus_seq = remove_duplicates[len(remove_duplicates)-1][1]
						list_time_info = ml_model(bus_number,departure_bus_seq,arrival_bus_seq,arrival_stop_id,departure_stop_id,bus_at_departure_stop,bus_at_arrival_stop,departure_date,precip_prob,temp)
						print("Result from Machine Learning Model is",list_time_info)
						if(len(list_time_info)!=0):
							list_with_alternate_routes[len(list_with_alternate_routes)-1][9] = list_time_info[0]   #Time of arrival of the bus at departure stop
							list_with_alternate_routes[len(list_with_alternate_routes)-1][16] = list_time_info[1]  #Time of arrival of the bus at arrival stop 

						print("-----------------------------------------------------------------------------------------")
					else: #This else is doing error handling if list_arrive_depart_stop_id returns 0 in case of a database failure
						pass
				else:
					list_intermediate_bus_stops_alternate_stops.append([])


			elif(len(i['legs'][0]['steps'])==4 or len(i['legs'][0]['steps'])==5 ): #To handle one or more bus transfer
				
				print("Routes from google apis",i)
				list_with_direction = get_transit_details(i)
				list_with_alternate_routes.append(list_with_direction)

				departure_stop = list_with_direction[0]
				bus_at_departure_stop = list_with_direction[1]
				headsign_first = list_with_direction[2]
				bus_number_first = list_with_direction[3]
				number_of_stops_first = list_with_direction[4]
				arrival_stop_transit = list_with_direction[5]
				bus_at_intermediate_transfer_stop = list_with_direction[14]
				lat1 = list_with_direction[15]
				long1 = list_with_direction[16]
				lat2 = list_with_direction[17]
				long2 = list_with_direction[18]
				lat3 = list_with_direction[19]
				long3 = list_with_direction[20]
				lat4 = list_with_direction[21]
				long4 = list_with_direction[22]

				departure_stop_transit = list_with_direction[7]
				bus_at_transit_departure_stop = list_with_direction[8]
				headsign_second = list_with_direction[9]
				bus_number_second = list_with_direction[10]
				number_of_stops_second = list_with_direction[11]
				arrival_stop_final = list_with_direction[12]
				bus_at_final_destination_stop = list_with_direction[13]
				print("Bus Number first is",bus_number_first)
				print("Bus Number second is",bus_number_second)
				print("Departure Stop",departure_stop)
				print("Arrival stop transit",arrival_stop_transit)
				print("Departure Stop Transit",departure_stop_transit)
				print("Arrival Stop Final",arrival_stop_final)

				#Check if all the bus lines (depending on bus transfers) suggested by Google direction API is available in our Dublin Bus database
				if(bus_number_first.upper() in list(map(itemgetter(0),list_all_bus_numbers)) and bus_number_second.upper() in list(map(itemgetter(0),list_all_bus_numbers))):
					list_remove_duplicates = []
					departure_stop ='%'+departure_stop+'%'
					arrival_stop_transit ='%'+arrival_stop_transit+'%'
					list_arrive_depart_stop_id=extract_correct_depart_arrival_stop_id(departure_stop,arrival_stop_transit,bus_number_first,headsign_first,lat1,long1,lat2,long2,result)
					if(list_arrive_depart_stop_id!=0):
						arrival_stop_id_first = list_arrive_depart_stop_id[0]
						departure_stop_id_first = list_arrive_depart_stop_id[1]
						
						number_of_stops_first = int(number_of_stops_first)
						print("Bus Number first is",bus_number_first)
						remove_duplicates = extract_seq_numbers_bus_stops(headsign_first,bus_number_first,arrival_stop_id_first,departure_stop_id_first,number_of_stops_first,bus_at_departure_stop,bus_at_intermediate_transfer_stop,departure_date)
						list_remove_duplicates.append(remove_duplicates)
						departure_bus_seq = remove_duplicates[0][1]
						arrival_bus_seq = remove_duplicates[len(remove_duplicates)-1][1]
						list_time_info = ml_model(bus_number_first,departure_bus_seq,arrival_bus_seq,arrival_stop_id_first,departure_stop_id_first,bus_at_departure_stop,bus_at_intermediate_transfer_stop,departure_date,precip_prob,temp)
						print("Result from Machine Learning Model is",list_time_info)
						if(len(list_time_info)!=0):
							list_with_alternate_routes[len(list_with_alternate_routes)-1][1] = list_time_info[0]
							list_with_alternate_routes[len(list_with_alternate_routes)-1][8] = list_time_info[1]

						#------------------------------TRANSIT PART SECOND LEG INFO-------------------------------------------#	
						departure_stop_transit ='%'+departure_stop_transit+'%'
						arrival_stop_final ='%'+arrival_stop_final+'%'
						list_arrive_depart_stop_id=extract_correct_depart_arrival_stop_id(departure_stop_transit,arrival_stop_final,bus_number_second,headsign_second,lat3,long3,lat4,long4,result)
						if(list_arrive_depart_stop_id!=0 and len(remove_duplicates)>=0):

							arrival_stop_id_second = list_arrive_depart_stop_id[0]
							departure_stop_id_second = list_arrive_depart_stop_id[1]
							
							number_of_stops_second = int(number_of_stops_second)
							print("Bus Number second is",bus_number_second)
							remove_duplicates = extract_seq_numbers_bus_stops(headsign_second,bus_number_second,arrival_stop_id_second,departure_stop_id_second,number_of_stops_second,bus_at_transit_departure_stop,bus_at_final_destination_stop,departure_date)
							
							#Add a check if remove_duplicates is [],pop the intermediate bus stops inserted for first leg
							list_remove_duplicates.append(remove_duplicates)
							list_intermediate_bus_stops_alternate_stops.append(list_remove_duplicates)
							departure_bus_seq = remove_duplicates[0][1]
							arrival_bus_seq = remove_duplicates[len(remove_duplicates)-1][1]
							list_time_info = ml_model(bus_number_second,departure_bus_seq,arrival_bus_seq,arrival_stop_id_second,departure_stop_id_second,bus_at_transit_departure_stop,bus_at_final_destination_stop,departure_date,precip_prob,temp)
							print("Result from Machine Learning Model is",list_time_info)
							if(len(list_time_info)!=0):
								list_with_alternate_routes[len(list_with_alternate_routes)-1][14] = list_time_info[0] #Time of arrival of the bus at intermediate transfer stop
								list_with_alternate_routes[len(list_with_alternate_routes)-1][13] = list_time_info[1] #Time of arrival of the bus at final arrival/destination stop

							
						else:
							pass
					else:
						pass

				else:
					list_intermediate_bus_stops_alternate_stops.append([])

		print("-----------------------------------------------------------------------------------------")
		print("List of intermediate_bus_stops_with individual sequence numbers",list_intermediate_bus_stops_alternate_stops)
		list_bus_lines = []
		for i in list_intermediate_bus_stops_alternate_stops:
			#if(len(i))
			if(len(i)!=0  and isinstance(i[0][0],str) == True):

				print(len(i))
				print(i[0])
				list_bus_lines.append(i[0][5])
			else:
				if(len(i)==2):
					appended_bus_line = i[0][0][5]+'/'+i[1][0][5]
					list_bus_lines.append(appended_bus_line)
				elif(len(i)==3):
					appended_bus_line = i[0][0][5]+'/'+i[1][0][5] +'/'+i[2][0][5]
					list_bus_lines.append(appended_bus_line)
				else:
					list_bus_lines.append([])

		print("List of bus lines from back end for user",list_bus_lines)

		return HttpResponse(json.dumps({'list_with_alternate_routes': list_with_alternate_routes,'list_intermediate_bus_stops_alternate_stops':list_intermediate_bus_stops_alternate_stops,'list_bus_lines':list_bus_lines,'departure_date_time':departure_date_time}))
	else:
		return HttpResponse("Error")




@csrf_exempt
def getnearestbusstops(request):
	'''
	To find and return  the seven closest bus stops (with all the information specific to a bus stop) to a user, fetching his current
	location using Geocode. The number of bus stops returned is flexible and can be changed to any number by changing the numeric value
	in argsort method. 
	The function is triggered when the user clicks 'Find nearest bus stops' on the web page

	'''
	try:

		from geopy.distance import great_circle
		from geopy import distance
		import numpy as np

		user_lat = request.POST['current_latitude']
		user_lng = request.POST['current_longitude']
		print("user's lat: ",user_lat)
		print("user's longitude: ",user_lng)
		user_location = (user_lat, user_lng)
		sql_4 = "SELECT * FROM mydbservlet.stops_2ttest_bus_stops"
		db = pymysql.connect(host="127.0.0.1", user="root", passwd="Ganesha-46", db="mydbservlet")
		cursor = db.cursor()
		cursor.execute(sql_4,)
		list_stop_details = cursor.fetchall()
		list_stop_details = list(list_stop_details)
		distances = []
		for i in list_stop_details:
			stop_location = (i[1],i[3])
			dist = distance.distance(user_location, stop_location).km
			distances.append(dist)
		closest_3_indexes = np.argsort(distances)[:7] #Change 7 to any number as much as you want for nearest bus numbers
		closest_3_stops = []
		for i in closest_3_indexes:
			closest_3_stops.append(list_stop_details[i])
		print("closest stops to your location is: ",closest_3_stops)
		closest_3_stops_bus_info = []

		for i in closest_3_stops:
			sql4 = "SELECT distinct bus_number,headsign FROM mydbservlet.stops_times where bus_stop_number=%s "
			cursor.execute(sql4,(i[4]),)
			list_buses_passing_a_stop = cursor.fetchall()
			print(list_buses_passing_a_stop)
			list_buses_passing_a_stop = list(list_buses_passing_a_stop)
			closest_3_stops_bus_info.append(list_buses_passing_a_stop)
		print("bus lines in 3 closest bus stops",closest_3_stops_bus_info)




		return HttpResponse(json.dumps({'closest_3_stops': closest_3_stops, 'closest_3_stops_bus_info': closest_3_stops_bus_info}))

	except:
		return("Error")

@csrf_exempt
def getalltouristplaces(request):
	'''
	To return list of all tourist places with their respective information (latitude, longitude, name and a breif history of the place).
	This function is triggered when the user ticks the check-box related to 'Tourist Mode' on the web-page

	'''
	try:
		sql_5 = "SELECT * FROM mydbservlet.tourist_places"
		db = pymysql.connect(host="127.0.0.1", user="root", passwd="Ganesha-46", db="mydbservlet")
		cursor = db.cursor()
		cursor.execute(sql_5,)
		list_tourist_places = cursor.fetchall()
		list_tourist_places = list(list_tourist_places)
		return HttpResponse(json.dumps({'list_tourist_places':list_tourist_places}))

	except:
		return("Error")

