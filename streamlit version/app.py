from config import *
from predictor import parse_time_input, get_stock_data, run_model

st.title("Stock Pattern Recognizer")

ticker = st.text_input("Enter a stock ticker:").upper()
time_input = st.text_input("How far back should we analyze? (e.g. 90d, 6m, 2y)")
time_forward = st.number_input("How many days ahead to predict?", min_value=1, max_value=30, value=5, step=1)

if st.button("Run"):
    try:
        days = parse_time_input(time_input)
        test = get_stock_data(ticker, 30)
        if test.empty:
            raise ValueError()
    except:
        st.error("Invalid ticker or time format.")
        st.stop()

    df, forecast, forecast_lower, forecast_upper = run_model(ticker, days, time_forward)

    def plot_context(display_days):
        fig = go.Figure()
        future_dates = pd.date_range(start=df.index[-1], periods=time_forward + 1, freq='B')
        connected_predictions = np.append(df['close'].iloc[-1], forecast)
        connected_lower = np.append(df['close'].iloc[-1], forecast_lower)
        connected_upper = np.append(df['close'].iloc[-1], forecast_upper)

        fig.add_trace(go.Scatter(x=df.index[-display_days:], y=df['close'].tail(display_days), name="Actual", line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=future_dates, y=connected_predictions, name="Predicted", line=dict(color='orange')))
        fig.add_trace(go.Scatter(x=future_dates, y=connected_upper, fill=None, mode='lines', line=dict(color='rgba(255,165,0,0)'), showlegend=False))
        fig.add_trace(go.Scatter(x=future_dates, y=connected_lower, fill='tonexty', mode='lines', line=dict(color='rgba(255,165,0,0)'), fillcolor='rgba(255,165,0,0.3)', name="Margin of Error"))

        fig.update_layout(title=f"{ticker} - {display_days} Day View", xaxis_title="Date", yaxis_title="Price (US$)")
        st.plotly_chart(fig)

    plot_context(30)
    plot_context(90)

