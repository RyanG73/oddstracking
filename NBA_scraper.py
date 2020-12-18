import pandas as pd
import requests
import numpy as np
import datetime
import time
start_time = time.time()

eventIDs = []
url = 'https://sportsbook.draftkings.com//sites/US-SB/api/v1/eventgroup/103/full?format=json'
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
                        ML1 = selections[0]['oddsAmerican']
                        ML2 = selections[1]['oddsAmerican']
                    if 'total' in globals():
                        pass
                    else:
                        total = np.nan
                    if 'line' in globals():
                        pass
                    else:
                        line = np.nan
                    if 'ML1' in globals():
                        pass
                    else:
                        ML1 = np.nan
                    if 'ML2' in globals():
                        pass
                    else:
                        ML2 = np.nan
                scrapeData.append([event_id,away_team,home_team,event_start,event_status,line,total,ML1,ML2])
                del (line, total, ML1, ML2)
    except:
        pass
df = pd.DataFrame(scrapeData, columns=['event_id','away_team','home_team','event_start','event_status','current_line','current_total','ML_away','ML_home'])
df['event_start'] = pd.to_datetime(df['event_start']).dt.tz_convert('US/Eastern')
df['capture_time'] = pd.to_datetime(datetime.datetime.now()).tz_localize('US/Eastern')



try:
    event_df = pd.read_csv('output/NBA_events.csv')
    event_df['event_start'] = pd.to_datetime(event_df['event_start']).dt.tz_convert('US/Eastern')
    event_df['capture_time'] = pd.to_datetime(event_df['capture_time']).dt.tz_convert('US/Eastern')
    event_df['opening_capture_time'] = pd.to_datetime(event_df['opening_capture_time']).dt.tz_convert('US/Eastern')
except:
    event_df = pd.DataFrame(columns=['event_id','away_team','home_team','event_start','event_status','opening_line',
                                 'opening_total','opening_capture_time','closing_line','closing_total',
                                     'closing_capture_time','current_line','current_total','ML_away','ML_home',
                                     'opening_ML_away','opening_ML_home','closing_ML_away','closing_ML_home'])

new_events = []
for e in df['event_id']:
    if e in event_df['event_id'].to_list():
        pass
    else:
        new_events.append(e)
new_events = df[df['event_id'].isin(new_events)]

event = pd.concat([event_df,new_events],sort=False)
event.drop(['event_status','current_line', 'current_total', 'capture_time','ML_away','ML_home'],axis=1,inplace=True)
event = pd.merge(event,df[['event_id', 'event_status','current_line', 'current_total', 'capture_time','ML_away','ML_home']],on='event_id',how='left')

event['opening_line'] = np.where(event['opening_line'].isna(),event['current_line'],event['opening_line'])
event['opening_total'] = np.where(event['opening_total'].isna(),event['current_total'],event['opening_total'])
event['opening_ML_away'] = np.where(event['opening_ML_away'].isna(),event['ML_away'],event['opening_ML_away'])
event['opening_ML_home'] = np.where(event['opening_ML_home'].isna(),event['ML_home'],event['opening_ML_home'])
event['opening_capture_time'] = np.where(event['opening_capture_time'].isna(),event['capture_time'],event['opening_capture_time'])
event['countdown'] = event['event_start'] - event['capture_time']
one_hour = datetime.timedelta(hours=1)
game_time = datetime.timedelta(hours=0)
event['closing_line'] = np.where((event['countdown'] < one_hour)&((event['countdown'] > game_time)),event['current_line'],event['closing_line'])
event['closing_total'] = np.where((event['countdown'] < one_hour)&((event['countdown'] > game_time)),event['current_total'],event['closing_total'])
event['closing_capture_time'] = np.where((event['countdown'] < one_hour)&((event['countdown'] > game_time)),event['capture_time'],event['closing_capture_time'])
event['closing_ML_away'] = np.where((event['countdown'] < one_hour)&((event['countdown'] > game_time)),event['ML_away'],event['closing_ML_away'])
event['closing_ML_home'] = np.where((event['countdown'] < one_hour)&((event['countdown'] > game_time)),event['ML_home'],event['closing_ML_home'])

event['line_change'] = event['current_line'] - event['opening_line']
event['total_change'] = event['current_total'] - event['opening_total']

event['ML_away'] = event['ML_away'].astype(int)
event['implied_probability_away'] = np.where(event['ML_away'] > 0,(100/(event['ML_away'] + 100)),(abs(event['ML_away'])/(abs(event['ML_away'])+100)))
event['implied_probability_away'] = event['implied_probability_away'].round(2)
event['ML_home'] = event['ML_home'].astype(int)
event['implied_probability_home'] = np.where(event['ML_home'] > 0,(100/(event['ML_home'] + 100)),(abs(event['ML_home'])/(abs(event['ML_home'])+100)))
event['implied_probability_home'] = event['implied_probability_home'].round(2)

event = event[['event_id',
        'event_start',
        'implied_probability_away',
        'ML_away',
        'away_team',
        'current_line',
        'current_total',
        'home_team',
        'ML_home',
        'implied_probability_home',
        'line_change',
        'total_change',
        'event_status',
        'opening_line',
        'closing_line',
        'opening_total',
        'closing_total',
        'opening_ML_away',
        'closing_ML_away',
        'opening_ML_home',
        'closing_ML_home',
        'opening_capture_time',
        'closing_capture_time',
        'countdown',
        'capture_time']]


try:
    history = pd.read_csv('output/NBA_history.csv')
except:
    history = pd.DataFrame(columns=['event_id','event_status','current_line','current_total','capture_time'])

narrow = df[['event_id','event_status','current_line','current_total','ML_away','ML_home','capture_time']]
history = pd.concat([history,narrow])


history.to_csv('output/NBA_history.csv',index=False)
event.to_csv('output/NBA_events.csv',index=False)

print(f"Total Run Time: {round((time.time() - start_time)/60,3)} Minutes")