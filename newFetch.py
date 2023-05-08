import pandas as pd
from os.path import exists
import glob
import time
import json
with open('/Users/user/Desktop/Intro-to-Ethereum-Programming/nodejs-twitter-bot/mdrive.json') as f:
 data = json.load(f)
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from df2gspread import df2gspread as d2g
import requests


t = time.time()
day = time.strftime('%d', time.gmtime(t))
month = time.strftime('%m', time.gmtime(t))
year = time.strftime('%Y', time.gmtime(t))
current_time = "{}".format((2023, 5, 7))

endpointUrl = "https://api.twitter.com/2/tweets/search/recent"
tweetLookupEndpoint = "https://api.twitter.com/2/users"

bearer_token = ""

file_exists = exists('/Users/user/Desktop/Intro-to-Ethereum-Programming/nodejs-twitter-bot/lw3Tweets.xlsx')
usernameArray = []
if file_exists is True:
    df = pd.read_excel('/Users/user/Desktop/Intro-to-Ethereum-Programming/nodejs-twitter-bot/lw3Tweets.xlsx')
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

def get_tweet_authors(tweetIds):
    params = {
        "ids": ",".join(tweetIds),
        "user.fields": "username",
    }

    response = requests.get(
        tweetLookupEndpoint, params=params,
        headers={
            "User-Agent": "v2UserLookupPython",
            "Authorization": f"Bearer {bearer_token}"
        })

    if response.status_code != 200:
        raise Exception(f"Request failed with code {response.status_code}: {response.text}")

    return response.json()

def get_request():
    # Edit query parameters below
    # specify a search query, and any additional fields that are required
    # by default, only the Tweet ID and text fields are returned

    startDate = "2023-05-7T00:00:00Z"
    endDate = "2023-05-7T23:59:59Z"
    params = {
        "query": "#30DaysofSolidityLW3 has:mentions",
        "start_time": startDate,
        "end_time": endDate,
        "tweet.fields": "author_id",
        "user.fields": "username",
        "max_results": 100,
    }

    response = requests.get(
        endpointUrl, params=params,
        headers={
            "User-Agent": "v2FullArchiveSearchPython",
            "Authorization": f"Bearer {bearer_token}"
        })

    if response.status_code != 200:
        raise Exception(f"Request failed with code {response.status_code}: {response.text}")
    try:
        tweetData = response.json()["data"]
        tweetIds = [tweet["author_id"] for tweet in tweetData]
        authorsData = get_tweet_authors(tweetIds)
        authors = {}
        for author in authorsData["data"]:
            authors[author["id"]] = author["username"]
            

        for tweet in tweetData:
            tweet["author_name"] = authors[tweet["author_id"]]
            tweet["url"] = f"https://twitter.com/{tweet['author_name']}/status/{tweet['id']}"  
            if file_exists is False:
             if(tweet["author_name"]) not in usernameArray: 
              usernameArray.append(tweet["author_name"])
              attributes_container.append([current_time, tweet["author_name"], tweet["text"], tweet["url"], 1])
              tweets_df = pd.DataFrame(attributes_container, columns=["Date Created", "Username", "Tweets", "Link", "DaysOfCoding"])
              tweets_df.to_excel('/Users/user/Desktop/Intro-to-Ethereum-Programming/nodejs-twitter-bot/lw3Tweets.xlsx', header=True, index=False)
            else:
             if(tweet["author_name"]) not in usernameArray:  
               hashTable[tweet["author_name"]] = [tweet["text"], tweet["url"]]  
             if tweet["author_name"] not in nameValues and not usernameArray:
              attributes_container.append([current_time, tweet["author_name"], tweet["text"], tweet["url"], 1])
              tweets_df2 = pd.DataFrame(attributes_container, columns=["Date Created", "Username", "Tweets", "Link", "DaysOfCoding"])
              with pd.ExcelWriter("/Users/user/Desktop/Intro-to-Ethereum-Programming/nodejs-twitter-bot/lw3Tweets.xlsx",mode="a",engine="openpyxl",if_sheet_exists="overlay") as writer:
               tweets_df2.to_excel(writer, sheet_name="Sheet1",header=None, startrow=writer.sheets["Sheet1"].max_row,index=False)          
            usernameArray.append(tweet["author_name"])  

       
    except Exception as e:
        print(e)

if __name__ == "__main__":
    try:
        # Make request
        get_request()
    except Exception as e:
        print(e)
        exit(-1)


if file_exists is True:
 df = pd.read_excel('/Users/user/Desktop/Intro-to-Ethereum-Programming/nodejs-twitter-bot/lw3Tweets.xlsx')
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
   df.to_excel('/Users/user/Desktop/Intro-to-Ethereum-Programming/nodejs-twitter-bot/lw3Tweets.xlsx', sheet_name="Sheet1", header=True, index=False)
  counter = counter + 1

counter = 0
usernameArray = []
hashTable = {}

df = pd.DataFrame(pd.read_excel('/Users/user/Desktop/Intro-to-Ethereum-Programming/nodejs-twitter-bot/lw3Tweets.xlsx'))
df.drop_duplicates(subset=['Username'], inplace=True)
df.to_excel('/Users/user/Desktop/Intro-to-Ethereum-Programming/nodejs-twitter-bot/lw3Tweets.xlsx', sheet_name="Sheet1", header=True,index=False)
df.sort_values(by="DaysOfCoding", inplace=True, ascending=False)
df.to_excel('/Users/user/Desktop/Intro-to-Ethereum-Programming/nodejs-twitter-bot/lw3Tweets.xlsx', sheet_name="Sheet1", header=True, index=False)

# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive','https://www.googleapis.com/auth/drive.file','https://www.googleapis.com/auth/spreadsheets']
creds = ServiceAccountCredentials.from_json_keyfile_name('/Users/user/Desktop/Intro-to-Ethereum-Programming/nodejs-twitter-bot/mdrive.json', scope)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
# Make sure you use the right name here.
sheet = client.open("Learnweb3-DaysOfCode-Leaderboards").sheet1
spreadsheet_key = '1ifq06TD9qtnrSM5psbPAENktSXRM60RGUOtmDrMJgvk'


wks_name = '30DoS'
cell_of_start_df = 'A1'
d2g.upload(df,
      spreadsheet_key,
      wks_name,
      credentials=creds,
      col_names=True,
      row_names=True,
      start_cell = cell_of_start_df,
      clean=False)