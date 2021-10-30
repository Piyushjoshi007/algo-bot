#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 14 13:02:34 2021



@author: mani
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 09:31:18 2021

@author: mani
"""


from kiteconnect import KiteConnect
import pandas as pd
import time
import datetime
import os
import mysql.connector
import telegram



mydb = mysql.connector.connect(host = "localhost", user="root",password="slsamggt3", database = "supreme")
cwd = os.chdir("/Users/mani/Downloads/final_app")

access_token = open("access_token.txt",'r').read()
key_secret = open("zerodhaCred.txt",'r').read().split()
kite = KiteConnect(api_key=key_secret[0])
kite.set_access_token(access_token)
mis_stocks = pd.read_csv('misnew.csv')
# vv = (mis_stocks["Stocks allowed for MIS"])

    


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

def notify_ending(message):
    token = "telegram_token"
    chat_id = "telegram_chat_ID"
    bot = telegram.Bot(token=token)
    bot.sendMessage(chat_id=chat_id, text=message) 

    
############################code to find ohlc #########

def fetchOHLC(ticker,interval,duration):
    """extracts historical data and outputs in the form of dataframe"""
    instrument = instrumentLookup(instrument_df,ticker)
    time = datetime.datetime.now() - datetime.timedelta(minutes= duration)
    data = pd.DataFrame(kite.historical_data(instrument,time,datetime.datetime.now(),interval))
    data.set_index("date",inplace=True)
    return data


def fetchLtp(ticker):
    """extracts historical data and outputs in the form of dataframe"""
    instrument = instrumentLookup(instrument_df,ticker)
    data = kite.ltp(instrument)
    pp = data[str(instrument)]['last_price']
    return pp

def myround(x, base=0.05):
    return round(base * round(x/base),2)
#----------------------------------------------------------

targetOrder = {}
stopOrder = {}
############################c extract data from file #########

def buy(stock):
    print ("buylogic")
    mycursor = mydb.cursor(buffered = True)
    mycursor.execute("Select ts from websocket_buy_stocks where stock = '{}'".format(stock))
    timee = mycursor.fetchone()[0]
    mycursor.execute("Select candles from websocket_buy_stocks where stock = '{}'".format(stock))
    cand = int(mycursor.fetchone()[0])
    no_of_candles = (divmod((datetime.datetime.now() - timee).total_seconds(),60)[0] + cand)
    ohlc_buy = fetchOHLC(stock,"minute",(no_of_candles))
    stopLoss = min(ohlc_buy["low"]) 
    stopLoss = myround(stopLoss)
    buy_price = myround(fetchLtp(stock))
    stoploss_length = (buy_price - stopLoss)
    # quantity = 1
    # target = myround(buy_price + (stoploss_length * 1.1))
    target = myround(buy_price - (stoploss_length * 0.4))
    stoploss_length = (buy_price - target)
    quantity = int(divmod(400, stoploss_length)[0])
    stopLoss = myround(buy_price + stoploss_length/2)


    
    
    try:
        mycursor.execute("Select upper_circuit from stocksCircuitInformation where stock = '{}'".format(stock))
        circuit_limit = mycursor.fetchone()[0]
    except Exception as e :
        circuit_limit = 0
        print(e)  
    mycursor.close()

    if(quantity > 0 and stopLoss < circuit_limit):
        try:
            # t_type=kite.TRANSACTION_TYPE_BUY
            # t_type_sl=kite.TRANSACTION_TYPE_SELL
            # market_order = kite.place_order(tradingsymbol=stock,
            #                 exchange=kite.EXCHANGE_NSE,
            #                 transaction_type=t_type,
            #                 quantity=quantity,
            #                 order_type=kite.ORDER_TYPE_MARKET,
            #                 product=kite.PRODUCT_MIS,
            #                 variety=kite.VARIETY_REGULAR)
            # print("placed a buy order in market conditions for stock : {} with quantity : {},stoplossLength : {}, no_of_candles : {}, stopLoss : {}, buyPrice: {}, target:{} ,time :{}".format(stock,quantity,stoploss_length,no_of_candles,stopLoss,buy_price,target,datetime.datetime.now()))
            # time.sleep(0.2)
           
            # # a = 0
            # # while a < 10:
            # #     try:
            # #         order_list = kite.orders()
            # #         break
            # #     except:
            # #         print("can't get orders..retrying")
            # #         a+=1
            # # for order in order_list:
            # #     if order["order_id"]==market_order:
            # #         if order["status"]=="COMPLETE":
            # stopOrder[stock] = kite.place_order(tradingsymbol=stock,
            #                 exchange=kite.EXCHANGE_NSE,
            #                 transaction_type=t_type_sl,
            #                 quantity=quantity,
            #                 order_type=kite.ORDER_TYPE_SLM,
            #                 price=stopLoss,
            #                 trigger_price = stopLoss,
            #                 product=kite.PRODUCT_MIS,
            #                 variety=kite.VARIETY_REGULAR)
            
            # print("stoploss order placed for stock: {}",format(stock)) 
            
            # targetOrder[stock] = kite.place_order(tradingsymbol=stock,
            #                 exchange=kite.EXCHANGE_NSE,
            #                 transaction_type=t_type_sl,
            #                 quantity=quantity,
            #                 order_type=kite.ORDER_TYPE_LIMIT,
            #                 price=target,
            #                 # trigger_price = target,
            #                 product=kite.PRODUCT_MIS,
            #                 variety=kite.VARIETY_REGULAR)
            
            # print("Target order placed for stock: {}",format(stock))
            
            t_type=kite.TRANSACTION_TYPE_SELL
            t_type_sl=kite.TRANSACTION_TYPE_BUY
            market_order = kite.place_order(tradingsymbol=stock,
                            exchange=kite.EXCHANGE_NSE,
                            transaction_type=t_type,
                            quantity=quantity,
                            order_type=kite.ORDER_TYPE_MARKET,
                            product=kite.PRODUCT_MIS,
                            variety=kite.VARIETY_REGULAR)
            print("placed a sell order in market conditions for stock : {} with quantity : {},stoplossLength : {}, no_of_candles : {}, stopLoss : {}, sellPrice: {}, target:{} ,time :{}".format(stock,quantity,stoploss_length,no_of_candles,stopLoss,buy_price,target,datetime.datetime.now()))
            time.sleep(0.2)
            
            # a = 0
            # while a < 10:
            #     try:
            #         order_list = kite.orders()
            #         break
            #     except:
            #         print("can't get orders..retrying")
            #         a+=1
            # for order in order_list:
            #     if order["order_id"]==market_order:
            #         if order["status"]=="COMPLETE":
                
            stopOrder[stock] = kite.place_order(tradingsymbol=stock,
                            exchange=kite.EXCHANGE_NSE,
                            transaction_type=t_type_sl,
                            quantity=quantity,
                            order_type=kite.ORDER_TYPE_SLM,
                            price=stopLoss,
                            trigger_price = stopLoss,
                            product=kite.PRODUCT_MIS,
                            variety=kite.VARIETY_REGULAR)
            print("stoploss order placed for stock: {}",format(stock)) 

            targetOrder[stock] = kite.place_order(tradingsymbol=stock,
                            exchange=kite.EXCHANGE_NSE,
                            transaction_type=t_type_sl,
                            quantity=quantity,
                            order_type=kite.ORDER_TYPE_LIMIT,
                            price=target,
                            # trigger_price = target,
                            product=kite.PRODUCT_MIS,
                            variety=kite.VARIETY_REGULAR)
            
           
            print("Target order placed for stock: {}",format(stock))
            mycursor=mydb.cursor() 
            vals = [stock,targetOrder[stock],stopOrder[stock]]
            query = "INSERT INTO stocks_brought (stock,targetOrder,stopOrder) VALUES (%s,%s,%s)"
            mycursor.execute(query,vals)
            mydb.commit()
            mycursor.close()
            mycursor=mydb.cursor()                         
            mycursor.execute("Delete from websocket_buy_stocks where stock = '{}'".format(stock))
            mydb.commit()
            mycursor.close()
            print("deleted stock as order placed : {}".format(stock)) 
                    # else:
                    #     kite.cancel_order(order_id=market_order,variety=kite.VARIETY_REGULAR)  
        except Exception as e:
            mycursor = mydb.cursor()
            mycursor.execute("Delete from websocket_buy_stocks where stock = '{}'".format(stock))
            mydb.commit()
            mycursor.close()
            print("deleted stock as stock not currently in mis list placed : {}".format(stock)) 
            print(e) 
        
    else:
        print("invalid quantity for stock {}".format(stock)) 
        mycursor = mydb.cursor()
        mycursor.execute("Delete from websocket_buy_stocks where stock = '{}'".format(stock))
        mydb.commit()
        mycursor.close()
        print("deleted stock as stock not currently in mis list placed : {}".format(stock))            
    
    
def CancelOrder(order_id):    
    kite.cancel_order(order_id=order_id,
                    variety=kite.VARIETY_REGULAR,parent_order_id=None) 
#----------------------------------------------------------


def buy_logic(stock):
    mycursor = mydb.cursor(buffered = True)
    a = 0
    while a <= 15 :
        try:
            # ohlc_latest = fetchOHLC(stock,"minute",3)
            ohlc_latest = fetchOHLC(stock,"minute",5)            
            break
        except:
            notify_ending("Something is wrong with buy script")     
            print("can't get ohlc values ..retrying")
            a+=1 
        
    try:        
        # latest_close_min = min(ohlc_latest["close"])
        # latest_close_max = max(ohlc_latest["close"]) 
        latest_close_min = ohlc_latest["low"][-2]
        latest_close_max = ohlc_latest["close"][-2]
        # mycursor.execute("Select ts from websocket_buy_stocks where stock = '{}'".format(stock))
        # timee = mycursor.fetchone()[0]
        # no_of_candles = (divmod((datetime.datetime.now() - timee).total_seconds(),60)[0])
        # ohlc_volume = fetchOHLC(stock,"minute",3)
        # latest_close_volume_max = max(ohlc_volume["volume"])
        latest_close_volume_max = ohlc_latest["volume"][-2]
        latest_close_volume_max = latest_close_volume_max + (latest_close_volume_max * 0.05)
        mycursor.execute("select validityPrice from websocket_buy_stocks where stock = '{}'".format(stock))
        validPrice = mycursor.fetchone()[0]
        mycursor.execute("select volume from websocket_buy_stocks where stock = '{}'".format(stock))
        breakoutvolume = mycursor.fetchone()[0]
        mycursor.execute("select breakoutHeight from websocket_buy_stocks where stock = '{}'".format(stock))
        breakoutHeight = mycursor.fetchone()[0]
        mycursor.execute("select breakoutPrice from websocket_buy_stocks where stock = '{}'".format(stock))
        breakoutpp = mycursor.fetchone()[0]
        mycursor.close()
        
        # height= 0
        # bodyRatio = 0
        
        # if((ohlc_latest["close"][0] - ohlc_latest["open"][0]) == 0 or (ohlc_latest["high"][0] - ohlc_latest["low"][0]) == 0):
        #     pass
        # else:
        #     bodyRatio = ((ohlc_latest["close"][0] - ohlc_latest["open"][0])/(ohlc_latest["high"][0] - ohlc_latest["low"][0])) * 100
        #     height = ohlc_latest["high"][0] - ohlc_latest["low"][0]
        #     height = height + (height * 0.7) 
        
        latest_close_min = latest_close_min - (breakoutHeight * 0.1)
        if (latest_close_max < validPrice):
            mycursor = mydb.cursor()
            mycursor.execute("Delete from websocket_buy_stocks where stock = '{}'".format(stock))
            mydb.commit()
            mycursor.close()
            print("deleted stock : {}".format(stock)) 
            # height = 0
            # bodyRatio = 0
    
        # and height >= breakoutHeight and bodyRatio >= 30.0
        elif (latest_close_max > breakoutpp and latest_close_volume_max >= breakoutvolume  and latest_close_min <= breakoutpp):
            # height = 0
            # bodyRatio = 0
            buy(stock)
            
        elif(latest_close_max > breakoutpp and latest_close_min <= breakoutpp):
            if(ohlc_latest["volume"][-3] >= breakoutvolume  and ohlc_latest["open"][-3] <= ohlc_latest["close"][-3] and ohlc_latest["low"][-3] <= breakoutpp and ohlc_latest["open"][-4] <= ohlc_latest["close"][-4]):
                buy(stock) 
                
            elif(ohlc_latest["volume"][-4] >= breakoutvolume and ohlc_latest["open"][-4] <= ohlc_latest["close"][-4] and ohlc_latest["low"][-4] <= breakoutpp and ohlc_latest["open"][-3] <= ohlc_latest["close"][-3]):
                buy(stock) 
                
            # elif(ohlc_latest["volume"][-5] >= breakoutvolume and ohlc_latest["open"][-5] <= ohlc_latest["close"][-5] and ohlc_latest["low"][-5] <= breakoutpp):
            #     buy(stock) 
            
        elif (latest_close_max > breakoutpp):
            if (latest_close_min<= breakoutpp):
                print(latest_close_min)
                print("stock {} still in breakout range".format(stock))
            
            else:
                print(latest_close_min)
                mycursor = mydb.cursor()
                mycursor.execute("Delete from websocket_buy_stocks where stock = '{}'".format(stock))
                mydb.commit()
                mycursor.close()
                print("deleted stock because of volume : {}".format(stock)) 
                # height = 0
                # bodyRatio = 0
                
    except:
        print("skipping passthrough for stock {} ".format(stock))                

       

def main():
    mycursor = mydb.cursor(buffered = True)
    mycursor.execute('Select stock from websocket_buy_stocks')
    mydb.commit()
    mycursor.close() 
    
    
    for row in mycursor:
        print("passing passtrough from {}".format(row[0]))
        buy_logic(row[0])
        
            
    mycursor = mydb.cursor(buffered = True)      
    mycursor.execute('Select stock from stocks_brought') 
    mydb.commit()
    broughted_stocks = mycursor.fetchall()
    a = 0
    while a < 10:
        try:
            order_list = kite.orders()
            break
        except:
            print("can't get orders..retrying")
            a+=1 
    for name in broughted_stocks:  
        mycursor.execute("Select stopOrder from stocks_brought where stock = '{}'".format(name[0]))
        stopOrderPrice = mycursor.fetchone()[0]
        mycursor.execute("Select targetOrder from stocks_brought where stock = '{}'".format(name[0]))
        targetOrderPrice = mycursor.fetchone()[0]
        for order in order_list :
           if order["order_id"] == stopOrderPrice:  
               if order["status"]=="COMPLETE":
                    attempt = 0
                    while  attempt<5:
                        try:
                            CancelOrder(targetOrderPrice)
                            print("order squared off = {}".format(name[0]))
                            mycursor.execute("Delete from stocks_brought where targetOrder = {}".format(targetOrderPrice))
                            mydb.commit()
                            break
                        except:
                            print("unable to delete order id : ",targetOrderPrice)
                            attempt+=1
                       
           elif order['order_id'] == targetOrderPrice:
               if order["status"]=="COMPLETE":              
                    attempt = 0
                    while  attempt<5:
                        try:
                            CancelOrder(stopOrderPrice)
                            print("order squared off = {}".format(name[0]))
                            mycursor.execute("Delete from stocks_brought where stopOrder = {}".format(stopOrderPrice))
                            mydb.commit()
                            break
                            
                        except:
                            print("unable to delete order id : {}".format(stopOrderPrice))
                            attempt+=1
                          
             
    mycursor.close()                       
              
                          
                    
count = 0    
starttime=time.time()
timeout = time.time() + 60*60*7  # 60 seconds times 360 meaning 6 hrs
while time.time() <= timeout:
    try:            
        main()
        count = count+1
        print("{} minute passed -------- -------".format(count))
        time.sleep(60 - ((time.time() - starttime) % 60.0))
    except KeyboardInterrupt:
        notify_ending("Something is wrong with buy script")     
        print('\n\nKeyboard exception received. Exiting.')
        exit()    
        
        
notify_ending("Something is wrong with buy script")     
    

"""
mycursor.execute('Select stock from stocks_brought')
mycursor.fetchall()

c.execute('SELECT stock from websocket_buy_stocks')
c.fetchall()

c.execute('''PRAGMA table_info(TOKEN975873)''')
c.fetchall()

for m in c.execute('''SELECT * FROM ACC'''):
    print(m)
"""     


    