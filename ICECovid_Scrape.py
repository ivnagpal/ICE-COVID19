#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import re
import os
import pandas as pd 
from bs4 import BeautifulSoup
import datetime

#Date and Time of Program
dt = datetime.datetime.now().strftime('%m/%d/%y')


#Scrape ICE website for detainee COVID-19 infections
url = 'https://www.ice.gov/coronavirus#wcm-survey-target-id'
response = requests.get(url) 
soup = BeautifulSoup(response.text, 'lxml') 
td_list = soup.findAll ('td')
td_list_txt = [txt.get_text() for txt in td_list]
beg_ind = td_list_txt.index ('Atlanta Field Office') + 1
end_ind = td_list_txt.index ('TOTAL')
covid_detain = td_list_txt [beg_ind:end_ind]

#ICE Last Update
p_list = soup.findAll ('p')
p_list_txt = [txt.get_text() for txt in p_list]
staff_update = p_list_txt[106].replace('Updated','').strip()
detainee_update = p_list_txt[109].replace('Updated','').strip()
staff_update_string = 'ICE Employee Data Last Updated on' + ' ' + staff_update
detainee_update_string = 'ICE Detainee Data Last Updated on:' + ' ' + detainee_update
print (staff_update_string)
print (detainee_update_string)


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

#Dictionary of detainee COVID19 infections
imm_covid = {'Custody/AOR/Facility': custody_facility,
             dt + ':Confirmed cases currently under isolation or monitoring':covid_current,
             dt + ':Detainee deaths':covid_deaths, dt + ':Total confirmed COVID-19 cases':covid_total}

#DF of detainee COVID19 infections
imm_df = pd.DataFrame(imm_covid) #Df for detainee covid19

#Scrape ICE website for staff COVID-19 infections
li_list = soup.findAll ('li')
li_list_txt = [txt.get_text() for txt in li_list]
beg_inx = li_list_txt.index ('Optional COVID-19 School Reporting Template that schools can use to report temporary procedural adaptations (Mar. 2020)') + 1
end_inx = li_list_txt.index ('a 24-year-old Guatemalan national at La Palma Correctional Center in Arizona')
covid_staff = li_list_txt [beg_inx:end_inx]
covid_staff = [ele.replace ('at','') for ele in covid_staff]
covid_staff = [ele.replace ('in','') for ele in covid_staff]

#Extract number of staff COVID19 infections
staff_len = len (covid_staff)
staff_covid_list = []
for ele in range (staff_len):
    staff_covid_list.append([int(s) for s in covid_staff[ele].split() if s.isdigit()])

staff_covid = []
for ele in staff_covid_list:
    for x in ele:
        staff_covid.append (str(x))
        
#Extract facility of staff COVID19 infections
staff_det_1 = []
for ele in covid_staff:
    staff_det_1.append (''.join(i for i in ele if not i.isdigit()))

staff_det = []
for ele in staff_det_1:
    staff_det.append (re.sub(r" ?\([^)]+\)", "", ele))
staff_det = [ele.strip() for ele in staff_det]
staff_det = staff_det[3:]
staff_covid = staff_covid [1:]

#Dictionary of Staff COVID19 infections
staffdic_covid = {'Custody/AOR/Facility':staff_det,
             dt + ':Staff Confirmed Cases':staff_covid}

#DF of Staff COVID19 infections
staff_df = pd.DataFrame(staffdic_covid)

#Changing name of detention facilities to conform with imm_df
staff_df = staff_df.replace ('Adelanto ICE Processg Center','Adelanto ICE Processing Center')
staff_df = staff_df.replace ('Alexandria Stagg Facility','Alexandria Staging Facility')
staff_df = staff_df.replace ('El Paso Processg Center','El Paso Service Processing Center')
staff_df = staff_df.replace ('Elizabeth Contract Detention Facility','Elizabeth Detention Center')
staff_df = staff_df.replace ('Eloy Detention Center','Eloy Federal Contract Facility')
staff_df = staff_df.replace ('Essex County Correctional Facility','Essex County Jail')
staff_df = staff_df.replace ('Florence Correctional Center','Florence Detention Center')
staff_df = staff_df.replace ('Otay Mesa Detention Center','Otay Mesa Detention Center (San Diego CDF)')
staff_df = staff_df.replace ('La Salle ICE Processg Center','LaSalle ICE Processing Center - Jena')


#Merging Staff and Detainee DF
immfinal_df = pd.merge(imm_df, staff_df, how= 'outer', on= 'Custody/AOR/Facility')
immfinal_df [[dt + ':Confirmed cases currently under isolation or monitoring',dt + ':Detainee deaths'
              ,dt + ':Total confirmed COVID-19 cases',dt + ':Staff Confirmed Cases']] = immfinal_df [[dt + ':Confirmed cases currently under isolation or monitoring',dt + ':Detainee deaths'
              ,dt + ':Total confirmed COVID-19 cases',dt + ':Staff Confirmed Cases']].apply(pd.to_numeric)
                                                                                       
#Detention with maximum cases
max_confirm = dt + ':Confirmed cases currently under isolation or monitoring'                                                                          
curr_max = immfinal_df[max_confirm].max()
curr_max_fac = immfinal_df.loc[immfinal_df[dt + ':Confirmed cases currently under isolation or monitoring'] == curr_max]
curr_max_fac = curr_max_fac ['Custody/AOR/Facility'].item()
print ('Facility with most current confirmed detainee cases:',curr_max_fac,'w/',curr_max,"cases")

detdeath_max = immfinal_df[dt + ':Detainee deaths'].max()
death_max_fac = immfinal_df.loc[immfinal_df[dt + ':Detainee deaths'] == detdeath_max]
death_max_fac = death_max_fac ['Custody/AOR/Facility']
for ele in death_max_fac:
    print ('Facility with most detainee deaths:',ele,'w/',detdeath_max,"death/s")

dettot_max = immfinal_df[dt + ':Total confirmed COVID-19 cases'].max()
dettot_max_fac = immfinal_df.loc[immfinal_df[dt + ':Total confirmed COVID-19 cases'] == dettot_max]
dettot_max_fac = dettot_max_fac ['Custody/AOR/Facility'].item()
print ('Facility with most total confirmed detainee cases:',dettot_max_fac,'w/', dettot_max,"cases")


staffcon_max = immfinal_df[dt + ':Staff Confirmed Cases'].max()
staffcon_max_fac = immfinal_df.loc[immfinal_df[dt + ':Staff Confirmed Cases'] == staffcon_max]
staffcon_max_fac = staffcon_max_fac ['Custody/AOR/Facility'].item()
print ('Facility with most staff cases:',staffcon_max_fac,'w/',staffcon_max,"cases")

#Create CSV File of Updated ICE COVID19 Data
df = pd.read_csv('imm_df.csv') 
immfinal_df= pd.merge(df, immfinal_df, on='Custody/AOR/Facility', how='right')
path = os.getcwd() + '/imm_df.csv'
immfinal_df.to_csv (path, index = False, header=True)



