import requests
import numpy as np
import re
import os
import pandas as pd 
from bs4 import BeautifulSoup
import datetime

#DATA SCRAIPING
#Date and Time of Program
dt = datetime.datetime.now().strftime('%m/%d/%y')

#Parse ICE Website
url = 'https://www.ice.gov/coronavirus#wcm-survey-target-id'
response = requests.get(url) 
soup = BeautifulSoup(response.text, 'lxml') 

#Information on latest ICE Update
p_list = soup.findAll ('p')
p_list_txt = [txt.get_text() for txt in p_list]
detainee_update = p_list_txt[123].replace('Updated','').strip()
detainee_update_string = 'ICE Detainee Data Last Updated on:' + ' ' + detainee_update
print (detainee_update_string)


#Scrape for detainee COVID infections
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
                'St. Paul Field Office','Washington D.C. Field Office','Endeavors 5']


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
immfinal_df = pd.DataFrame(imm_covid) #Df for detainee covid19

#Create CSV File of Updated ICE COVID19 Data w/ Historical Data
df = pd.read_csv('imm_df.csv') 
immfinal_df= pd.merge(df, immfinal_df, on='Custody/AOR/Facility', how='outer')
columns = immfinal_df.columns.tolist()
columns.remove('Custody/AOR/Facility')
columns_r = columns[::-1]
columns_r.insert(0,'Custody/AOR/Facility')
immfinal_dfr = immfinal_df[columns_r]

# CSV File Time Ascending 
path = os.getcwd() + '/imm_df.csv'
immfinal_df.to_csv (path, index = False, header=True)

# CSV File Time Descending
path2 = os.getcwd() + '/immdet_df.csv'
immfinal_dfr.to_csv (path2, index = False, header=True)






