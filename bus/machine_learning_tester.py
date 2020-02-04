import joblib
import _pickle as cPickle
import os
import math
CURRENT_DIR = os.path.dirname(__file__)

#The purpose of ml_model is to invoke the correct model pickle file based on the input parameters received from views.py
def ml_model(bus_line,departure_bus_seq,arrival_bus_seq,arrival_stop_id,departure_stop_id,bus_at_departure_stop,bus_at_arrival_stop,departure_date,precip_prob,temp):
	#Departure date needs to be passed as well from views.py
	try:
		import gc
		from datetime import date
		from datetime import datetime
		import calendar

		#If-else is to extract day of the week (eg: Monday/Sunday..) based on the date received from the user
		if(departure_date==''): #If no departure date has been selected by the user, it is assumed the date is for today/this-day
			departure_date = date.today()
			print(departure_date)
			day_of_week = calendar.day_name[departure_date.weekday()]
		else:
			departure_date = departure_date.split('-')
			print(departure_date)
			year = int(departure_date[0])
			month = int(departure_date[1])
			date = int(departure_date[2])
			departure_date = datetime(year,month,date)
			day_of_week = calendar.day_name[departure_date.weekday()]  

		print("Day of the week is",day_of_week)
		#import time,datetime
		print("Bus Line is",bus_line)
		extract_dept_stop_id = int(departure_stop_id[-4:])
		print("Extracted departure stop id is",extract_dept_stop_id)
		print("Sequence Number of departure stop id",departure_bus_seq)
		extract_arr_stop_id = int(arrival_stop_id[-4:])
		print("Extracted arrival stop id is",extract_arr_stop_id)
		print("Sequence Number of arrival stop id",arrival_bus_seq)
		print("Bus at depart stop from Google",bus_at_departure_stop)
		print("Bus at arrival stop from Google", bus_at_arrival_stop)
		
		'''
		Since the static time input to the Planned Arrival Time in the machine learning model is in milliseconds, the time format
		XX:YY is converted to equivalent milliseconds to be used for input to the model
		''' 
		a = bus_at_departure_stop[-2:]  #To convert time of arrival at departure stop to milliseconds
		if(a=='am'):
			print("Inside am")
			bus_at_departure_stop = bus_at_departure_stop[:-2]
			bus_at_departure_stop = bus_at_departure_stop.split(':')
			hr_in_sec_1 = int(bus_at_departure_stop[0])*3600
			mins_sec_1 = int(bus_at_departure_stop[1])*60
			time_secs_1 = hr_in_sec_1+mins_sec_1
		else:
			print("Inside pm")
			bus_at_departure_stop = bus_at_departure_stop[:-2]
			bus_at_departure_stop = bus_at_departure_stop.split(':')
			if(int(bus_at_departure_stop[0])==12):
				hr_in_sec_1 = (int(bus_at_departure_stop[0]))*3600
			else:
				hr_in_sec_1 = (int(bus_at_departure_stop[0])+12)*3600
			mins_sec_1 = int(bus_at_departure_stop[1])*60
			time_secs_1 = hr_in_sec_1+mins_sec_1

		print("Time in seconds1",time_secs_1)

		a = bus_at_arrival_stop[-2:] #To convert time of arrival at arrival stop to milliseconds
		if(a=='am'):
			print("Inside am")
			bus_at_arrival_stop = bus_at_arrival_stop[:-2]
			bus_at_arrival_stop = bus_at_arrival_stop.split(':')
			hr_in_sec_2 = int(bus_at_arrival_stop[0])*3600
			mins_sec_2 = int(bus_at_arrival_stop[1])*60
			time_secs_2 = hr_in_sec_2+mins_sec_2
		else:
			print("Inside pm")
			bus_at_arrival_stop = bus_at_arrival_stop[:-2]
			bus_at_arrival_stop = bus_at_arrival_stop.split(':')
			if(int(bus_at_arrival_stop[0])==12):
				hr_in_sec_2 = (int(bus_at_arrival_stop[0]))*3600
			else:
				hr_in_sec_2 = (int(bus_at_arrival_stop[0])+12)*3600


			
			mins_sec_2 = int(bus_at_arrival_stop[1])*60
			time_secs_2 = hr_in_sec_2+mins_sec_2

		print("Time in seconds2",time_secs_2)

		list_bus_lines_mon_fri = ['68A','747','66B','757','27X','33X','84A','7D','66X','66E','38B','67X','116','44B','38D','31B','25D', '32X', '51D', '16D', '46E', '84X', '7B', '69X', '15D', '41X', '142', '68X', '25X', '39X', '41D', '33D', '51X', '77X', '118', '33E']
		list_time_info = []  #Store arrival time at departure bus stop, arrival bus stop and the difference between the two in minutes

		if(bus_line in list_bus_lines_mon_fri):  #If condition is invoked is a bus line has a service from Monday-Friday
			file_name = bus_line+'.pickle'
			model_file = os.path.join(CURRENT_DIR, file_name)  #The path to the equivalent bus line model pickle file is set
			
			#Check the day of the week and the corresponding day of the week flag is set to 1, remaining are 0
			
			if(day_of_week=="Friday"):

				print("Inside day_of_week:->",day_of_week)

				request_to_model = [[int(departure_bus_seq),int(extract_dept_stop_id),time_secs_1,1,0,0,0,0,precip_prob,temp]]
				gc.disable()
				model = cPickle.load(open(model_file,'rb'))
				gc.enable()
				predicted_arrival_time_1 = int(model.predict(request_to_model))
				print("Predicted arrival time in milliseconds to the departure bus stop is",predicted_arrival_time_1)
				predicted_arrival_time_1_hour_mins = predicted_arrival_time_1/3600 #To convert it in hour-mins format Time-> XX:YY
				hour_part =  int(str(predicted_arrival_time_1_hour_mins).split('.')[0])
				mins_part =  int(str(predicted_arrival_time_1_hour_mins).split('.')[1][:2])
				mins_part = int((mins_part*60)/100)
				mins_part = str(mins_part)
				if(len(mins_part)==1):
					mins_part = '0'+mins_part
				hour_mins = str(hour_part)+':'+mins_part
				print("Predicted arrival time in XX:YY format to the departure bus stop is",hour_mins)
				list_time_info.append(hour_mins)

				request_to_model = [[int(arrival_bus_seq),int(extract_arr_stop_id),time_secs_2,1,0,0,0,0,precip_prob,temp]]
				predicted_arrival_time_2 = int(model.predict(request_to_model))
				print("Predicted arrival time in milliseconds to the arrival bus stop is",predicted_arrival_time_2)
				predicted_arrival_time_2_hour_mins = predicted_arrival_time_2/3600 #To convert it in hour-mins format Time-> XX:YY
				hour_part =  int(str(predicted_arrival_time_2_hour_mins).split('.')[0])
				mins_part =  int(str(predicted_arrival_time_2_hour_mins).split('.')[1][:2])
				mins_part = int((mins_part*60)/100)
				mins_part = str(mins_part)
				if(len(mins_part)==1):
					mins_part = '0'+mins_part
				hour_mins = str(hour_part)+':'+mins_part
				print("Predicted arrival time in XX:YY format to the arrival bus stop is",hour_mins)
				list_time_info.append(hour_mins)
				predicted_bus_journey_time = int((predicted_arrival_time_2 - predicted_arrival_time_1)/60) #Divided by 60 to get the bus journey time in minutes
				print("Estimated bus journey time in minutes",predicted_bus_journey_time)
				list_time_info.append(predicted_bus_journey_time)

				return list_time_info



			if(day_of_week=="Monday"):

				print("Inside day_of_week:->",day_of_week)

				request_to_model = [[int(departure_bus_seq),int(extract_dept_stop_id),time_secs_1,0,1,0,0,0,precip_prob,temp]]
				gc.disable()
				model = cPickle.load(open(model_file,'rb'))
				gc.enable()
				predicted_arrival_time_1 = int(model.predict(request_to_model))
				print("Predicted arrival time to the departure bus stop is",predicted_arrival_time_1)
				predicted_arrival_time_1_hour_mins = predicted_arrival_time_1/3600 #To convert it in hour-mins format Time-> XX:YY
				hour_part =  int(str(predicted_arrival_time_1_hour_mins).split('.')[0])
				mins_part =  int(str(predicted_arrival_time_1_hour_mins).split('.')[1][:2])
				mins_part = int((mins_part*60)/100)
				mins_part = str(mins_part)
				if(len(mins_part)==1):
					mins_part = '0'+mins_part
				hour_mins = str(hour_part)+':'+mins_part
				print("Predicted arrival time in XX:YY format to the departure bus stop is",hour_mins)
				list_time_info.append(hour_mins)

				request_to_model = [[int(arrival_bus_seq),int(extract_arr_stop_id),time_secs_2,0,1,0,0,0,precip_prob,temp]]
				predicted_arrival_time_2 = int(model.predict(request_to_model))
				print("Predicted arrival time to the arrival bus stop is",predicted_arrival_time_2)
				predicted_arrival_time_2_hour_mins = predicted_arrival_time_2/3600 #To convert it in hour-mins format Time-> XX:YY
				hour_part =  int(str(predicted_arrival_time_2_hour_mins).split('.')[0])
				mins_part =  int(str(predicted_arrival_time_2_hour_mins).split('.')[1][:2])
				mins_part = int((mins_part*60)/100)
				mins_part = str(mins_part)
				if(len(mins_part)==1):
					mins_part = '0'+mins_part
				hour_mins = str(hour_part)+':'+mins_part
				print("Predicted arrival time in XX:YY format to the arrival bus stop is",hour_mins)
				list_time_info.append(hour_mins)
				predicted_bus_journey_time = int((predicted_arrival_time_2 - predicted_arrival_time_1)/60) #Divided by 60 to get the bus journey time in minutes
				print("Estimated bus journey time in minutes",predicted_bus_journey_time)
				list_time_info.append(predicted_bus_journey_time)
				return list_time_info
				




			if(day_of_week=="Thursday"):

				print("Inside day_of_week:->",day_of_week)

				request_to_model = [[int(departure_bus_seq),int(extract_dept_stop_id),time_secs_1,0,0,1,0,0,precip_prob,temp]]
				gc.disable()
				model = cPickle.load(open(model_file,'rb'))
				gc.enable()
				predicted_arrival_time_1 = int(model.predict(request_to_model))
				print("Predicted arrival time to the departure bus stop is",predicted_arrival_time_1)
				predicted_arrival_time_1_hour_mins = predicted_arrival_time_1/3600 #To convert it in hour-mins format Time-> XX:YY
				hour_part =  int(str(predicted_arrival_time_1_hour_mins).split('.')[0])
				mins_part =  int(str(predicted_arrival_time_1_hour_mins).split('.')[1][:2])
				mins_part = int((mins_part*60)/100)
				mins_part = str(mins_part)
				if(len(mins_part)==1):
					mins_part = '0'+mins_part
				hour_mins = str(hour_part)+':'+mins_part
				print("Predicted arrival time in XX:YY format to the departure bus stop is",hour_mins)
				list_time_info.append(hour_mins)
				request_to_model = [[int(arrival_bus_seq),int(extract_arr_stop_id),time_secs_2,0,0,1,0,0,precip_prob,temp]]
				predicted_arrival_time_2 = int(model.predict(request_to_model))
				print("Predicted arrival time to the arrival bus stop is",predicted_arrival_time_2)
				predicted_arrival_time_2_hour_mins = predicted_arrival_time_2/3600 #To convert it in hour-mins format Time-> XX:YY
				hour_part =  int(str(predicted_arrival_time_2_hour_mins).split('.')[0])
				mins_part =  int(str(predicted_arrival_time_2_hour_mins).split('.')[1][:2])
				mins_part = int((mins_part*60)/100)
				mins_part = str(mins_part)
				if(len(mins_part)==1):
					mins_part = '0'+mins_part
				hour_mins = str(hour_part)+':'+mins_part
				print("Predicted arrival time in XX:YY format to the arrival bus stop is",hour_mins)
				list_time_info.append(hour_mins)
				predicted_bus_journey_time = int((predicted_arrival_time_2 - predicted_arrival_time_1)/60) #Divided by 60 to get the bus journey time in minutes
				print("Estimated bus journey time in minutes",predicted_bus_journey_time)
				list_time_info.append(predicted_bus_journey_time)
				return list_time_info


			if(day_of_week=="Tuesday"):

				print("Inside day_of_week:->",day_of_week)

				request_to_model = [[int(departure_bus_seq),int(extract_dept_stop_id),time_secs_1,0,0,0,1,0,precip_prob,temp]]
				gc.disable()
				model = cPickle.load(open(model_file,'rb'))
				gc.enable()
				predicted_arrival_time_1 = int(model.predict(request_to_model))
				print("Predicted arrival time to the departure bus stop is",predicted_arrival_time_1)
				predicted_arrival_time_1_hour_mins = predicted_arrival_time_1/3600 #To convert it in hour-mins format Time-> XX:YY
				hour_part =  int(str(predicted_arrival_time_1_hour_mins).split('.')[0])
				mins_part =  int(str(predicted_arrival_time_1_hour_mins).split('.')[1][:2])
				mins_part = int((mins_part*60)/100)
				mins_part = str(mins_part)
				if(len(mins_part)==1):
					mins_part = '0'+mins_part
				hour_mins = str(hour_part)+':'+mins_part
				print("Predicted arrival time in XX:YY format to the departure bus stop is",hour_mins)
				list_time_info.append(hour_mins)
				request_to_model = [[int(arrival_bus_seq),int(extract_arr_stop_id),time_secs_2,0,0,0,1,0,precip_prob,temp]]
				predicted_arrival_time_2 = int(model.predict(request_to_model))
				print("Predicted arrival time to the arrival bus stop is",predicted_arrival_time_2)
				predicted_arrival_time_2_hour_mins = predicted_arrival_time_2/3600 #To convert it in hour-mins format Time-> XX:YY
				hour_part =  int(str(predicted_arrival_time_2_hour_mins).split('.')[0])
				mins_part =  int(str(predicted_arrival_time_2_hour_mins).split('.')[1][:2])
				mins_part = int((mins_part*60)/100)
				mins_part = str(mins_part)
				if(len(mins_part)==1):
					mins_part = '0'+mins_part
				hour_mins = str(hour_part)+':'+mins_part
				print("Predicted arrival time in XX:YY format to the arrival bus stop is",hour_mins)
				list_time_info.append(hour_mins)
				predicted_bus_journey_time = int((predicted_arrival_time_2 - predicted_arrival_time_1)/60) #Divided by 60 to get the bus journey time in minutes
				print("Estimated bus journey time in minutes",predicted_bus_journey_time)
				list_time_info.append(predicted_bus_journey_time)
				return list_time_info



			if(day_of_week=="Wednesday"):

				print("Inside day_of_week:->",day_of_week)

				request_to_model = [[int(departure_bus_seq),int(extract_dept_stop_id),time_secs_1,0,0,0,0,1,precip_prob,temp]]
				gc.disable()
				model = cPickle.load(open(model_file,'rb'))
				gc.enable()
				predicted_arrival_time_1 = int(model.predict(request_to_model))
				print("Predicted arrival time to the departure bus stop is",predicted_arrival_time_1)
				predicted_arrival_time_1_hour_mins = predicted_arrival_time_1/3600 #To convert it in hour-mins format Time-> XX:YY
				hour_part =  int(str(predicted_arrival_time_1_hour_mins).split('.')[0])
				mins_part =  int(str(predicted_arrival_time_1_hour_mins).split('.')[1][:2])
				mins_part = int((mins_part*60)/100)
				mins_part = str(mins_part)
				if(len(mins_part)==1):
					mins_part = '0'+mins_part
				hour_mins = str(hour_part)+':'+mins_part
				print("Predicted arrival time in XX:YY format to the departure bus stop is",hour_mins)
				list_time_info.append(hour_mins)
				request_to_model = [[int(arrival_bus_seq),int(extract_arr_stop_id),time_secs_2,0,0,0,0,1,precip_prob,temp]]
				predicted_arrival_time_2 = int(model.predict(request_to_model))
				print("Predicted arrival time to the arrival bus stop is",predicted_arrival_time_2)
				predicted_arrival_time_2_hour_mins = predicted_arrival_time_2/3600 #To convert it in hour-mins format Time-> XX:YY
				hour_part =  int(str(predicted_arrival_time_2_hour_mins).split('.')[0])
				mins_part =  int(str(predicted_arrival_time_2_hour_mins).split('.')[1][:2])
				mins_part = int((mins_part*60)/100)
				mins_part = str(mins_part)
				if(len(mins_part)==1):
					mins_part = '0'+mins_part
				hour_mins = str(hour_part)+':'+mins_part
				print("Predicted arrival time in XX:YY format to the arrival bus stop is",hour_mins)
				list_time_info.append(hour_mins)
				predicted_bus_journey_time = int((predicted_arrival_time_2 - predicted_arrival_time_1)/60) #Divided by 60 to get the bus journey time in minutes
				print("Estimated bus journey time in minutes",predicted_bus_journey_time)
				list_time_info.append(predicted_bus_journey_time)
				return list_time_info

			else:
				return list_time_info
		
		#Else condition is triggered for bus lines operating Monday-Sunday
		else: 
			file_name = bus_line+'.pickle'
			model_file = os.path.join(CURRENT_DIR, file_name) #The path to the equivalent bus line model pickle file is set

			#Check the day of the week and the corresponding day of the week flag is set to 1, remaining are 0
			
			if(day_of_week=="Monday"):

				print("Inside Else Part day_of_week:->",day_of_week)  #take this print statements out
				request_to_model = [[int(departure_bus_seq),int(extract_dept_stop_id),time_secs_1,1,0,0,0,0,0,precip_prob,temp]]
				gc.disable()
				model = cPickle.load(open(model_file,'rb'))
				gc.enable()
				predicted_arrival_time_1 = int(model.predict(request_to_model))
				print("Predicted arrival time to the departure bus stop is",predicted_arrival_time_1)
				predicted_arrival_time_1_hour_mins = predicted_arrival_time_1/3600 #To convert it in hour-mins format Time-> XX:YY
				hour_part =  int(str(predicted_arrival_time_1_hour_mins).split('.')[0])
				mins_part =  int(str(predicted_arrival_time_1_hour_mins).split('.')[1][:2])
				mins_part = int((mins_part*60)/100)
				mins_part = str(mins_part)
				if(len(mins_part)==1):
					mins_part = '0'+mins_part
				hour_mins = str(hour_part)+':'+mins_part
				print("Predicted arrival time in XX:YY format to the departure bus stop is",hour_mins)
				list_time_info.append(hour_mins)
				request_to_model = [[int(arrival_bus_seq),int(extract_arr_stop_id),time_secs_2,1,0,0,0,0,0,precip_prob,temp]]
				predicted_arrival_time_2 = int(model.predict(request_to_model))
				print("Predicted arrival time to the arrival bus stop is",predicted_arrival_time_2)
				predicted_arrival_time_2_hour_mins = predicted_arrival_time_2/3600 #To convert it in hour-mins format Time-> XX:YY
				hour_part =  int(str(predicted_arrival_time_2_hour_mins).split('.')[0])
				mins_part =  int(str(predicted_arrival_time_2_hour_mins).split('.')[1][:2])
				mins_part = int((mins_part*60)/100)
				mins_part = str(mins_part)
				if(len(mins_part)==1):
					mins_part = '0'+mins_part
				hour_mins = str(hour_part)+':'+mins_part
				print("Predicted arrival time in XX:YY format to the arrival bus stop is",hour_mins)
				list_time_info.append(hour_mins)
				predicted_bus_journey_time = int((predicted_arrival_time_2 - predicted_arrival_time_1)/60) #Divided by 60 to get the bus journey time in minutes
				print("Estimated bus journey time in minutes",predicted_bus_journey_time)
				list_time_info.append(predicted_bus_journey_time)
				return list_time_info

			if(day_of_week=="Saturday"):

				print("Inside Else Part day_of_week:->",day_of_week)

				request_to_model = [[int(departure_bus_seq),int(extract_dept_stop_id),time_secs_1,0,1,0,0,0,0,precip_prob,temp]]
				gc.disable()
				model = cPickle.load(open(model_file,'rb'))
				gc.enable()
				predicted_arrival_time_1 = int(model.predict(request_to_model))
				print("Predicted arrival time to the departure bus stop is",predicted_arrival_time_1)
				predicted_arrival_time_1_hour_mins = predicted_arrival_time_1/3600 #To convert it in hour-mins format Time-> XX:YY
				hour_part =  int(str(predicted_arrival_time_1_hour_mins).split('.')[0])
				mins_part =  int(str(predicted_arrival_time_1_hour_mins).split('.')[1][:2])
				mins_part = int((mins_part*60)/100)
				mins_part = str(mins_part)
				if(len(mins_part)==1):
					mins_part = '0'+mins_part
				hour_mins = str(hour_part)+':'+mins_part
				print("Predicted arrival time in XX:YY format to the departure bus stop is",hour_mins)
				list_time_info.append(hour_mins)

				request_to_model = [[int(arrival_bus_seq),int(extract_arr_stop_id),time_secs_2,0,1,0,0,0,0,precip_prob,temp]]
				predicted_arrival_time_2 = int(model.predict(request_to_model))
				print("Predicted arrival time to the arrival bus stop is",predicted_arrival_time_2)
				predicted_arrival_time_2_hour_mins = predicted_arrival_time_2/3600 #To convert it in hour-mins format Time-> XX:YY
				hour_part =  int(str(predicted_arrival_time_2_hour_mins).split('.')[0])
				mins_part =  int(str(predicted_arrival_time_2_hour_mins).split('.')[1][:2])
				mins_part = int((mins_part*60)/100)
				mins_part = str(mins_part)
				if(len(mins_part)==1):
					mins_part = '0'+mins_part
				hour_mins = str(hour_part)+':'+mins_part
				print("Predicted arrival time in XX:YY format to the arrival bus stop is",hour_mins)
				list_time_info.append(hour_mins)
				predicted_bus_journey_time = int((predicted_arrival_time_2 - predicted_arrival_time_1)/60) #Divided by 60 to get the bus journey time in minutes
				print("Estimated bus journey time in minutes",predicted_bus_journey_time)
				list_time_info.append(predicted_bus_journey_time)



				return list_time_info

			if(day_of_week=="Sunday"):

				print("Inside Else Part day_of_week:->",day_of_week)

				request_to_model = [[int(departure_bus_seq),int(extract_dept_stop_id),time_secs_1,0,0,1,0,0,0,precip_prob,temp]]
				gc.disable()
				model = cPickle.load(open(model_file,'rb'))
				gc.enable()
				predicted_arrival_time_1 = int(model.predict(request_to_model))
				print("Predicted arrival time to the departure bus stop is",predicted_arrival_time_1)
				predicted_arrival_time_1_hour_mins = predicted_arrival_time_1/3600 #To convert it in hour-mins format Time-> XX:YY
				hour_part =  int(str(predicted_arrival_time_1_hour_mins).split('.')[0])
				mins_part =  int(str(predicted_arrival_time_1_hour_mins).split('.')[1][:2])
				mins_part = int((mins_part*60)/100)
				mins_part = str(mins_part)
				if(len(mins_part)==1):
					mins_part = '0'+mins_part
				hour_mins = str(hour_part)+':'+mins_part
				print("Predicted arrival time in XX:YY format to the departure bus stop is",hour_mins)
				list_time_info.append(hour_mins)
				request_to_model = [[int(arrival_bus_seq),int(extract_arr_stop_id),time_secs_2,0,0,1,0,0,0,precip_prob,temp]]
				predicted_arrival_time_2 = int(model.predict(request_to_model))
				print("Predicted arrival time to the arrival bus stop is",predicted_arrival_time_2)
				predicted_arrival_time_2_hour_mins = predicted_arrival_time_2/3600 #To convert it in hour-mins format Time-> XX:YY
				hour_part =  int(str(predicted_arrival_time_2_hour_mins).split('.')[0])
				mins_part =  int(str(predicted_arrival_time_2_hour_mins).split('.')[1][:2])
				mins_part = int((mins_part*60)/100)
				mins_part = str(mins_part)
				if(len(mins_part)==1):
					mins_part = '0'+mins_part
				hour_mins = str(hour_part)+':'+mins_part
				print("Predicted arrival time in XX:YY format to the arrival bus stop is",hour_mins)
				list_time_info.append(hour_mins)
				predicted_bus_journey_time = int((predicted_arrival_time_2 - predicted_arrival_time_1)/60) #Divided by 60 to get the bus journey time in minutes
				print("Estimated bus journey time in minutes",predicted_bus_journey_time)
				list_time_info.append(predicted_bus_journey_time)
				return list_time_info



			if(day_of_week=="Thursday"):

				print("Inside Else Part day_of_week:->",day_of_week)

				request_to_model = [[int(departure_bus_seq),int(extract_dept_stop_id),time_secs_1,0,0,0,1,0,0,precip_prob,temp]]
				gc.disable()
				model = cPickle.load(open(model_file,'rb'))
				gc.enable()
				predicted_arrival_time_1 = int(model.predict(request_to_model))
				print("Predicted arrival time to the departure bus stop is",predicted_arrival_time_1)
				predicted_arrival_time_1_hour_mins = predicted_arrival_time_1/3600 #To convert it in hour-mins format Time-> XX:YY
				hour_part =  int(str(predicted_arrival_time_1_hour_mins).split('.')[0])
				mins_part =  int(str(predicted_arrival_time_1_hour_mins).split('.')[1][:2])
				mins_part = int((mins_part*60)/100)
				mins_part = str(mins_part)
				if(len(mins_part)==1):
					mins_part = '0'+mins_part
				hour_mins = str(hour_part)+':'+mins_part
				print("Predicted arrival time in XX:YY format to the departure bus stop is",hour_mins)
				list_time_info.append(hour_mins)
				request_to_model = [[int(arrival_bus_seq),int(extract_arr_stop_id),time_secs_2,0,0,0,1,0,0,precip_prob,temp]]
				predicted_arrival_time_2 = int(model.predict(request_to_model))
				print("Predicted arrival time to the arrival bus stop is",predicted_arrival_time_2)
				predicted_arrival_time_2_hour_mins = predicted_arrival_time_2/3600 #To convert it in hour-mins format Time-> XX:YY
				hour_part =  int(str(predicted_arrival_time_2_hour_mins).split('.')[0])
				mins_part =  int(str(predicted_arrival_time_2_hour_mins).split('.')[1][:2])
				mins_part = int((mins_part*60)/100)
				mins_part = str(mins_part)
				if(len(mins_part)==1):
					mins_part = '0'+mins_part
				hour_mins = str(hour_part)+':'+mins_part
				print("Predicted arrival time in XX:YY format to the arrival bus stop is",hour_mins)
				list_time_info.append(hour_mins)
				predicted_bus_journey_time = int((predicted_arrival_time_2 - predicted_arrival_time_1)/60) #Divided by 60 to get the bus journey time in minutes
				print("Estimated bus journey time in minutes",predicted_bus_journey_time)
				list_time_info.append(predicted_bus_journey_time)
				return list_time_info



			if(day_of_week=="Tuesday"):

				print("Inside Else Part day_of_week:->",day_of_week)

				request_to_model = [[int(departure_bus_seq),int(extract_dept_stop_id),time_secs_1,0,0,0,0,1,0,precip_prob,temp]]
				gc.disable()
				model = cPickle.load(open(model_file,'rb'))
				gc.enable()
				predicted_arrival_time_1 = int(model.predict(request_to_model))
				print("Predicted arrival time to the departure bus stop is",predicted_arrival_time_1)
				predicted_arrival_time_1_hour_mins = predicted_arrival_time_1/3600 #To convert it in hour-mins format Time-> XX:YY
				hour_part =  int(str(predicted_arrival_time_1_hour_mins).split('.')[0])
				mins_part =  int(str(predicted_arrival_time_1_hour_mins).split('.')[1][:2])
				mins_part = int((mins_part*60)/100)
				mins_part = str(mins_part)
				if(len(mins_part)==1):
					mins_part = '0'+mins_part
				hour_mins = str(hour_part)+':'+mins_part
				print("Predicted arrival time in XX:YY format to the departure bus stop is",hour_mins)
				list_time_info.append(hour_mins)
				request_to_model = [[int(arrival_bus_seq),int(extract_arr_stop_id),time_secs_2,0,0,0,0,1,0,precip_prob,temp]]
				predicted_arrival_time_2 = int(model.predict(request_to_model))
				print("Predicted arrival time to the arrival bus stop is",predicted_arrival_time_2)
				predicted_arrival_time_2_hour_mins = predicted_arrival_time_2/3600 #To convert it in hour-mins format Time-> XX:YY
				hour_part =  int(str(predicted_arrival_time_2_hour_mins).split('.')[0])
				mins_part =  int(str(predicted_arrival_time_2_hour_mins).split('.')[1][:2])
				mins_part = int((mins_part*60)/100)
				mins_part = str(mins_part)
				if(len(mins_part)==1):
					mins_part = '0'+mins_part
				hour_mins = str(hour_part)+':'+mins_part
				print("Predicted arrival time in XX:YY format to the arrival bus stop is",hour_mins)
				list_time_info.append(hour_mins)
				predicted_bus_journey_time = int((predicted_arrival_time_2 - predicted_arrival_time_1)/60) #Divided by 60 to get the bus journey time in minutes
				print("Estimated bus journey time in minutes",predicted_bus_journey_time)
				list_time_info.append(predicted_bus_journey_time)
				return list_time_info




			if(day_of_week=="Wednesday"):

				print("Inside Else Part day_of_week:->",day_of_week)

				request_to_model = [[int(departure_bus_seq),int(extract_dept_stop_id),time_secs_1,0,0,0,0,0,1,precip_prob,temp]]
				gc.disable()
				model = cPickle.load(open(model_file,'rb'))
				gc.enable()
				predicted_arrival_time_1 = int(model.predict(request_to_model))
				print("Predicted arrival time to the departure bus stop is",predicted_arrival_time_1)
				predicted_arrival_time_1_hour_mins = predicted_arrival_time_1/3600 #To convert it in hour-mins format Time-> XX:YY
				hour_part =  int(str(predicted_arrival_time_1_hour_mins).split('.')[0])
				mins_part =  int(str(predicted_arrival_time_1_hour_mins).split('.')[1][:2])
				mins_part = int((mins_part*60)/100)
				mins_part = str(mins_part)
				if(len(mins_part)==1):
					mins_part = '0'+mins_part
				hour_mins = str(hour_part)+':'+mins_part
				print("Predicted arrival time in XX:YY format to the departure bus stop is",hour_mins)
				list_time_info.append(hour_mins)
				request_to_model = [[int(arrival_bus_seq),int(extract_arr_stop_id),time_secs_2,0,0,0,0,0,1,precip_prob,temp]]
				predicted_arrival_time_2 = int(model.predict(request_to_model))
				print("Predicted arrival time to the arrival bus stop is",predicted_arrival_time_2)
				predicted_arrival_time_2_hour_mins = predicted_arrival_time_2/3600 #To convert it in hour-mins format Time-> XX:YY
				hour_part =  int(str(predicted_arrival_time_2_hour_mins).split('.')[0])
				mins_part =  int(str(predicted_arrival_time_2_hour_mins).split('.')[1][:2])
				mins_part = int((mins_part*60)/100)
				mins_part = str(mins_part)
				if(len(mins_part)==1):
					mins_part = '0'+mins_part
				hour_mins = str(hour_part)+':'+mins_part
				print("Predicted arrival time in XX:YY format to the arrival bus stop is",hour_mins)
				list_time_info.append(hour_mins)
				predicted_bus_journey_time = int((predicted_arrival_time_2 - predicted_arrival_time_1)/60) #Divided by 60 to get the bus journey time in minutes
				print("Estimated bus journey time in minutes",predicted_bus_journey_time)
				list_time_info.append(predicted_bus_journey_time)
				return list_time_info

			#If Day of the week is Friday
			else:

				print("Inside Else Part day_of_week:->",day_of_week)

				request_to_model = [[int(departure_bus_seq),int(extract_dept_stop_id),time_secs_1,0,0,0,0,0,0,precip_prob,temp]]
				gc.disable()
				model = cPickle.load(open(model_file,'rb'))
				gc.enable()
				predicted_arrival_time_1 = int(model.predict(request_to_model))
				print("Predicted arrival time to the departure bus stop is",predicted_arrival_time_1)
				predicted_arrival_time_1_hour_mins = predicted_arrival_time_1/3600 #To convert it in hour-mins format Time-> XX:YY
				hour_part =  int(str(predicted_arrival_time_1_hour_mins).split('.')[0])
				mins_part =  int(str(predicted_arrival_time_1_hour_mins).split('.')[1][:2])
				mins_part = int((mins_part*60)/100)
				mins_part = str(mins_part)
				if(len(mins_part)==1):
					mins_part = '0'+mins_part
				hour_mins = str(hour_part)+':'+mins_part
				print("Predicted arrival time in XX:YY format to the departure bus stop is",hour_mins)
				list_time_info.append(hour_mins)
				request_to_model = [[int(arrival_bus_seq),int(extract_arr_stop_id),time_secs_2,0,0,0,0,0,0,precip_prob,temp]]
				predicted_arrival_time_2 = int(model.predict(request_to_model))
				print("Predicted arrival time to the arrival bus stop is",predicted_arrival_time_2)
				predicted_arrival_time_2_hour_mins = predicted_arrival_time_2/3600 #To convert it in hour-mins format Time-> XX:YY
				hour_part =  int(str(predicted_arrival_time_2_hour_mins).split('.')[0])
				mins_part =  int(str(predicted_arrival_time_2_hour_mins).split('.')[1][:2])
				mins_part = int((mins_part*60)/100)
				mins_part = str(mins_part)
				if(len(mins_part)==1):
					mins_part = '0'+mins_part
				hour_mins = str(hour_part)+':'+mins_part
				print("Predicted arrival time in XX:YY format to the arrival bus stop is",hour_mins)
				list_time_info.append(hour_mins)

				predicted_bus_journey_time = int((predicted_arrival_time_2 - predicted_arrival_time_1)/60) #Divided by 60 to get the bus journey time in minutes
				print("Estimated bus journey time in minutes",predicted_bus_journey_time)
				list_time_info.append(predicted_bus_journey_time)
				return list_time_info

	except: #If a bus line does not have its equivalent pickle file/ Any error triggered from the model - Return an empty list
		print("Bus Line not availabe for machine learning model")
		return list_time_info










	


	
	
