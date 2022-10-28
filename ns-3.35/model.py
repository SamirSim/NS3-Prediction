import numpy as np
import pandas as pd
from sklearn import linear_model
from sklearn.model_selection import train_test_split

data = pd.read_csv('lora-data-test.csv')

x = data.iloc[:,0:11]
y = data.iloc[:,11:13]

x_train, x_test, y_train, y_test = train_test_split(x, y)

print(x_train)
print(x_test)
print(y_train)
print(y_test)

regr = linear_model.LinearRegression()
regr.fit(x_train, y_train)

print('Intercept: ', regr.intercept_)
print('Coefficients: ', regr.coef_)

print("Train score: ", regr.score(x_train, y_train))
print("Test score: ", regr.score(x_test, y_test))

x = [[100,300,20,5000,1,2,9,0,1,125,1]]

y_pred = regr.predict(x)
print(f"Predicted response: {y_pred}")