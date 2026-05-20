
def plot_context(display_days):
    plt.figure(figsize=(10,5))
    plt.title(f"{ticker} - {display_days} Day View")
    plt.plot(df.index[-display_days:-1], df['close'].tail(display_days)[:-1], label="Actual", color='Blue')
    future_dates = pd.date_range(start=df.index[-1], periods=time_forward + 1, freq='B') #generates an array with the next time_forward days and skips weekends. 
    #Starts at the last day we had and ends after the time_forward days have passed
    connected_predictions = np.append(df['close'].iloc[-1], forecast)
    connected_lower = np.append(df['close'].iloc[-1], forecast_lower)
    connected_upper = np.append(df['close'].iloc[-1], forecast_upper)

    plt.plot(future_dates, connected_predictions, label="Predicted", color='Orange')
    plt.fill_between(future_dates, connected_lower, connected_upper, alpha=0.3, color='Orange', label='Margin of Error')
    plt.legend()
    plt.xlabel("Date")
    plt.ylabel("Price (US$)")

plot_context(2)
plot_context(30)
plot_context(90)