from config import *

N_ESTIMATORS = 100

def parse_time_input(time_str): #gets the time input desired by user
    time_str = time_str.strip().lower()
    
    if time_str.isdigit():
        days = int(time_str)
    elif time_str.endswith("d"):
        days = int(time_str[:-1])
    elif time_str.endswith("m"):
        days = int(time_str[:-1]) * 30
    elif time_str.endswith("y"):
        days = int(time_str[:-1]) * 365
    else:
        raise ValueError("Invalid format. Use d, m, or y (e.g. 90d, 6m, 2y)")
    
    if days < 30:
        raise ValueError("Minimum time period is 30d")
    if days > 1825:
        raise ValueError("Maximum time period is 5y")
    
    return days

def days_forward(time_advance):
    
    if time_advance>=1 and time_advance<=30:
        return time_advance
    
    else:
        raise ValueError('Invalid. Make sure you enter a number between 1-30: ')

def get_stock_data(ticker, days=365): #gets stock data desired by user and put it in a pandas df
    end = datetime.now()
    start = end - timedelta(days=days)
    
    df = api.get_bars(
        ticker,
        "1Day",
        start=start.strftime("%Y-%m-%d"),
        end=end.strftime("%Y-%m-%d"),
        feed="iex"
    ).df
    
    return df

while True:
    try:
        ticker = input("Enter a stock ticker: ").upper() 
        test = get_stock_data(ticker, 30)
        if test.empty:
            raise ValueError()
        break
    except:
        print("Stock unknown or nonexistent. Try again. ", end="")

while True:
    try:
        time_input = input("How far back should we analyze? (e.g. 90d, 6m, 2y): ")
        days = parse_time_input(time_input)
        break
    except:
        print("Invalid format. ", end="")

while True:
    try:
        time_forward = input("How many days ahead do you want to predict? (1-30d): ")
        time_forward=int(time_forward[:-1]) if time_forward.endswith('d') else int(time_forward)
        time_forward=days_forward(time_forward)
        break
    except:
        print("Invalid format or invalid day number. ", end="")


df = get_stock_data(ticker, days)
# print(df.head())

df['daily_return']=df['close'].pct_change() * 100 #adds a daily return column to our df

df['SMA_20']=df['close'].rolling(window=20).mean() #SMA 20 & 50
df['SMA_50']=df['close'].rolling(window=50).mean()

df['volume_change']=df['volume'].pct_change() * 100 #volume change, can be its own indicator

df['price_range']=df['high']-df['low']

df['target']=df['close'].shift(-time_forward)

df=df.dropna()

features=df[['daily_return', 'SMA_20', 'SMA_50', 'volume_change', 'price_range']]
target_values=df['target']

features_train, features_test, target_values_train, target_values_test = train_test_split(features, target_values, test_size=0.2, random_state=42)

regressor=RandomForestRegressor(n_estimators=N_ESTIMATORS, random_state=42)
regressor.fit(features_train, target_values_train)

predictions=regressor.predict(features_test)

tree_predictions=[tree.predict(features_test.values) for tree in regressor.estimators_]
tree_predictions_array=np.array(tree_predictions)

lower_bound=np.percentile(tree_predictions_array, 5, axis=0)
upper_bound=np.percentile(tree_predictions_array, 95, axis=0)

print(predictions)
print(upper_bound)
print(lower_bound)