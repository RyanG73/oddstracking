import pandas as pd
import requests

def get_event_IDs():
    # Returns a list of unique event IDs for all NCAAB matches on DK
    # 3230960 CBB
    eventIDs = []
    url = 'https://sportsbook.draftkings.com//sites/US-SB/api/v1/eventgroup/3/full?format=json'
    response = requests.get(url)
    payload = response.json()['eventGroup']['events']
    for e in payload:
        eventID = e['eventId']
        eventIDs.append(eventID)
    return eventIDs


def scrape_events(eventIDs=get_event_IDs()):
    # Returns a dataframe of all scraped data (Event Name, Event Status, Team Name, Current Spread)
    scrapeData = []
    for eventID in eventIDs:
        eventURL = f'https://sportsbook.draftkings.com//sites/US-SB/api/v1/event/{eventID}?format=json'
        response = requests.get(eventURL)
        payload = response.json()
        eventName = payload['event']['shortName']
        eventStatus = payload['event']['eventStatus']['state']
        categories = payload['eventCategories']
        for c in categories:
            if c['name'] == 'Game Lines':
                markets = c['componentizedOffers'][0]['offers'][0]
                for m in markets:
                    if 'label' in m and m['label'] == 'Point Spread':
                        selections = m['outcomes']
                        for s in selections:
                            name = s['label']
                            line = s['line']
                            scrapeData.append([eventName,eventStatus,name,line])
    df = pd.DataFrame(scrapeData, columns=['Event','Status','Team','Line'])
    return df


test = scrape_events()
print(test)



# 174342473
eventURL = f'https://sportsbook.draftkings.com//sites/US-SB/api/v1/event/176121455?format=json'
response = requests.get(eventURL)
payload = response.json()
eventId = payload['event']['eventId']
eventName = payload['event']['shortName']
eventStatus = payload['event']['eventStatus']['state']
categories = payload['eventCategories']
