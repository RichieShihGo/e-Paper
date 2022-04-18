#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import ctypes
import os
#picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
#libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
libdir = "/home/pi/e-Paper/lib"
picdir = "/home/pi/e-Paper/pic"

url_file_path = "/home/pi/e-Paper/epaper_meeting_room.config"
room_name_file_path = "/home/pi/e-Paper/room_name.config"


if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd7in5b_HD
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

import requests
from bs4 import BeautifulSoup

import time
from time import sleep
from datetime import datetime

URL = 'http://192.1.1.50/sys/sys310w.aspx'

logging.basicConfig(level=logging.DEBUG)

meeting_room_name = "SJ14"

meeting_room_title = ""

now_idx=-1
next_idx=-1

class MeetingRoom:
    def __init__(self):
        self.name = ""
        self.reserved_dept = ""
        self.purpose = ""
        self.date = ""
        self.startTime = ""
        self.endTime = ""
        self.status = ""


class DynamicArray(MeetingRoom):
    #Initialize it
    def __init__(self):
        #We'll have three attributes
        self.n = 0 # by default
        self.capacity = 1 # by default
        self.A = self.make_array(self.capacity) # make_array will be defined later
    #Length method
    def __len__(self):
        #It will return number of elements in the array
        return self.n
    def __getitem__(self, k):
        #it will return the elements at the index k
        if not 0 <=k <self.n:
            return IndexError('k is out of bounds')
        return self.A[k]
    def append(self, element):
        #checking the capacity
        if self.n == self.capacity:
            #double the capacity for the new array i.e
            self.resize(2*self.capacity) # _resize is the method that is defined later
        # set the n indexes of array A to elements
        self.A[self.n] = element
        self.n += 1
    def resize(self, new_cap): #new_cap is for new capacity
        #declare array B
        B = self.make_array(new_cap)
        for k in range(self.n):
            B[k] = self.A[k] # referencing the elements from array A to B
            #ones refered then
        self.A = B # A is now the array B
        self.capacity = new_cap # resets the capacity
        #making the make-array method using ctypes
    def make_array(self,new_cap):
        return (new_cap * ctypes.py_object)()

    def clear(self):
        self.n = 0
        self.capacity = 1
        self.A = []
        self.A = self.make_array(self.capacity)

    #def sort(self):
        #self.sort(key=lambda x: x.ipaddr, reverse=False)
    #    self.sorted()

    #    return self

#meetingRoomArray = None
meetingRoomArray = DynamicArray()
#now_idx = -1
#next_idx = -1

match_room_total = 0

def load_meeting_page():

    print("=== load_meeting_page start ===")

    #meetingRoomArray = []

    global meeting_room_name

    print("meeting room = %d" % len(meetingRoomArray))

    if os.path.exists(url_file_path):
        #web_url
        fp = open(url_file_path, "r")
        line = fp.readline()
        line = line.replace("\n", "")
        fp.close()

        URL = line        
        #room name
        fp2 = open(room_name_file_path, "r")
        line = fp2.readline()
        line = line.replace("\n", "")
        fp2.close()

        meeting_room_name = line

        response = requests.get(URL)
        print(response.status_code)

        if response.status_code == 200:

            soup = BeautifulSoup(response.content, 'html.parser')

            td_elems = soup.find_all('td')

            match_room_total = 0

            for td_elem in td_elems:
            #print(td_elem.text)

                if meeting_room_name in td_elem.text:
                    match_room_total = match_room_total + 1

            print("match_room_total = %d" % match_room_total)

            meetingRoomArray.clear()

            print("meetingRoomArray = %d" % len(meetingRoomArray))

            #if match_room_total > 0:
            #    meetingRoomArray = [MeetingRoom() for x in range(match_room_total)]

            idx = 0
            fetch = False
            count = 0

            for td_elem in td_elems:

                if meeting_room_name in td_elem.text:
                    fetch = True
                    room = MeetingRoom()

                if fetch == True:
            
                    print("fetch start")
                    print(td_elem.text)
                    if count == 0:
                        room.name = td_elem.text
                        count = count + 1
                    elif count == 1:
                        room.reserved_dept = td_elem.text
                        count = count + 1
                    elif count == 2:
                        room.purpose = td_elem.text
                        count = count + 1
                    elif count == 3:
                        room.date = td_elem.text
                        count = count + 1
                    elif count == 4:
                        room.startTime = td_elem.text
                        count = count + 1
                    elif count == 5:
                        room.endTime = td_elem.text
                        count = count + 1
                    else:
                        room.status = td_elem.text

                        print("name = %s, reserved_dept = %s, purpose = %s, date = %s, startTime = %s, endTime = %s, status = %s" % (room.name, room.reserved_dept, room.purpose, room.date, room.startTime, room.endTime, room.status))

                        meetingRoomArray.append(room)

                        count = 0
                        idx = idx + 1
                        fetch = False


            print("idx = %d" % idx)

            print("meetingRoomArray = %d" % len(meetingRoomArray))

            for i in range(len(meetingRoomArray)):
                print("meetingRoomArray[%d].purpose = %s" % (i, meetingRoomArray[i].purpose))

        else:
            print("Cannot access web. error code: %d" % response.status_code)

    else:
        print("url_file_path not exist")

    print("=== load meeting page end ===")

def find_now_and_next():

    print("=== find_now_and_next start ===")

    global now_idx 
    global next_idx

    now_idx = -1
    next_idx = -1

    if len(meetingRoomArray) > 0:
        
        current_timestamp = datetime.now().timestamp()

        print("current_timestamp = %d" % current_timestamp)

        for i in range(len(meetingRoomArray)):
            room_start_time_string = meetingRoomArray[i].date+" "+meetingRoomArray[i].startTime
            room_end_time_string = meetingRoomArray[i].date+" "+meetingRoomArray[i].endTime
            print("start_time = %s, end_time = %s" % (room_start_time_string, room_end_time_string))
            room_start_timestamp = time.mktime(datetime.strptime(room_start_time_string, "%Y%m%d %H:%M").timetuple())
            room_end_timestamp = time.mktime(datetime.strptime(room_end_time_string, "%Y%m%d %H:%M").timetuple())
            print("current_timestamp=%s, start=%s, end=%s" % (current_timestamp, room_start_timestamp, room_end_timestamp))
            if room_start_timestamp <= current_timestamp and room_end_timestamp >= current_timestamp:
                print("i = %d match!" % i)
                now_idx = i
            
                if i == (len(meetingRoomArray) - 1):
                    print("current meeting is the last meeting today.")
            
            if room_start_timestamp > current_timestamp:

                if next_idx == -1: #current is empty, but next may not be empty
                    next_idx = i
                
    else:
        print("meetingRoomArray.size = 0")


    print("now_idx = %d, next_idx = %d" % (now_idx, next_idx))

    print("=== find_now_and_next end ===")

try:
    logging.info("epd7in5b_HD Demo")

    epd = epd7in5b_HD.EPD()

    logging.info("init and Clear")
    epd.init()
    epd.Clear()

    font48 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 48)
    font32 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 32)
    font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)

    # Drawing on the Horizontal image
    logging.info("1.Drawing on the Horizontal image...")
    #Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    #Other = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    #draw_Himage = ImageDraw.Draw(Himage)
    #draw_other = ImageDraw.Draw(Other)
    
    #draw_Himage.text((10, 0), meetingRoomArray[0].name, font = font48, fill = 0)
    #draw_other.text((180, 77), 'NOW', font = font32, fill = 0)
    #draw_other.text((620, 77), 'NEXT', font = font32, fill = 0)

    
    #draw_Himage.text((10, 20), '7.5inch e-Paper', font = font24, fill = 0)
    #draw_Himage.text((150, 0), u'微雪电子', font = font24, fill = 0)    
    #draw_other.line((20, 50, 70, 100), fill = 0)
    #draw_other.line((70, 50, 20, 100), fill = 0)
    #draw_other.rectangle((20, 50, 70, 100), outline = 0)
    #draw_other.line((165, 50, 165, 100), fill = 0)
    #draw_Himage.line((0, 75, 880, 75), fill = 0)
    #draw_Himage.line((0, 120, 880, 120), fill = 0)
    #draw_Himage.line((440, 75, 440, 528), fill = 0)
    #draw_Himage.arc((140, 50, 190, 100), 0, 360, fill = 0)
    #draw_Himage.rectangle((80, 50, 130, 100), fill = 0)
    #draw_Himage.chord((200, 50, 250, 100), 0, 360, fill = 0)
    #pd.display(epd.getbuffer(Himage),epd.getbuffer(Other))
    
    #current_time = datetime.today().strftime("%2H:%2M")

    first = True
    update = False
    second = 0
    while(True):

        #if first == False:
        #    load_meeting_page()
        #    find_now_and_next()
        #    first = True

        current_time = datetime.today().strftime("%2H:%2M")
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        #second = int(datetime.today().strftime("%2S"))
        minute = datetime.today().strftime("%2M")
        
        #print("current_time = %s, timestamp = %s" % (current_time, timestamp))

        #if second == 0 or first == True:
        if minute == "30" or minute == "00" or first == True:

            if second == 0:

                if first == True:
                    first = False

                load_meeting_page()
                find_now_and_next()

                print("meetingRoomArray size = %d" % len(meetingRoomArray))

                #if len(meetingRoomArray) > 0:

                Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
                Other = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
                draw_Himage = ImageDraw.Draw(Himage)
                draw_other = ImageDraw.Draw(Other)

                print("now_idx = %d, next_idx = %d" % (now_idx, next_idx))

                print("meeting_room_name = %s, meeting_room_title = %s" % (meeting_room_name, meeting_room_title))

                if len(meetingRoomArray) > 0:
                    now_interval = ""
                    next_interval = ""

                    #title
                    if meeting_room_name in meeting_room_title:
                        if meeting_room_title == "" and len(meetingRoomArray[0].name) > 0:
                            meeting_room_title = meetingRoomArray[0].name
                    else:
                    
                        meeting_room_title = ""
                        if len(meetingRoomArray[0].name) > 0:
                            meeting_room_title = meetingRoomArray[0].name
                        else:
                            meeting_room_title = meeting_room_name

                    draw_Himage.text((10, 0), meeting_room_title, font = font48, fill = 0)

                    #if now_idx >= 0: 
                    #    now_interval = "%s - %s" % (meetingRoomArray[now_idx].startTime, meetingRoomArray[now_idx].endTime)
        
                    #now
                    draw_Himage.line((0, 78, 880, 78), fill = 0)
                    draw_Himage.line((0, 120, 880, 120), fill = 0)
                    draw_other.text((420, 80), 'NOW', font = font32, fill = 0)
                    if now_idx >= 0:
                        now_interval = "%s - %s" % (meetingRoomArray[now_idx].startTime, meetingRoomArray[now_idx].endTime)
                        draw_Himage.text((10, 122), meetingRoomArray[now_idx].purpose, font = font32, fill = 0)
                        draw_Himage.text((10, 154), now_interval, font = font32, fill = 0)
                        draw_Himage.text((10, 186), meetingRoomArray[now_idx].reserved_dept, font = font32, fill = 0)
                        draw_other.text((10, 218), meetingRoomArray[now_idx].status, font = font32, fill = 0)
                    else:
                        draw_Himage.text((10, 122), "無會議", font = font32, fill = 0)
                    #next
                    draw_Himage.line((0, 303, 880, 303), fill = 0)
                    draw_Himage.line((0, 345, 880, 345), fill = 0)
                    draw_other.text((420, 305), 'NEXT', font = font32, fill = 0)
                    if next_idx >= 0:
                        next_interval = "%s - %s" % (meetingRoomArray[next_idx].startTime, meetingRoomArray[next_idx].endTime)
                        draw_Himage.text((10, 347), meetingRoomArray[next_idx].purpose, font = font32, fill = 0)
                        draw_Himage.text((10, 379), next_interval, font = font32, fill = 0)
                        draw_Himage.text((10, 411), meetingRoomArray[next_idx].reserved_dept, font = font32, fill = 0)
                        draw_other.text((10, 443), meetingRoomArray[next_idx].status, font = font32, fill = 0)
                        #draw_other.text((180, 77), 'NOW', font = font32, fill = 0)
                        #draw_other.text((620, 77), 'NEXT', font = font32, fill = 0)
                        #draw_Himage.text((10, 123), meetingRoomArray[0].purpose, font = font18, fill = 0)
        
                        #time
        
                        #draw_Himage.text((720, 0), current_time, font = font48, fill = 0)

                        #epd.display(epd.getbuffer(Himage),epd.getbuffer(Other))
                    else:
                        draw_Himage.text((10, 347), "無會議", font = font32, fill = 0)
                    #time
                    #draw_Himage.text((720, 0), current_time, font = font48, fill = 0)
                    epd.display(epd.getbuffer(Himage), epd.getbuffer(Other))

                else: #meetingRoomArray == 0

                    if meeting_room_title == "":
                        meeting_room_title = "會議室 %s " % meeting_room_name
                    

                    print("meetingRoomArray size = 0")    
                    draw_Himage.text((10, 0), meeting_room_title, font = font48, fill = 0)
                    #now
                    draw_Himage.line((0, 78, 880, 78), fill = 0)
                    draw_Himage.line((0, 120, 880, 120), fill = 0)
                    draw_other.text((420, 80), 'NOW', font = font32, fill = 0)
                    draw_Himage.text((10, 122), "無會議", font = font32, fill = 0)
                    #next
                    draw_Himage.line((0, 303, 880, 303), fill = 0)
                    draw_Himage.line((0, 345, 880, 345), fill = 0)
                    draw_other.text((420, 305), 'NEXT', font = font32, fill = 0)
                    draw_Himage.text((10, 347), "無會議", font = font32, fill = 0)
                    #time
                    #draw_Himage.text((720, 0), current_time, font = font48, fill = 0)
                    epd.display(epd.getbuffer(Himage), epd.getbuffer(Other))
            
                


            second = second + 1
        else:
            second = 0
        #if second == 60:
        #    second = 0

        sleep(1)

    #time.sleep(2)

    # Drawing on the Vertical image
    #logging.info("2.Drawing on the Vertical image...")
    #Limage = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    #Limage_Other = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    #draw_Himage = ImageDraw.Draw(Limage)
    #draw_Himage_Other = ImageDraw.Draw(Limage_Other)
    #draw_Himage.text((2, 0), 'hello world', font = font18, fill = 0)
    #draw_Himage.text((2, 20), '7.5inch epd', font = font18, fill = 0)
    #draw_Himage_Other.text((20, 50), u'微雪电子', font = font18, fill = 0)
    #draw_Himage_Other.line((10, 90, 60, 140), fill = 0)
    #draw_Himage_Other.line((60, 90, 10, 140), fill = 0)
    #draw_Himage_Other.rectangle((10, 90, 60, 140), outline = 0)
    #draw_Himage_Other.line((95, 90, 95, 140), fill = 0)
    #draw_Himage.line((70, 115, 120, 115), fill = 0)
    #draw_Himage.arc((70, 90, 120, 140), 0, 360, fill = 0)
    #draw_Himage.rectangle((10, 150, 60, 200), fill = 0)
    #draw_Himage.chord((70, 150, 120, 200), 0, 360, fill = 0)
    #epd.display(epd.getbuffer(Limage), epd.getbuffer(Limage_Other))
    #time.sleep(2)
    
    #logging.info("3.read bmp file...")
    #blackimage = Image.open(os.path.join(picdir, '7in5_HD_b.bmp'))
    #redimage = Image.open(os.path.join(picdir, '7in5_HD_r.bmp'))    
    #epd.display(epd.getbuffer(blackimage),epd.getbuffer(redimage))
    #time.sleep(1)

    #logging.info("4.read bmp file on window")
    #Himage2 = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    #Himage2_Other = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    #bmp = Image.open(os.path.join(picdir, '100x100.bmp'))
    #Himage2.paste(bmp, (50,10))
    #Himage2_Other.paste(bmp, (50,300))
    #epd.display(epd.getbuffer(Himage2), epd.getbuffer(Himage2_Other))
    #time.sleep(2)

    #logging.info("Clear...")
    #epd.init()
    #epd.Clear()

    #logging.info("Goto Sleep...")
    #epd.sleep()
    
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd7in5b_HD.epdconfig.module_exit()
    exit()
