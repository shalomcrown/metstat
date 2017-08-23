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


class TokenDialog:
    def __init__(self, parent):
        top = self.top = Toplevel(parent)
        Label(top, text="Enter SPI token").pack()
        Button(top, text="OK", command=self.ok)

    def ok(self):
        pass

        # =====================================


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
        self.cityCombo.grid(row=2, column=2)
        Button(frame, text="Get cities", command=self.get_cities).grid(row=2, column=3)
        
        
        Label(frame, text="Datasets").grid(row=3, column=1)
        self.categoryVar = StringVar(master)
        self.categories = {}
        self.categoryCombo = ttk.Combobox(master=frame, textvariable=self.categoryVar)
        self.categoryCombo.grid(row=3, column=2)
        Button(frame, text="Get datasets", command=self.get_city_categories).grid(row=3, column=4)
        
        Button(frame, text="QUIT", fg="red", command=frame.quit).grid(row=8, column=1)
        Button(frame, text="Enter token", command=self.enter_token).grid(row=8, column=2)

        self.progressBar = ttk.Progressbar(frame, mode='determinate')
        self.progressBar.grid(row=9, column=0, columnspan=6, sticky=W+E)

        self.load_token()

    # =====================================

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
        for cityData in self.get_all_data('locations?locationcategoryid=CITY&sortfield=name&sortorder=desc'):
            self.cities[cityData['name']] = cityData
            self.cityCombo['values'] = sorted(self.cities.keys())
        

    def get_cities(self):
        threading.Thread(target=self.get_cities_thread).start()


    #--------------------------------------------------------------------------------------------

    def getDataCategoriesThread(self, locationId):
        for categoryData in self.get_all_data("datasets?datatypeid=TOBS&locationId=" + locationId, blocksize):
            categoryName = "{} {} {}".format(categoryData['name'], categoryData['mindate'], categoryData['maxDate'])
            self.categories[categoryName] = categoryData
            self.categoryCombo['values'] = sorted(self.categories.keys())


    def getDataCategories(self, locationId):
        threading.Thread(target=self.getTempDataThread, args=(locationId))

    #--------------------------------------------------------------------------------------------

    def get_city_categories(self):
        cityName = self.cityVar.get()
        cityData = self.cities[cityName]
        self.getDataCategories(cityData['id'])



    #--------------------------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG, format ='[%(levelname)s] %(asctime)s  %(filename)s(%(lineno)d)  %(funcName)s %(message)s')    
    root = Tk()
    app = MetApp(root)
    root.mainloop()
    root.destroy()
