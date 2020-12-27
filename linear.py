import pandas as pd
import numpy as np

odds = np.array([.1,.23,.32,.4,.47,.59,.75,.8,.9,.98])
goals = np.array([0,.5,1,1.5,2,2.5,3,3.5,4,4.5])

from sklearn.linear_model import LinearRegression

model = LinearRegression(fit_intercept=False)

x_raw, y_raw = odds,goals

x_data = x_raw.reshape(len(x_raw),1)
y_data = y_raw.reshape(len(y_raw),1)

model_fit = model.fit(x_data,y_data)
odds_seeker = .5
future_y = model.predict([[odds_seeker]])
print("Predicted = {:0.2f} Goals".format(future_y[0,0]))