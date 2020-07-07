#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import re
import pandas as pd 
from bs4 import BeautifulSoup

#Scrape ICE detainee COVID-19 Infections
url = 'https://www.ice.gov/coronavirus#wcm-survey-target-id'
response = requests.get(url) 
soup = BeautifulSoup(response.text, 'lxml') 
td_list = soup.findAll ('td')
td_list_txt = [txt.get_text() for txt in td_list]
beg_ind = td_list_txt.index ('Atlanta Field Office') + 1
end_ind = td_list_txt.index ('TOTAL')
covid_detain = td_list_txt [beg_ind:end_ind]


#Remove "Field Office" Headers
field_office = ['Atlanta Field Office','Baltimore Field Office','Boston Field Office','Buffalo Field Office',
                'Chicago Field Office','Dallas Field Office','Denver Field Office',
                'Detroit Field Office','El Paso Field Office','Houston Field Office',
                'Los Angeles Field Office','Miami Field Office','Newark Field Office',
                'New Orleans Field Office','New York City Field Office','Philadelphia Field Office',
                'Phoenix Field Office','Salt Lake City Field Office','San Antonio Field Office',
                'San Diego Field Office','San Francisco Field Office','Seattle Field Office',
                'St. Paul Field Office','Washington D.C. Field Office']


covid_detain = [ele for ele in covid_detain if ele not in field_office]

#Create COVID infection dataframe
custody_facility = covid_detain[0::4]
covid_current = covid_detain[1::4]
covid_deaths = covid_detain[2::4]
covid_total = covid_detain[3::4]

imm_covid = {'Custody/AOR/Facility': custody_facility,
             'Confirmed cases currently under isolation or monitoring':covid_current,
             'Detainee deaths':covid_deaths,'Total confirmed COVID-19 cases':covid_total}

imm_df = pd.DataFrame(imm_covid) #Df for detainee covid19

#Scrape ICE Employee COVID-19 Infections
li_list = soup.findAll ('li')
li_list_txt = [txt.get_text() for txt in li_list]
beg_inx = li_list_txt.index ('Frequently Asked Questions about Fall 2020 Semester Guidance') + 1
end_inx = li_list_txt.index ('a 24-year-old Guatemalan national at La Palma Correctional Center in Arizona')
covid_staff = li_list_txt [beg_inx:end_inx]
covid_staff = [ele.replace ('at','') for ele in covid_staff]
covid_staff = [ele.replace ('in','') for ele in covid_staff]

#Extract number of COVID infections
staff_len = len (covid_staff)
staff_covid_list = []
for ele in range (staff_len):
    staff_covid_list.append([int(s) for s in covid_staff[ele].split() if s.isdigit()])

staff_covid = []
for ele in staff_covid_list:
    for x in ele:
        staff_covid.append (str(x))
        
#Extract location of COVID infections
staff_det_1 = []
for ele in covid_staff:
    staff_det_1.append (''.join(i for i in ele if not i.isdigit()))

staff_det = []
for ele in staff_det_1:
    staff_det.append (re.sub(r" ?\([^)]+\)", "", ele))
staff_det = [ele.strip() for ele in staff_det]

#Create Staff infection Dataframe
staff_covid = {'Custody/AOR/Facility': staff_det,
             'Staff Confirmed Cases':staff_covid}

staff_df = pd.DataFrame(staff_covid) #Df for staff covid19

#Print Staff and Inmate COVID19 cases
print (imm_df)
print (staff_df)
