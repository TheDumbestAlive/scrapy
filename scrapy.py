import requests
import pandas as pd
from bs4 import BeautifulSoup
import datetime
import os
import time
from IPython.display import display
cards = []
print('A dueling nexus card scraper :3')

def getPage(url):
    # Stores the response from the page
    res = requests.get(url)
    print('Page fetched. Parsing HTML...')
    html = BeautifulSoup(res.content, 'html.parser')
    print('Parsed!')
    #Get all the <a> tags (where the wiki links to the cards are stored)
    cardEls = html.find_all('a')
    #Search for the stats (stored in tr td.)
    statEls = html.select('tr td')
    # Stores all the scraped cards.
    # Using the word 'wiki' (as in duelingnexus.com/wiki), sort for all the <a> tags that link to the wiki,
    # and pass the innerHTML as the card name.
    for i in cardEls:
        if 'wiki' in str(i):
            cards.append(i.getText())
    cardStats = []
    rawCardStats = []
    for i in statEls:
            if '%' in str(i):
                rawCardStats.append(i.getText())
                if len(rawCardStats) == 4:
                     proto = ''
                     proto += 'Win: '+rawCardStats[0]+','
                     proto += 'Draw: '+rawCardStats[1]+','
                     proto += 'Loss: '+rawCardStats[2]+','
                     proto += 'Usage: '+rawCardStats[3]+','
                     cardStats.append(proto)
                     rawCardStats = []

    for i in range(0,len(cardStats)):
        cards[i] += str(cardStats[i])

def pandaParse(unparsed):
    name = unparsed[2]
    stats = unparsed[5]
    stats = stats.split(',')
    stats = ",".join(list(map(lambda indx: indx.split(':')[1].strip() if len(indx.split(':')) > 1 else '', stats)))
    return f'"{name}",{stats[:-1]}'

cardTime = os.path.getmtime("cards.txt")
cardTime = datetime.datetime.fromtimestamp(cardTime)
cardTime = str(cardTime).split(' ')[0]
option = input(f'The cardlist was last updated on {cardTime}. Are you sure you want to update it *again*? (Type nothing for no, or "yes" for yes.).\n')
if option.lower() == 'yes':
    print('Updating cardlist...')
    fetchTime = time.perf_counter()
    print('Fetching cardlist...')
    getPage("https://duelingnexus.com/blog/yu-gi-oh-top-100-cards/")
    cards = list(map(lambda val: val.split('\t'), cards))
    cards = list(map(pandaParse, cards))
    endFetchTime = time.perf_counter()
    print(f'Cardlist filled & parsed! (Took {round(endFetchTime - fetchTime,3)}s)')
    with open('cards.txt', 'w',newline='', encoding='utf-8') as file:
        file.write('Name,W%,D%,L%,Usage\n')
        for i in cards:
            file.write(i+'\n')
        file.close()
print('Parsing data (again)...')
df = pd.read_csv('cards.txt')
df = df.fillna('N/A')
display(df)
ext = False
while not ext:
    action = input('Enter the name of a top 100 card, or the specific rank you would like to look at (or type "ext" to quit.) NOTE: 0 is the highest, not 1.\n')

    if action == 'ext':
        ext = True
        print('Closing...')
        break
    try:
        action = int(action)
    except:
        action = str(action)
    
    if type(action) == int:
        if action >= 0 and action < 100:
            print(f'Entry at position {action}')
            display(df.iloc[[action]])

    else:
        print(f'Matches for \'{action}\'')
        action = action.lower()
        display(df.query('Name.str.contains(@action)', engine='python'))