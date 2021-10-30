#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 21:42:08 2021

@author: mani
"""


from flask import Flask, request, abort
from kiteconnect import KiteConnect
import pandas as pd
import datetime as dt
from selenium import webdriver
import time
import os
import datetime
import mysql.connector
import telegram


def notify_ending(message):
    token = "Telegram_token"
    chat_id = "telegram_chat_id"
    bot = telegram.Bot(token=token)
    bot.sendMessage(chat_id=chat_id, text=message)


mydb = mysql.connector.connect(host = "localhost", user="root",password="slsamggt3", database = "supreme")
cwd = os.chdir("/Users/mani/Downloads/final_app")
mis_stocks = pd.read_csv('misnew.csv')
vv = (mis_stocks["Stocks allowed for MIS"])


############################code to use access token and create a session ############################

def autologin():
    token_path = "zerodhaCred.txt"
    key_secret = open(token_path,'r').read().split()
    kite = KiteConnect(api_key=key_secret[0])
    service = webdriver.chrome.service.Service('./chromedriver')
    service.start()
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options = options.to_capabilities()
    driver = webdriver.Remote(service.service_url, options)
    driver.get(kite.login_url())
    driver.implicitly_wait(10)
    username = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[1]/input')
    password = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[2]/input')
    username.send_keys(key_secret[2])
    password.send_keys(key_secret[3])
    driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[4]/button').click()
    pin = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[2]/div/input')
    pin.send_keys(key_secret[4])
    driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[3]/button').click()
    time.sleep(10)    
    request_token=driver.current_url.split('=')[1].split('&action')[0]
    with open('request_token.txt', 'w') as the_file:
        the_file.write(request_token)
    driver.quit()

autologin()


#generating and storing access token - valid till 6 am the next day
request_token = open("request_token.txt",'r').read()
key_secret = open("zerodhaCred.txt",'r').read().split()
kite = KiteConnect(api_key=key_secret[0])
data = kite.generate_session(request_token, api_secret=key_secret[1])
with open('access_token.txt', 'w') as file:
        file.write(data["access_token"])




access_token = open("access_token.txt",'r').read()
key_secret = open("zerodhaCred.txt",'r').read().split()
kite = KiteConnect(api_key=key_secret[0])
kite.set_access_token(access_token)

#---------------------------------------------------------



############################ code to find all zerodha trading scripts number ############################

#get dump of all NSE instruments
instrument_dump = kite.instruments("NSE")
instrument_df = pd.DataFrame(instrument_dump)

def instrumentLookup(instrument_df,symbol):
    """Looks up instrument token for a given script from instrument dump"""
    try:
        return instrument_df[instrument_df.tradingsymbol==symbol].instrument_token.values[0]
    except:
        return -1

#-----------------------------------------------


############################code to find ohlc #########

def fetchOHLC(ticker,interval,duration):
    """extracts historical data and outputs in the form of dataframe"""
    instrument = instrumentLookup(instrument_df,ticker)
    data = pd.DataFrame(kite.historical_data(instrument,dt.date.today()-dt.timedelta(duration), dt.date.today(),interval))
    data.set_index("date",inplace=True)
    return data

#----------------------------------------------------------
  
def insert_ticks(stock,validityPrice,breakoutPrice,volume,candles,breakoutHeight):
    mycsursor = mydb.cursor()
    vals = [stock,datetime.datetime.now(),validityPrice,breakoutPrice,volume,candles,breakoutHeight]
    query = "INSERT INTO websocket_buy_stocks(stock,ts,validityPrice,breakoutPrice,volume,candles,breakoutHeight) VALUES (%s,%s,%s,%s,%s,%s,%s)"
    mycsursor.execute(query,vals)
    mydb.commit()
    mycsursor.close()
      
        
        
def insert_ticks_sell(stock,validityPrice,breakoutPrice,volume,candles,breakoutHeight):
    mycsursor = mydb.cursor()
    vals = [stock,datetime.datetime.now(),validityPrice,breakoutPrice,volume,candles,breakoutHeight]
    query = "INSERT INTO websocket_sell_stocks (stock,ts,validityPrice,breakoutPrice,volume,candles,breakoutHeight) VALUES (%s,%s,%s,%s,%s,%s,%s)"
    mycsursor.execute(query,vals)
    mydb.commit()     
    mycsursor.close()       

app = Flask(__name__)



@app.route('/', methods=['POST'])
def webhook():
    if request.method == 'POST':
        a = request.json
        stocks_names = a['stocks'].split(",")
        alert_name = a['alert_name']
        
        for x in range(0,len(stocks_names)):
            stock_name = stocks_names[x]
            
                
            if(alert_name == 'buy'):
                count = 0
                mycsursor = mydb.cursor(buffered = True)
                mycsursor.execute("select stock from websocket_buy_stocks")
                mydb.commit()
                mycsursor.close()
                for x in mycsursor:
                    if(x[0] == stock_name):
                        count = count +1
                        print("stock already exist in buy stocks list",x[0])
                        break
               
                        
                # for v in vv:
                if(count == 0):
                    ohlc = fetchOHLC(stock_name,"minute",4)
                    r = 0
                    l = -1
                    while(r<=48):
                        if (ohlc["volume"][l] > 0):
                            r = r+1
                            l = l-1
                        else:
                            l = l-1
                            
                    l = l+2   
                    df_valid_price = ohlc.iloc[l-30:l+1]
                    list_low = df_valid_price["low"]
                    list_low = list_low.iloc[::-1]
                    a = 0
                    while(a == 0):
                        for x,y in zip(list_low,list_low[1:]):
                            # y = y - (y*0.001)
                            if(x<y):
                                # valid_price = x - (x * 0.002)
                                valid_price = x
                                list_low = []
                                a = 1
                                break
                    one_more_valid = ohlc.iloc[l:,:]
                    volume_max = ohlc.iloc[l-1:l+10]
                    height= 0
                    for w,x,z,a,b in zip(volume_max["high"],volume_max["low"],volume_max["volume"],volume_max["open"],volume_max["close"]):
                        if (w-x >= height and b > a):
                            height = (w-x)
                            volume = z
                    # valid_price = valid_price - (height * 0.2)
                    if(min(one_more_valid['low']) >= valid_price):
                        df_breakout_price = ohlc.iloc[l-1:-38]
                        breakout_price = max(df_breakout_price['high'])
                        print(volume,height)
                        print(l)
                        insert_ticks(stock_name,valid_price,breakout_price,volume,abs(l),height)                       
                        print(stock_name, 'added to BUY dictionary with valid_price = {} and breakout_price = {} and volume = {},l = {},height = {}'.format(valid_price,breakout_price,volume,l,height))
                        # time.sleep(1)
                    else:
                       
                        print("check valid price of stock {} {}".format(stock_name,valid_price))
                        print(l)
                        r = 0
                        l = -1

                            
                            
                    
                         
            elif(alert_name == 'sell'):
                count = 0
                mycsursor = mydb.cursor(buffered = True)
                mycsursor.execute("select stock from websocket_sell_stocks")
                mydb.commit()
                mycsursor.close()
                for x in mycsursor:
                    if(x[0] == stock_name):
                        count = count +1
                        print("stock already exist in sell stocks list",x[0])
                        break
                
                    
                # for v in vv:   
                if(count == 0):
                    ohlc_sell = fetchOHLC(stock_name,"minute",4)
                    r = 0
                    l = -1
                    
                    while(r<=48):
                        if (ohlc_sell["volume"][l] > 0):
                            r = r+1
                            l = l-1
                        else:
                            l = l-1
                            
                    l = l+2
                    df_validComput_sell = ohlc_sell.iloc[l-30:l+1] 
                    list_low_sell = df_validComput_sell["high"]
                    list_low_sell = list_low_sell.iloc[::-1]
                    a = 0
                    while(a == 0):
                        for x,y in zip(list_low_sell,list_low_sell[1:]):
                            # y = y + (y*0.001)
                            if(x>y):
                                # sell_valid_price = x + (x * 0.002)
                                sell_valid_price = x 
                                list_low_sell = []
                                a = 1
                                break
                   
                    one_more_valid_sell = ohlc_sell.iloc[l:,:] 
                    volume_max_sell = ohlc_sell.iloc[l-1:l+10]
                    height= 0
                    for w,x,z,a,b in zip(volume_max_sell["high"],volume_max_sell["low"],volume_max_sell["volume"],volume_max_sell["open"],volume_max_sell["close"]):
                        if (w-x >= height and a > b):
                            height = (w-x)
                            volume = z
                    # sell_valid_price =   sell_valid_price + (height * 0.2)      
                    if(max(one_more_valid_sell['high']) <= sell_valid_price):
                        df_valid_breakout_sell = ohlc_sell.iloc[l-1:-38]
                        print(volume,height)                       
                        print(l)                        
                        sell_breakout_price = min(df_valid_breakout_sell['low']) 
                        insert_ticks_sell(stock_name,sell_valid_price,sell_breakout_price,volume,abs(l),height)                         
                        print(stock_name, 'added to SELL dictionary with valid price = {} and breakout_price = {} and volume = {}, l = {},height = {}'.format(sell_valid_price,sell_breakout_price,volume,l,height)) 
                        r = 0
                        l = -1
                    else:
                        
                        print("check valid price of stock {} {}".format(stock_name,sell_valid_price))
                        print(l)
                        r = 0
                        l = -1
                
        return ('success', 200)
    else:
        abort(400)
        
if __name__ == '__main__':
    app.run(threaded = True)
     
notify_ending("Something is wrong with main script")    

"""
c2.execute('SELECT * from websocket_buy_stocks')
c2.fetchall()

c.execute('SELECT stock from websocket_buy_stocks')
c.fetchall()

c.execute('''PRAGMA table_info(TOKEN975873)''')
c.fetchall()

for m in c.execute('''SELECT * FROM ACC'''):
    print(m)
"""  
    
    