#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Created on Fri Aug 11 09:46:54 2017

@author: shalom
"""

# Email:	shalomcrown@gmail.com
# https://www.ncdc.noaa.gov/cdo-web/api/v2/locations?locationcategoryid=CITY&sortfield=name&sortorder=desc

# matplotlib

from Tkinter import *
import tkMessageBox
import ttk
import httplib
import os
import json
import logging
import threading
import sqlite3
import time
import calendar
import datetime


ISODATESTRING = "%Y-%m-%d"

class TokenDialog:
    def __init__(self, parent):
        top = self.top = Toplevel(parent)
        Label(top, text="Enter SPI token").pack()
        Button(top, text="OK", command=self.ok)

    def ok(self):
        pass

        # =====================================


class DateWidget(Frame):
    def __init__(self, parent, start = datetime.date.today()):
        Frame.__init__(self, parent)
        self.yearVar = StringVar(self)
        self.monthVar = StringVar(self)
        self.dayVar = StringVar(self)
        self.cal = calendar.Calendar()
        now = datetime.date.today()
        
        self.yearVar.set(str(start.year))
        self.monthVar.set(str(start.month))
        self.dayVar.set(str(start.day))
        
        self.yearCombo = ttk.Combobox(master=self, textvariable=self.yearVar, values=[str(a) for a in range(1900, now.year)])
        self.yearCombo.bind("<<ComboboxSelected>>", self.setMonthDays)
        self.yearCombo.pack(side=LEFT)
        
        self.monthCombo = ttk.Combobox(master=self, textvariable=self.monthVar, values=[str(a) for a in range(1, 12)])
        self.monthCombo.bind("<<ComboboxSelected>>", self.setMonthDays)
        self.monthCombo.pack(side=LEFT)
        
        self.dayCombo = ttk.Combobox(master=self, textvariable=self.dayVar)
        self.setMonthDays()
        self.dayCombo.pack(side=LEFT)
        
    def setMonthDays(self, what=0):
        values=[str(a) for a in self.cal.itermonthdays(int(self.yearVar.get()), int(self.monthVar.get())) if a != 0]
        self.dayCombo['values'] = values
        
    def getDate(self):
        return datetime.date(int(self.yearVar.get()), int(self.monthVar.get()), int(self.dayVar.get()))

#--------------------------------------------------------------------------------------------


class MetApp:

    def load_token(self):
        tokenfile = os.path.expanduser('~/.metstat/token')
        if not os.path.exists(tokenfile):
            tkMessageBox.showerror("Metstat", "No toke file found for NOAA\nPlease visit https://www.ncdc.noaa.gov/cdo-web/token\n    and obtain one")
            return

        with open(tokenfile) as fl:
            self.token = fl.read().strip()

    def __init__(self, master):
        self.cities = {}
        self.token = None
        master.title('MetStat')
        frame = Frame(master)
        frame.pack()
        Label(frame, text="Location:").grid(row=0, column=1, columnspan=6)
        Label(frame, text="Lat:").grid(row=1, column=1, sticky=E)
        self.latVar = StringVar(master)
        self.latVar.set("32.868")
        Entry(frame, textvariable=self.latVar).grid(row=1, column=2)
        self.lonVar = StringVar(master)
        self.lonVar.set("34.555")
        Label(frame, text="Lon:").grid(row=1, column=3, sticky=E)
        Entry(frame, textvariable=self.lonVar).grid(row=1, column=4)

        Label(frame, text="Cities").grid(row=2, column=1)
        self.cityVar = StringVar(master)
        self.cityCombo = ttk.Combobox(master=frame, textvariable=self.cityVar)
        self.cityCombo.grid(row=2, column=2, sticky=W+E)
        Button(frame, text="Get cities", command=self.get_cities).grid(row=2, column=3, sticky=W+E)
        
        
        Label(frame, text="Datasets").grid(row=3, column=1)
        self.categoryVar = StringVar(master)
        self.categories = {}
        self.categoryCombo = ttk.Combobox(master=frame, textvariable=self.categoryVar)
        self.categoryCombo.grid(row=3, column=2, sticky=W+E)
        Button(frame, text="Get datasets", command=self.get_city_categories).grid(row=3, column=3, sticky=W+E)
        
        Button(frame, text="Get data", command=self.get_city_data).grid(row=3, column=4, sticky=W+E)
        
        Label(frame, text="From").grid(row=4, column=1)
        self.fromDate = DateWidget(frame)
        self.fromDate.grid(row=4, column=2)
        
        Label(frame, text="To").grid(row=5, column=1)
        self.toDate = DateWidget(frame)
        self.toDate.grid(row=5, column=2)
        
        Button(frame, text="QUIT", fg="red", command=frame.quit).grid(row=11, column=1)
        Button(frame, text="Enter token", command=self.enter_token).grid(row=11, column=2)

        self.progressBar = ttk.Progressbar(frame, mode='determinate')
        self.progressBar.grid(row=12, column=0, columnspan=6, sticky=W+E)
        self.dbPath = os.path.expanduser('~/.metstat/db')
        
        self.readCitiesFromDb()
        self.load_token()

    # =====================================

    def readCitiesFromDb(self):
        conn = sqlite3.connect(self.dbPath)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS CITIES (MINDATE TEXT, MAXDATE TEXT, NAME TEXT, DATACOVERAGE INTEGER, ID TEXT PRIMARY KEY)")
        cursor.execute("CREATE TABLE IF NOT EXISTS DAILY_SUMMARY (DATE TEXT, STATION TEXT, PRCP INTEGER, TMAX INTEGER, TMIN INTEGER, TAVG INTEGER, PRIMARY KEY (STATION, DATE) )")
        conn.commit()
        
        cursor.execute("SELECT * FROM CITIES")
        for row in cursor:
            cityData = {'mindate':row[0], 'maxdate':row[1], 'name':row[2], 'datacoverage':row[3], 'id':row[4]}
            self.cities[cityData['name']] = cityData
            
            if cityData['name'].startswith("Tel Aviv"):
                self.cityVar.set(cityData['name'])

        self.cityCombo['values'] = sorted(self.cities.keys())
            
        
    #--------------------------------------------------------------------------------------------

    def enter_token(self):
        tkMessageBox.showinfo("MetStat", "Use mine for now")

    def doGet(self, path, parameters=None):
        connection = httplib.HTTPSConnection("www.ncdc.noaa.gov")

        url = "/cdo-web/api/v2/" + path

        if parameters is not None:
            pass


        logging.debug("GET: " + url)

        print "GET: ", url
        connection.request("GET", url, headers={"token" : self.token})
        response = connection.getresponse()
        data = response.read();
        status = response.status

        logging.debug("Response code {}, data:\n{}".format(response, data))
        return data, status

    #--------------------------------------------------------------------------------------------



    def get_all_data(self, baseUrl, blocksize=100):
        recordsRemaining = None # unknown for now
        startRecord = 0
        
        while recordsRemaining is None or recordsRemaining > 0:
            url = "{}&offset={}&limit={}".format(baseUrl, startRecord, blocksize)
            data, status = self.doGet(url)
            
            if status > 299:
                raise Exception("GET failed")
            
            result = json.loads(data)
            
            if result['metadata']:
                totalRecords = result['metadata']['resultset']['count']
                
                if recordsRemaining is None:
                    self.progressBar['maximum'] = totalRecords
                    
                recordsThisTime =len(result['results'])
                startRecord = result['metadata']['resultset']['offset'] + recordsThisTime
                recordsRemaining = totalRecords - startRecord
                self.progressBar.step(recordsThisTime)
                
                for item in result['results']:
                    yield item
                
            else:
                yield result
                return

    # ========================================

    def get_cities_thread(self):
        conn = sqlite3.connect(self.dbPath)
        cursor = conn.cursor()
        #{"mindate":"1927-02-01","maxdate":"2017-08-22","name":"Destin, FL US","datacoverage":1,"id":"CITY:US120011"
        
        for cityData in self.get_all_data('locations?locationcategoryid=CITY&sortfield=name&sortorder=desc'):
            self.cities[cityData['name']] = cityData
            self.cityCombo['values'] = sorted(self.cities.keys())
            cursor.execute("INSERT OR REPLACE INTO CITIES VALUES (?, ?, ?, ?, ?)", (
                           cityData['mindate'],
                           cityData['maxdate'],
                           cityData['name'],
                           cityData['datacoverage'],
                           cityData['id']
                           ))
            
            if cityData['name'].startswith("Tel Aviv"):
                self.cityVar.set(cityData['name'])

        conn.commit()
        conn.close()
        

    def get_cities(self):
        threading.Thread(target=self.get_cities_thread).start()


    #--------------------------------------------------------------------------------------------

    def getDataCategoriesThread(self, locationId):
        for categoryData in self.get_all_data("datasets?datatypeid=TOBS&locationId=" + locationId):
            categoryName = "{} {} {}".format(categoryData['name'], categoryData['mindate'], categoryData['maxdate'])
            self.categories[categoryName] = categoryData
            self.categoryCombo['values'] = sorted(self.categories.keys())
        self.categoryVar.set(self.categories.keys()[0])


    def getDataCategories(self, locationId):
        threading.Thread(target=self.getDataCategoriesThread, args=(locationId,)).start()

    def get_city_categories(self):
        cityName = self.cityVar.get()
        cityData = self.cities[cityName]
        self.getDataCategories(cityData['id'])
        
    #--------------------------------------------------------------------------------------------

    def getDataThread(self, locationId, categoryUID, startDate, endDate):
        for data in self.get_all_data("data?datasetid={}&locationid={}&startdate={}&enddate={}".format(categoryUID, locationId, startDate, endDate)):
            
            print data


    def getData(self, locationId, categoryUID, startDate, endDate):
        threading.Thread(target=self.getDataThread, args=(locationId, categoryUID, startDate, endDate)).start()
        

        
        eaxmpleData= [{
                        "date": "2015-09-01T00:00:00",
                        "datatype": "PRCP",
                        "station": "GHCND:ISE00105694",
                        "attributes": ",,S,",
                        "value": 0
                    },
                    {
                        "date": "2015-09-01T00:00:00",
                        "datatype": "TAVG",
                        "station": "GHCND:ISE00105694",
                        "attributes": "H,,S,",
                        "value": 286
                    },
                    {
                        "date": "2015-09-01T00:00:00",
                        "datatype": "TMAX",
                        "station": "GHCND:ISE00105694",
                        "attributes": ",,E,",
                        "value": 331
                    },
                    {
                        "date": "2015-09-01T00:00:00",
                        "datatype": "TMIN",
                        "station": "GHCND:ISE00105694",
                        "attributes": ",,E,",
                        "value": 246
                    }]
        


    def get_city_data(self):
        cityName = self.cityVar.get()
        cityData = self.cities[cityName]        
        categoryName = self.categoryVar.get()
        category = self.categories[categoryName]
        fromDate = self.fromDate.getDate()
        toDate = self.toDate.getDate()
        self.getData(cityData['id'], category['id'], fromDate.strftime(ISODATESTRING), toDate.strftime(ISODATESTRING))

    #--------------------------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG, format ='[%(levelname)s] %(asctime)s  %(filename)s(%(lineno)d)  %(funcName)s %(message)s')    
    root = Tk()
    app = MetApp(root)
    root.mainloop()
