import pandas as pd
import requests
import numpy as np
import datetime
import time
start_time = time.time()

eventIDs = []
url = 'https://sportsbook.draftkings.com//sites/US-SB/api/v1/eventgroup/3230960/full?format=json'
response = requests.get(url)
payload = response.json()['eventGroup']['events']
for e in payload:
    eventID = e['eventId']
    eventIDs.append(eventID)

scrapeData = []
for eventID in eventIDs:
    eventURL = f'https://sportsbook.draftkings.com//sites/US-SB/api/v1/event/{eventID}?format=json'
    response = requests.get(eventURL)
    payload = response.json()
    try:
        event_id = payload['event']['eventId']
        away_team = payload['event']['teamName1']
        home_team = payload['event']['teamName2']
        event_start = payload['event']['startDate']
        event_status = payload['event']['eventStatus']['state']
        categories = payload['eventCategories']
        for c in categories:
            if c['name'] == 'Game Lines':
                markets = c['componentizedOffers'][0]['offers'][0]
                for m in markets:
                    if 'label' in m and m['label'] == 'Point Spread':
                        selections = m['outcomes']
                        for s in selections:
                            line = s['line']
                    if 'label' in m and m['label'] == 'Total Points':
                        selections = m['outcomes']
                        for s in selections:
                            total = s['line']
                    if 'label' in m and m['label'] == 'Moneyline':
                        selections = m['outcomes']
                        for s in selections:
                            ML = s['oddsAmerican'][0]
                scrapeData.append([event_id,away_team,home_team,event_start,event_status,line,total,ML])
    except:
        pass
df = pd.DataFrame(scrapeData, columns=['event_id','away_team','home_team','event_start','event_status','current_line','current_total','ML'])
df['event_start'] = pd.to_datetime(df['event_start']).dt.tz_convert('US/Eastern')
df['capture_time'] = pd.to_datetime(datetime.datetime.now()).tz_localize('US/Eastern')



try:
    event_df = pd.read_csv('CBB_events.csv')
    event_df['event_start'] = pd.to_datetime(event_df['event_start']).dt.tz_convert('US/Eastern')
    event_df['capture_time'] = pd.to_datetime(event_df['capture_time']).dt.tz_convert('US/Eastern')
    event_df['opening_capture_time'] = pd.to_datetime(event_df['opening_capture_time']).dt.tz_convert('US/Eastern')
except:
    event_df = pd.DataFrame(columns=['event_id','away_team','home_team','event_start','event_status','opening_line',
                                 'opening_total','opening_capture_time','closing_line','closing_total',
                                     'closing_capture_time','current_line','current_total'])

new_events = []
for e in df['event_id']:
    if e in event_df['event_id'].to_list():
        pass
    else:
        new_events.append(e)
new_events = df[df['event_id'].isin(new_events)]

event = pd.concat([event_df,new_events],sort=False)
event.drop(['event_status','current_line', 'current_total', 'capture_time'],axis=1,inplace=True)
event = pd.merge(event,df[['event_id', 'event_status','current_line', 'current_total', 'capture_time']],on='event_id',how='left')

event['opening_line'] = np.where(event['opening_line'].isna(),event['current_line'],event['opening_line'])
event['opening_total'] = np.where(event['opening_total'].isna(),event['current_total'],event['opening_total'])
event['opening_capture_time'] = np.where(event['opening_capture_time'].isna(),event['capture_time'],event['opening_capture_time'])
event['countdown'] = event['event_start'] - event['capture_time']
one_hour = datetime.timedelta(hours=1)
event['closing_line'] = np.where(event['countdown'] < one_hour,event['current_line'],event['closing_line'])
event['closing_total'] = np.where(event['countdown'] < one_hour,event['current_total'],event['closing_total'])
event['closing_capture_time'] = np.where(event['countdown'] < one_hour,event['capture_time'],event['closing_capture_time'])


event['line_change'] = event['current_line'] - event['opening_line']
event['total_change'] = event['current_total'] - event['opening_total']
try:
    history = pd.read_csv('CBB_history.csv')
except:
    history = pd.DataFrame(columns=['event_id','event_status','current_line','current_total','capture_time'])

narrow = df[['event_id','event_status','current_line','current_total','capture_time']]
history = pd.concat([history,narrow])


history.to_csv('CBB_history.csv',index=False)
event.to_csv('CBB_events.csv',index=False)

print(f"Total Run Time: {round((time.time() - start_time)/60,3)} Minutes")