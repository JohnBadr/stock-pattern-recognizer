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
    end = datetime.now() + timedelta(days=1)
    start = end - timedelta(days=days)
    
    df = yf.download(ticker, start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"))
    df.columns = df.columns.get_level_values(0)
    df.columns = [c.lower() for c in df.columns]
    
    return df


@st.cache_data
def run_model(ticker, days, time_forward):

    df = get_stock_data(ticker, days)

    #features, thing the model will be trained on
    df['daily_return']=df['close'].pct_change() * 100 

    df['SMA_20']=df['close'].rolling(window=20).mean() 
    df['SMA_50']=df['close'].rolling(window=50).mean()

    df['volume_change']=df['volume'].pct_change() * 100

    df['price_range']=df['high']-df['low']

    df['target']=df['close'].shift(-1)

    df_clean=df.dropna()

    features=df_clean[['daily_return', 'SMA_20', 'SMA_50', 'volume_change', 'price_range']]
    target_values=df_clean['target']

    features_train, features_test, target_values_train, target_values_test = train_test_split(features, target_values, test_size=0.2, random_state=42)

    #machine learning model \/
    regressor=RandomForestRegressor(n_estimators=N_ESTIMATORS, random_state=42)
    regressor.fit(features_train, target_values_train)

    tree_predictions=[tree.predict(features_test.values) for tree in regressor.estimators_]
    tree_predictions_array=np.array(tree_predictions)

    #predictor for the next time_forward days:
    last_features = features.iloc[[-1]].copy()
    last_close = df['close'].iloc[-1]
    forecast = []
    tree_preds = []
    recent_closes = list(df['close'].iloc[-50:])
    for i in range(time_forward): #here -> takes the last row of values then uses them to calc day 1, then uses the vals of
        pred = regressor.predict(last_features) #day 1 to calc day 2 etc. This causes compounding/accumulating error, the
        forecast.append(pred[0])  #more it goes forward, the more inaccurate it gets, exponentially.

        tree_preds_step = [tree.predict(last_features.values) for tree in regressor.estimators_]
        lower = np.percentile(tree_preds_step, 25)
        upper = np.percentile(tree_preds_step, 75)
        tree_preds.append((lower, upper))

        new_return = (pred[0] - last_close) / last_close * 100
        last_features['daily_return'] = new_return
        
        last_close = pred[0]  # update for next iteration
        recent_closes.append(pred[0])
        
        new_SMA_20 = np.mean(recent_closes[-20:])
        new_SMA_50 = np.mean(recent_closes[-50:])
        last_features['SMA_20'] = new_SMA_20
        last_features['SMA_50'] = new_SMA_50

        #price_range and volume_change we can't really calculate from predicted prices 
        # since we don't know future highs/lows or volume. So we just leave them as the last real values 

    forecast = np.array(forecast)
    forecast_lower = np.array([x[0] for x in tree_preds])
    forecast_upper = np.array([x[1] for x in tree_preds])

    return df, forecast, forecast_lower, forecast_upper