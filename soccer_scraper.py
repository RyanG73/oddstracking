import pandas as pd
import requests
import numpy as np
import datetime
import time
from sklearn.linear_model import LinearRegression
import seaborn as sns
import matplotlib.pyplot as plt
start_time = time.time()

leagues = {'Premier_League':53591936,'UEFA_Champions_League':56277606,'Europa_League':56420964,'Bundesliga':43,'La_Liga':56798651}
# 'Serie_A':132
for g in leagues:
    eventIDs = []
    url = f'https://sportsbook.draftkings.com//sites/US-SB/api/v1/eventgroup/{leagues[g]}/full?format=json'
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
            if event_status == 'STARTED':
                period = payload['event']['eventStatus']['period']
                minute = payload['event']['eventStatus']['minute']
                second = payload['event']['eventStatus']['second']
                home_score = payload['event']['eventStatus']['homeTeamScore']
                away_score = payload['event']['eventStatus']['awayTeamScore']
            for c in categories:
                if c['name'] == 'Game Lines':
                    ML_markets = c['componentizedOffers'][0]['offers'][0]
                    for m in ML_markets:
                        if 'label' in m and m['label'] == 'Full Time':
                            selections = m['outcomes']
                            label1 = selections[0]['label']
                            ML1 = selections[0]['oddsAmerican']
                            label2 = selections[1]['label']
                            ML2 = selections[1]['oddsAmerican']
                            label3 = selections[2]['label']
                            ML3 = selections[2]['oddsAmerican']
                    TOT_markets = c['componentizedOffers'][1]['offers'][0]
                    over_odds = np.array([])
                    over_line = np.array([])
                    under_odds = np.array([])
                    under_line = np.array([])
                    for m in TOT_markets:
                        if 'label' in m and m['label'] == 'Total Goals':
                            for t in m['outcomes']:
                                if t['label'] == 'Over':
                                    over_odds = np.append(over_odds,t['oddsAmerican'])
                                    over_line = np.append(over_line, t['line'])
                                if t['label'] == 'Under':
                                    under_odds = np.append(under_odds,t['oddsAmerican'])
                                    under_line = np.append(under_line, t['line'])
                        if 'goals' in globals():
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
                        if 'ML3' in globals():
                            pass
                        else:
                            ML3 = np.nan
                        if 'period' in globals():
                            pass
                        else:
                            period = np.nan
                        if 'minute' in globals():
                            pass
                        else:
                            minute = np.nan
                        if 'second' in globals():
                            pass
                        else:
                            second = np.nan
                        if 'home_score' in globals():
                            pass
                        else:
                            home_score = np.nan
                        if 'away_score' in globals():
                            pass
                        else:
                            away_score = np.nan
                    over_odds = over_odds.astype(float)
                    under_odds = under_odds.astype(float)
                    over_probability = np.where(over_odds > 0,(100 /(over_odds + 100)),(abs(over_odds)/(abs(over_odds)+100)))
                    under_probability = np.where(under_odds > 0, (100 / (under_odds + 100)),
                                                (abs(under_odds) / (abs(under_odds) + 100)))
                    under_probability = 1 - under_probability
                    probability = np.append(over_probability,under_probability)
                    lines = np.append(over_line,under_line)
                    model = LinearRegression()
                    x_raw, y_raw = probability,lines
                    x_data = x_raw.reshape(len(x_raw), 1)
                    y_data = y_raw.reshape(len(y_raw), 1)
                    model_fit = model.fit(x_data, y_data)
                    odds_seeker = .5
                    goals = model.predict([[odds_seeker]])
                    goals = goals[0,0].round(2)
                    goals = np.where(goals<0,0,goals)
                    print(f"{away_team} @ {home_team} -- O/U {goals} Goals")
                    scrapeData.append([event_id,away_team,home_team,event_start,event_status,ML1,ML2,ML3,goals,period,minute,second,home_score,away_score])
                    del (ML1,ML2,ML3,goals,period,minute,second,home_score,away_score)
        except:
            pass
    df = pd.DataFrame(scrapeData, columns=['event_id','away_team','home_team','event_start','event_status','away_ML','tie_ML','home_ML','current_total','period','minute','second','home_score','away_score'])
    df['event_start'] = pd.to_datetime(df['event_start']).dt.tz_convert('US/Eastern')
    df['capture_time'] = pd.to_datetime(datetime.datetime.now()).tz_localize('US/Eastern')
    try:
        event_df = pd.read_csv(f'output/{g}_events.csv')
        event_df['event_start'] = pd.to_datetime(event_df['event_start']).dt.tz_convert('US/Eastern')
        event_df['capture_time'] = pd.to_datetime(event_df['capture_time']).dt.tz_convert('US/Eastern')
        event_df['opening_capture_time'] = pd.to_datetime(event_df['opening_capture_time']).dt.tz_convert('US/Eastern')
    except:
        event_df = pd.DataFrame(columns=['event_id','away_team','home_team','event_start','event_status',
                                     'opening_total','opening_capture_time','closing_total',
                                         'closing_capture_time','current_total','away_ML','tie_ML','home_ML',
                                         'opening_ML_away','opening_ML_tie','opening_ML_home','closing_ML_away','closing_ML_tie','closing_ML_home'])
    new_events = []
    for e in df['event_id']:
        if e in event_df['event_id'].to_list():
            pass
        else:
            new_events.append(e)
    new_events = df[df['event_id'].isin(new_events)]
    event = pd.concat([event_df,new_events],sort=False)
    event.drop(['event_status', 'current_total', 'capture_time','away_ML','tie_ML','home_ML'],axis=1,inplace=True)
    event = pd.merge(event,df[['event_id', 'event_status', 'current_total', 'capture_time','away_ML','tie_ML','home_ML']],on='event_id',how='left')
    event['opening_total'] = np.where(event['opening_total'].isna(),event['current_total'],event['opening_total'])
    event['opening_ML_away'] = np.where(event['opening_ML_away'].isna(),event['away_ML'],event['opening_ML_away'])
    event['opening_ML_tie'] = np.where(event['opening_ML_tie'].isna(),event['tie_ML'],event['opening_ML_tie'])
    event['opening_ML_home'] = np.where(event['opening_ML_home'].isna(),event['home_ML'],event['opening_ML_home'])
    event['opening_capture_time'] = np.where(event['opening_capture_time'].isna(),event['capture_time'],event['opening_capture_time'])
    event['countdown'] = event['event_start'] - event['capture_time']
    one_hour = datetime.timedelta(hours=1)
    game_time = datetime.timedelta(hours=0)
    event['closing_total'] = np.where((event['countdown'] < one_hour)&((event['countdown'] > game_time)),event['current_total'],event['closing_total'])
    event['closing_capture_time'] = np.where((event['countdown'] < one_hour)&((event['countdown'] > game_time)),event['capture_time'],event['closing_capture_time'])
    event['closing_ML_away'] = np.where((event['countdown'] < one_hour)&((event['countdown'] > game_time)),event['away_ML'],event['closing_ML_away'])
    event['closing_ML_tie'] = np.where((event['countdown'] < one_hour)&((event['countdown'] > game_time)),event['tie_ML'],event['closing_ML_tie'])
    event['closing_ML_home'] = np.where((event['countdown'] < one_hour)&((event['countdown'] > game_time)),event['home_ML'],event['closing_ML_home'])
    event['total_change'] = event['current_total'] - event['opening_total']
    event['away_ML'] = event['away_ML'].astype(float)
    event['implied_probability_away'] = np.where(event['away_ML'] > 0,(100/(event['away_ML'] + 100)),(abs(event['away_ML'])/(abs(event['away_ML'])+100)))
    event['implied_probability_away'] = event['implied_probability_away'].round(2)
    event['tie_ML'] = event['tie_ML'].astype(float)
    event['implied_probability_tie'] = np.where(event['tie_ML'] > 0,(100/(event['tie_ML'] + 100)),(abs(event['tie_ML'])/(abs(event['tie_ML'])+100)))
    event['implied_probability_tie'] = event['implied_probability_tie'].round(2)
    event['home_ML'] = event['home_ML'].astype(float)
    event['implied_probability_home'] = np.where(event['home_ML'] > 0,(100/(event['home_ML'] + 100)),(abs(event['home_ML'])/(abs(event['home_ML'])+100)))
    event['implied_probability_home'] = event['implied_probability_home'].round(2)
    event = event[['event_id',
            'event_start',
            'implied_probability_away',
            'away_ML',
            'away_team',
            'tie_ML',
            'implied_probability_tie',
            'current_total',
            'home_team',
            'home_ML',
            'implied_probability_home',
            'total_change',
            'event_status',
            'opening_total',
            'closing_total',
            'opening_ML_away',
            'closing_ML_away',
            'opening_ML_tie',
            'closing_ML_tie',
            'opening_ML_home',
            'closing_ML_home',
            'opening_capture_time',
            'closing_capture_time',
            'countdown',
            'capture_time']]
    try:
        history = pd.read_csv(f'output/{g}_history.csv')
    except:
        history = pd.DataFrame(columns=['event_id','event_status','current_line','current_total','capture_time','period','minute','second','home_score','away_score'])
    narrow = df[['event_id','event_status','current_total','away_ML','tie_ML','home_ML','capture_time','period','minute','second','home_score','away_score']]
    history = pd.concat([history,narrow])
    history.to_csv(f'output/{g}_history.csv',index=False)
    event.to_csv(f'output/{g}_events.csv',index=False)
    print(f"{g} is finished at {round((time.time() - start_time)/60,3)} Minutes --------------------------------------")

print(f"Total Run Time: {round((time.time() - start_time)/60,3)} Minutes")