# Importiere alle benötigten packages

# Logging: Logge die Meldungen bei den Ausführungen deines Scripts mit, um Fehler einfacher beheben zu können.
import logging
# Client von binance.client: Binance API-Client ermöglicht uns die Abfrage von Kursdaten und ebenso die Ausführung von Kauf-/Verkaufaufträgen.
from binance.client import Client
# pandas as pd: Pandas wird für die Datenmanipulation verwendet, insbesondere für die Arbeit mit DataFrames. Wir wandeln damit die erhaltenen Kursdaten in ein weiterverarbeitbares DataFrame um.
import pandas as pd
# json: Dies wird verwendet, um die Konfiguration aus der Datei config.json zu laden. In diesem File sind die API-Schlüssel gespeichert.
import json
# pandas_ta as ta: Mit diesem Package können wir Analyseindikatoren auf pandas DataFrames anwenden. Wir berechnen dabei den MACD-Indikator, der die Grundlage für unsere Kauf-/Verkaufssignale ist.
import pandas_ta as ta
# time: Wird verwendet, um Verzögerungen mittels Sleep zwischen den Iterationen einzuführen. Es wird benötigt, um die Ausführung der Schleife zu steuern.
import time
# pytz: Dies wird verwendet, um mit Zeitzonen zu arbeiten. Es ist notwendig, um Zeitstempel in die gewünschte Zeitzone zu konvertieren, was wir für den auf unsere Zeitzone angepassten Timestamp verwenden.
import pytz
# csv: Dies wird verwendet, um Informationen über Kauf-/Verkauf Aufträge in eine CSV-Datei als Art Orderbuch zu schreiben.
import csv

# Erstelle ein logging und speichere die logs in einem neuen File unter der Bezeichnung 'optimistprimetrader.log'. Level Einstellung ist ERROR.
logging.basicConfig(
    level=logging.ERROR,  # Lege das Logging Level fest (INFO, WARNING, ERROR, etc.).
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='optimistprimetrader.log', # Benenne das Logfile 
    filemode='a' # Setzte den Mode 'a' fest, um weitere Lognachrichten im File zu ergänzen. 
)

# Lade das config file, welches die API Keys enthält. Die Keys erhält man unter https://testnet.binance.vision/".
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Definiere deine registrierten Keys und die API.
binance_api_key = config['binance']['api_key']
binance_api_secret = config['binance']['api_secret']
binance_api = Client(binance_api_key, binance_api_secret, testnet=True)

# Definiere mittels ta package von pandas den zu berechnenden MACD, den wir als Indikator verwenden.
def get_macd(data, slow=12, fast=26, signal=9):
    macd = ta.macd(data, slow=slow, fast=fast, signal=signal)
    return macd.iloc[:, -1]

# Definiere die Funktion, mit welcher wir die Binance API nach dem festgelegten Intervall ausführen und speichere das Ergebnis als Pandas DataFrame. Definiere die Zeit als Index und entferne die überflüssigen Spalten. 
def get_bars(asset='ADA'):
    bars = binance_api.get_historical_klines(f"{asset}USDT", Client.KLINE_INTERVAL_1MINUTE, start_str="1 hour ago UTC-1")
    df = pd.DataFrame(bars)
    df.columns = ["Open time", "Open", "High", "Low", "Close", "Volume", "Close time", "Quote asset volume", "Number of trades", "Taker buy base asset volume", "Taker buy quote asset volume", "Ignore"]
    df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')
    df.set_index('Open time', inplace=True)
    df = df.iloc[:, :7]

    # Ändere den Datentyp in ein nummerisches Format, um mit den Werten die MACD bzw. Percentage Change über 30 Minuten berechnen zu können.
    for col in df.columns:
        df[col] = pd.to_numeric(df[col])

    # Führe die im Vorfeld definierte Funktion 'get_macd' aus und berechne den Percentage Change
    df['macd'] = get_macd(df["Close"])
    df['pct_change_30m'] = df['Close'].pct_change(30)
    return df

# Definiere das Set an Assets, für welche du die Kursdaten abfragen möchtest, was die als Grundlage für die Ausführung von Handelsaufträgen dient. Lege dabei auch die Order_size pro Asset fest.
assets = [
    {'asset':'ADA','is_long':False,'order_size':10},
    {'asset':'BTC','is_long':False,'order_size':1},
    {'asset':'LTC','is_long':False,'order_size':1},
    {'asset':'TRX','is_long':False,'order_size':100},
    {'asset':'ETH','is_long':False,'order_size':1},
    {'asset':'BNB','is_long':False,'order_size':1},
    {'asset':'XRP','is_long':False,'order_size':100}
]

# Definiere eine Funktion um die Trading Details in einem .csv zu sammeln, nutze dabei den mode 'a', um alle weiteren Trades zu ergänzen
def write_order_to_csv(order_type, asset, quantity, price, timestamp):
    with open('orderbook.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([order_type, asset, quantity, price, timestamp])

# Definiere die aus unserer Sicht korrekte Zeitzone mit dem Package pytz
gmt_minus_1 = pytz.timezone('Etc/GMT-1')

while True:
    try:
        # Definiere die API Abfrage für die Accountinformationen, mit welcher wir den akutellen Depotstand des jeweiligen Assets abfragen
        account_info = binance_api.get_account()

        for asset_info in assets:
            asset, is_long, order_size = asset_info['asset'], asset_info['is_long'], asset_info['order_size']

            try:
                bars = get_bars(asset=asset)

                if bars is not None and not bars.empty:
                    # Definiere die Regel für das Kauf- & Verkaufsignal. Wenn der MACD größer 0 sowie der Percentage Change der letzen 30 minuten größer Null ist, wird ein Kaufsignal ausgelöst. Gegenteiliges gilt für das Verkaufssignal.
                    should_buy = bars['macd'].iloc[-1] > 0 and bars['pct_change_30m'].iloc[-1] > 0
                    should_sell = bars['macd'].iloc[-1] < 0 and bars['pct_change_30m'].iloc[-1] < 0
                else:
                    should_buy = False
                    should_sell = False

                # Frage den letzten Close Price ab und passe die Zeitzone ensprechend an
                if not bars.empty:
                    latest_close = bars['Close'].iloc[-1]
                    latest_close_time_utc = pd.to_datetime(bars['Close time'].iloc[-1], unit='ms', utc=True)
                    latest_close_time_gmt_minus_1 = latest_close_time_utc.astimezone(gmt_minus_1)
                    # Drucke die entsprechenden Werte an. Is Long = wir haben Bestand; Should Buy: Asset soll gekauft werden; Should Sell: Asset soll verkauft werden; Close Price: Aktueller Preis; Time: Aktueller Timestamp in CET
                    print(f"Asset: {asset} / Is Long: {is_long} / Should Buy: {should_buy}, / Should Sell: {should_sell} / Close Price: {latest_close:.8f} / Time: {latest_close_time_gmt_minus_1.strftime('%Y-%m-%d %H:%M')}")

                    # Drucke den aktuellen Depotstand an
                    for balance in account_info['balances']:
                        if balance['asset'] == asset:
                            print(f"Balance for {asset}: {float(balance['free']):.8f}")

                    #Definiere das Kaufsignal: Wenn wir keinen Bestand haben und die Should Buy Regel True ist, dann drucke das Trade Statement und sende eine Market Buy Order mittels Binance API für das entsprechende Asset und die festgelegte Ordersize
                    if is_long == False and should_buy == True:
                        print(f'+++ TRADE +++ We are buying {order_size} {asset}')
                        order = binance_api.order_market_buy(symbol=f'{asset}USDT', quantity=order_size)
                        asset_info['is_long'] = True
                        # Schreib den Trade in das orderbook.csv
                        write_order_to_csv('Buy', asset, order_size, latest_close, latest_close_time_gmt_minus_1.strftime("%Y-%m-%d %H:%M"))

                    #Definiere das Kaufsignal: Wenn wir keinen Bestand haben und die Should Buy Regel True ist, dann drucke das Trade Statement und sende eine Market Buy Order mittels Binance API für das entsprechende Asset und die festgelegte Ordersize
                    elif is_long == True and should_sell == True:
                        print(f'+++ TRADE +++ We are selling {order_size} {asset}')
                        order = binance_api.order_market_sell(symbol=f'{asset}USDT', quantity=order_size)
                        asset_info['is_long'] = False
                        # Schreib den Trade in das orderbook.csv
                        write_order_to_csv('Sell', asset, order_size, latest_close, latest_close_time_gmt_minus_1.strftime("%Y-%m-%d %H:%M"))

            except Exception as e:
                # Ergänze ein weiteren Error Log im File optimistprimetader.log für den Datenimport, nachdem hier die meisten Komplikationen auftreten
                print(f"An error occurred while processing {asset}: {str(e)}")

        print(assets)
        print("*" * 20)
        time.sleep(5)

    except Exception as e:
        # Logge die Errors im optimistprimetrade.log
        logging.error(f'Script encountered the following error: {str(e)}', exc_info=True)