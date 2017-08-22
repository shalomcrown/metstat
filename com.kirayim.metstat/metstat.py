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

        Button(frame, text="QUIT", fg="red", command=frame.quit).grid(row=3, column=1)
        Button(frame, text="Enter token", command=self.enter_token).grid(row=3, column=2)

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
                recordsThisTime = result['metadata']['resultset']['limit']
                startRecord = result['metadata']['resultset']['offset'] + recordsThisTime
                
                for item in result['results']:
                    yield item
                
            else:
                yield result
                return

    # ========================================

    def get_cities(self):
        for cityData in self.get_all_data('locations?locationcategoryid=CITY&sortfield=name&sortorder=desc'):
            self.cities[cityData['name']] = cityData
            self.cityCombo['values'] = self.cities.keys()



if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG, format ='[%(levelname)s] %(asctime)s  %(filename)s(%(lineno)d)  %(funcName)s %(message)s')    
    root = Tk()
    app = MetApp(root)
    root.mainloop()
    root.destroy()
