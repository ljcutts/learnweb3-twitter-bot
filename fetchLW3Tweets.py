import snscrape.modules.twitter as sntwitter
import pandas as pd
from os.path import exists
import glob
import json
with open('mdrive.json') as f:
 data = json.load(f)
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from df2gspread import df2gspread as d2g
import schedule
import time
from keep_alive import keep_alive

t = time.time()
day = time.strftime('%d', time.gmtime(t))
month = time.strftime('%m', time.gmtime(t))
year = time.strftime('%Y', time.gmtime(t))
current_time = "{}".format((int(year), int(month), int(day)))

keep_alive()
def fetch_tweets():
 file_exists = exists('lw3Tweets.xlsx')
 usernameArray = []
 if file_exists is True:
     df = pd.read_excel('lw3Tweets.xlsx')
     df2=df.filter(items=['Username'])
     df3=df.filter(items=['Tweets'])
     nameValues = []
     for value in df2.values:
       nameValues.append(value[0])

 for file in glob.glob('./*.xlsx'):
     if '~$' in file:
         continue
     else:
         df = pd.read_excel(
             file,
             engine='openpyxl'
         )
 hashTable = {}
 # Created a list to append all tweet attributes(data)
 attributes_container = []
 #Using TwitterSearchScraper to scrape data and append tweets to list
 if file_exists is False: 
  for i,tweet in enumerate(sntwitter.TwitterSearchScraper('100DaysOfCode LearnWeb3DAO').get_items()):
     if i>100000:
         break
     if tweet.date.day == int(day) and tweet.date.month == int(month) and tweet.date.year == int(year):  
      attributes_container.append([(tweet.date.year,tweet.date.month, tweet.date.day), tweet.user.username, tweet.content, tweet.url, 1])  
 # Creating a dataframe from the tweets list above 
  tweets_df = pd.DataFrame(attributes_container, columns=["Date Created", "Username", "Tweets", "Link", "DaysOfCoding"])
  tweets_df.to_excel('lw3Tweets.xlsx', header=True, index=False)
 else:
   for i,tweet in enumerate(sntwitter.TwitterSearchScraper('100DaysOfCode LearnWeb3DAO').get_items()):
     if i>100000:
         break
     notPresent = tweet.user.username in nameValues
     statement = (notPresent is False) and tweet.date.day == int(day) and tweet.date.month == int(month) and tweet.date.year == int(year)
     if tweet.date.day == int(day) and tweet.date.month == int(month) and tweet.date.year == int(year):
       usernameArray.append(tweet.user.username)
       hashTable[tweet.user.username] = [tweet.content, tweet.url]
     if statement:
      attributes_container.append([(tweet.date.year,tweet.date.month, tweet.date.day), tweet.user.username, tweet.content, tweet.url, 1])  
      tweets_df2 = pd.DataFrame(attributes_container, columns=["Date Created", "Username", "Tweets", "Link", "DaysOfCoding"])
      with pd.ExcelWriter("lw3Tweets.xlsx",mode="a",engine="openpyxl",if_sheet_exists="overlay") as writer:
       tweets_df2.to_excel(writer, sheet_name="Sheet1",header=None, startrow=writer.sheets["Sheet1"].max_row,index=False)  

 df = pd.read_excel('lw3Tweets.xlsx')
 df2 = df.filter(items=['Username'])
 counter = 0

 if file_exists is True:
  for value in df2.values:
   if value in usernameArray:
    value = df['DaysOfCoding'][counter]
    df['DaysOfCoding'][counter] = value if df['Date Created'][counter] == current_time else value + 1
    name = df2.values[counter][0]
    df['Tweets'][counter] = hashTable[name][0]
    df['Link'][counter] = hashTable[name][1]
    df['Date Created'][counter] = current_time
    df.to_excel('lw3Tweets.xlsx', sheet_name="Sheet1", header=True, index=False)
   counter = counter + 1

 counter = 0
 usernameArray = []
 hashTable = {}

 df = pd.DataFrame(pd.read_excel('lw3Tweets.xlsx'))
 df.drop_duplicates(subset=['Username'], inplace=True)
 df.to_excel('lw3Tweets.xlsx', sheet_name="Sheet1", header=True, index=False)
 df.sort_values(by="DaysOfCoding", inplace=True, ascending=False)
 df.to_excel('lw3Tweets.xlsx', sheet_name="Sheet1", header=True, index=False)

# use creds to create a client to interact with the Google Drive API
 scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive','https://www.googleapis.com/auth/drive.file','https://www.googleapis.com/auth/spreadsheets']
 creds = ServiceAccountCredentials.from_json_keyfile_name('mdrive.json', scope)
 client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
# Make sure you use the right name here.
 sheet = client.open("Learnweb3-100DaysOfCode-Leaderboard").sheet1
 spreadsheet_key = '1ifq06TD9qtnrSM5psbPAENktSXRM60RGUOtmDrMJgvk'

 wks_name = 'Sheet1'
 cell_of_start_df = 'A1'
 d2g.upload(df,
       spreadsheet_key,
       wks_name,
       credentials=creds,
       col_names=True,
       row_names=True,
       start_cell = cell_of_start_df,
       clean=False)
  
schedule.every(1).minutes.do(fetch_tweets)
  
while True:
    schedule.run_pending()
    time.sleep(1)