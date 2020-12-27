import pandas as pd
import requests
import numpy as np
import datetime
import time
import seaborn as sns
import matplotlib.pyplot as plt

start_time = time.time()
slot = {9:'London',
        12:'early',
        13:'early',
        16:'afternoon',
        20:'primetime'}
events = pd.read_csv('output/CBB_events.csv')
history = pd.read_csv('output/CBB_history.csv')

events = events[['event_id', 'event_start','away_team','home_team']]
history2 = pd.merge(history,events,on='event_id',how='left')
history2['capture_time'] = pd.to_datetime(history2['capture_time'])
history2['event_start'] = pd.to_datetime(history2['event_start'])
history2['date'] = history2['capture_time'].dt.date
history2['game_slot'] = history2['event_start'].dt.hour
history2['game_slot'] = history2['game_slot'].map(slot)
history2['matchup'] = history2['away_team'] + " @ " + history2['home_team']
history2['implied_probability_away'] = np.where(history2['ML_away'] > 0,(100/(history2['ML_away'] + 100)),(abs(history2['ML_away'])/(abs(history2['ML_away'])+100)))
history2['implied_probability_home'] = np.where(history2['ML_home'] > 0,(100/(history2['ML_home'] + 100)),(abs(history2['ML_home'])/(abs(history2['ML_home'])+100)))
history2['true_probability_home'] = history2['implied_probability_home'] / (history2['implied_probability_home'] + history2['implied_probability_away'])

#history2 = history2[history2['date'] == '2020-12-20']
#history2 = history2[history2['game_slot'] == 'primetime']
history2 = history2[history2['home_team'] == 'Washington']

#sns.lineplot(data=testgame,x='capture_time',y='current_line',hue='event_status')

g = sns.relplot(
    data=history2, x="capture_time", y="current_line",
    col="matchup", hue="event_status", style="event_status",
    kind="line",col_wrap=1,height=5,aspect=2
)
axes = g.axes.flatten()
for ax in axes:
    ax.axvline(x='2020-12-20 13:00:00-05:00',color='g',alpha=.3)
    ax.axvline('2020-12-20 14:00:00-05:00',color='g',alpha=.1)
    ax.axvline('2020-12-20 15:00:00-05:00',color='g',alpha=.1)
    ax.axvline('2020-12-20 16:00:00-05:00',color='g',alpha=.3)
    ax.axvline('2020-12-20 17:00:00-05:00',color='g',alpha=.1)
    ax.axvline('2020-12-20 18:00:00-05:00',color='g',alpha=.1)
    ax.axvline('2020-12-20 19:00:00-05:00',color='g',alpha=.1)
    ax.axvline('2020-12-20 20:00:00-05:00',color='g',alpha=.3)
    ax.axvline('2020-12-20 21:00:00-05:00',color='g',alpha=.1)
    ax.axvline('2020-12-20 22:00:00-05:00',color='g',alpha=.1)
    ax.axvline('2020-12-20 23:00:00-05:00',color='g',alpha=.1)
    ax.axvline('2020-12-20 23:59:00-05:00',color='g',alpha=.1)
    ax.axhline(y=0, color='k', alpha=.1)
plt.show()

print(f"Total Run Time: {round((time.time() - start_time)/60,3)} Minutes")


g = sns.relplot(
    data=history2, x="capture_time", y="true_probability_home",
    col="matchup", hue="event_status", style="event_status",
    kind="line",col_wrap=1,height=5,aspect=2
)
axes = g.axes.flatten()
for ax in axes:
    ax.axvline('2020-12-20 13:00:00-05:00',color='g',alpha=.3)
    ax.axvline('2020-12-20 14:00:00-05:00',color='g',alpha=.1)
    ax.axvline('2020-12-20 15:00:00-05:00',color='g',alpha=.1)
    ax.axvline('2020-12-20 16:00:00-05:00',color='g',alpha=.3)
    ax.axvline('2020-12-20 17:00:00-05:00',color='g',alpha=.1)
    ax.axvline('2020-12-20 18:00:00-05:00',color='g',alpha=.1)
    ax.axvline('2020-12-20 19:00:00-05:00',color='g',alpha=.1)
    ax.axvline('2020-12-20 20:00:00-05:00',color='g',alpha=.3)
    ax.axvline('2020-12-20 21:00:00-05:00',color='g',alpha=.1)
    ax.axvline('2020-12-20 22:00:00-05:00',color='g',alpha=.1)
    ax.axvline('2020-12-20 23:00:00-05:00',color='g',alpha=.1)
    ax.axvline('2020-12-20 23:59:00-05:00',color='g',alpha=.1)
    ax.axhline(y=0.5, color='k', alpha=.1)
    ax.set_ylim(0, 1)
    ax.set_yticks((0,.2,.4,.6,.8,1))
    ax.set_yticklabels(("100% AWAY", "80% AWAY","60% AWAY", "60% HOME", "80% HOME", "100% HOME"))
plt.show()