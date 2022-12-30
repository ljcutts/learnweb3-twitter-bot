import snscrape.modules.twitter as sntwitter
import pandas as pd
from os.path import exists
from openpyxl import load_workbook
import glob
import datetime

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
time = "{}".format((datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day))
hashTable = {}
term = '@LearnWeb3DAO'
# Created a list to append all tweet attributes(data)
attributes_container = []
#Using TwitterSearchScraper to scrape data and append tweets to list
if file_exists is False: 
 for i,tweet in enumerate(sntwitter.TwitterSearchScraper('100DaysOfCode LearnWeb3DAO').get_items()):
    if i>1000:
        break
    input = tweet.content.split()
    if term in input and tweet.date.day == datetime.datetime.now().day:   
     attributes_container.append([(tweet.date.year,tweet.date.month, tweet.date.day), tweet.user.username, tweet.content, 1])  
# Creating a dataframe from the tweets list above 
 tweets_df = pd.DataFrame(attributes_container, columns=["Date Created", "Username", "Tweets", "DaysOfCoding"])
 tweets_df.to_excel('lw3Tweets.xlsx', header=True, index=False)
else:
  for i,tweet in enumerate(sntwitter.TwitterSearchScraper('100DaysOfCode LearnWeb3DAO').get_items()):
    if i>1000:
        break
    notPresent = tweet.user.username in nameValues
    input = tweet.content.split()
    statement = term in input and (notPresent is False) 
    usernameArray.append(tweet.user.username)
    hashTable[tweet.user.username] = tweet.content
    if statement:
     attributes_container.append([(tweet.date.year,tweet.date.month, tweet.date.day), tweet.user.username, tweet.content, 0])  
     tweets_df2 = pd.DataFrame(attributes_container, columns=["Date Created", "Username", "Tweets", "DaysOfCoding"])
     with pd.ExcelWriter("lw3Tweets.xlsx",mode="a",engine="openpyxl",if_sheet_exists="overlay") as writer:
      tweets_df2.to_excel(writer, sheet_name="Sheet1",header=None, startrow=writer.sheets["Sheet1"].max_row,index=False)  


df = pd.read_excel('lw3Tweets.xlsx')
df2 = df.filter(items=['Username'])
counter = 0


if file_exists is True:
 for value in df2.values:
  if value in usernameArray:
   value = df['DaysOfCoding'][counter]
   df['DaysOfCoding'][counter] = value if df['Date Created'][counter] == time else value + 1
   df['Date Created'][counter] = (datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)
   name = df2.values[counter][0]
   df['Tweets'][counter] = hashTable[name]
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


#Update an excel on google using Python
#Channel where others can see the excel sheet
#Maybe automate code to run every 2-6 hours