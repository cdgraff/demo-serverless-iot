#!/usr/bin/python
import os
import time
import datetime
import json
from google.cloud import pubsub
from oauth2client.client import GoogleCredentials
from sense_hat import SenseHat
from tendo import singleton
from time import mktime

me = singleton.SingleInstance() # will sys.exit(-1) if other instance is running

# constants - change to fit your project and location
SEND_INTERVAL = 60 #seconds
credentials = GoogleCredentials.get_application_default()
# change project to your Project ID
project="vaulted-botany-211900"
# change topic to your PubSub topic name
topic = "sensordata"
# set the following four constants to be indicative of where you are placing your weather sensor
sensorID = "s-home-1"
sensorZipCode = "1173"
sensorLat = "-34.604549"
sensorLong = "-58.414730"

def createJSON(id, timestamp, zip, lat, long, temperature, humidity, pressure):
    data = {
      'sensorID' : id,
      'timecollected' : timestamp,
      'zipcode' : zip,
      'latitude' : lat,
      'longitude' : long,
      'temperature' : temperature,
      'humidity' : humidity,
      'pressure' : pressure
    }

    json_str = json.dumps(data)
    return json_str

def main():
  publisher = pubsub.PublisherClient()
  topicName = 'projects/' + project + '/topics/' + topic
  last_checked = 0
  while True:
    if time.time() - last_checked > SEND_INTERVAL:
      last_checked = time.time()
      temp, hum, pres = read_sensor()
      currentTime = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
      s = ", "
      sensorJSON = createJSON(sensorID, currentTime, sensorZipCode, sensorLat, sensorLong, temp, hum, pres)
      try:
	publisher.publish(topicName, sensorJSON, placeholder='')
	print sensorJSON
      except:
	print "There was an error publishing sensor data."

      if temp > 18.3 and temp < 26.7:
          bg = [0, 100, 0]  # green
      else:
          bg = [100, 0, 0]  # red

      msg = "Temperature = %s - Humidity=%s - Pressure=%s" % (temp, hum, pres)

      sense.show_message(msg, scroll_speed=0.07, back_colour=bg)


# get CPU temperature
def get_cpu_temp():
  res = os.popen("vcgencmd measure_temp").readline()
  t = float(res.replace("temp=","").replace("'C\n",""))
  return(t)

# use moving average to smooth readings
def get_smooth(x):
  if not hasattr(get_smooth, "t"):
    get_smooth.t = [x,x,x]
  get_smooth.t[2] = get_smooth.t[1]
  get_smooth.t[1] = get_smooth.t[0]
  get_smooth.t[0] = x
  xs = (get_smooth.t[0]+get_smooth.t[1]+get_smooth.t[2])/3
  return(xs)


sense = SenseHat()
sense.set_rotation(270)


def read_sensor():
  t1 = sense.get_temperature_from_humidity()
  t2 = sense.get_temperature_from_pressure()
  t_cpu = get_cpu_temp()
  h = sense.get_humidity()
  p = sense.get_pressure()

  # calculates the real temperature compesating CPU heating
  t = (t1+t2)/2
  t_corr = t - ((t_cpu-t)/1.5)
  t_corr = get_smooth(t_corr)

  t = round(t_corr, 1)
  p = round(p, 1)
  h = round(h, 1)
  return(t, h, p)

while True:
  if __name__ == '__main__':
      main()

#  print("t1=%.1f  t2=%.1f  t_cpu=%.1f  t_corr=%.1f  h=%d  p=%d" % (t1, t2, t_cpu, t_corr, round(h), round(p)))
  time.sleep(5)
