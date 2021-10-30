#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 24 08:58:47 2021

@author: mani
"""

from kiteconnect import KiteConnect
import mysql.connector
import os
import pandas as pd
import time

mydb = mysql.connector.connect(host = "localhost", user="root",password="slsamggt3", database = "supreme")
cwd = os.chdir("/Users/mani/Downloads/final_app")

access_token = open("access_token.txt",'r').read()
key_secret = open("zerodhaCred.txt",'r').read().split()
kite = KiteConnect(api_key=key_secret[0])
kite.set_access_token(access_token)
mis_stocks = pd.read_csv('misnew.csv')
vv = (mis_stocks["Stocks allowed for MIS"])

mycursor = mydb.cursor()

mycursor.execute("DROP TABLE websocket_buy_stocks")
mycursor.execute("DROP TABLE websocket_sell_stocks")
mycursor.execute("DROP TABLE stocks_brought")
mycursor.execute("DROP TABLE stocks_brought_sell")
mycursor.execute("DROP TABLE stocksCircuitInformation")


# -------------------------- Upstorx databases -------------

# mycursor.execute("DROP TABLE websocket_buy_stocks_up")
# mycursor.execute("DROP TABLE websocket_sell_stocks_up")
# mycursor.execute("DROP TABLE stocks_brought_up")
# mycursor.execute("DROP TABLE stocks_brought_sell_up")
# mycursor.execute("DROP TABLE stocksCircuitInformation_up")


# -------------------------- Upstorx databases -------------


mydb.commit()
mycursor.close()

mycursor = mydb.cursor()
# mycursor.execute("CREATE TABLE IF NOT EXISTS buyTenMin (stock varchar(20) primary key, ts datetime,validityPrice real(15,5),breakoutPrice real(15,5),volume real(15,5));")
# mycursor.execute("CREATE TABLE IF NOT EXISTS sellTenMin (stock varchar(20) primary key, ts datetime,validityPrice real(15,5),breakoutPrice real(15,5),volume real(15,5));")
# mycursor.execute("CREATE TABLE IF NOT EXISTS broughtTenMin (stock varchar(20),targetOrder varchar(20) primary key,stopOrder varchar(20));")
# mycursor.execute("CREATE TABLE IF NOT EXISTS shortedTenMin (stock varchar(20),targetOrder varchar(20) primary key,stopOrder varchar(20));")
# mycursor.execute("CREATE TABLE IF NOT EXISTS buyFiveMin (stock varchar(20) primary key, ts datetime,validityPrice real(15,5),breakoutPrice real(15,5),volume real(15,5));")
# mycursor.execute("CREATE TABLE IF NOT EXISTS sellFiveMin (stock varchar(20) primary key, ts datetime,validityPrice real(15,5),breakoutPrice real(15,5),volume real(15,5));")
# mycursor.execute("CREATE TABLE IF NOT EXISTS broughtFiveMin (stock varchar(20),targetOrder varchar(20) primary key,stopOrder varchar(20));")
# mycursor.execute("CREATE TABLE IF NOT EXISTS shortedFiveMin (stock varchar(20),targetOrder varchar(20) primary key,stopOrder varchar(20));")
# mycursor.execute("CREATE TABLE IF NOT EXISTS buyThreeMin (stock varchar(20) primary key, ts datetime,validityPrice real(15,5),breakoutPrice real(15,5),volume real(15,5));")
# mycursor.execute("CREATE TABLE IF NOT EXISTS sellThreeMin (stock varchar(20) primary key, ts datetime,validityPrice real(15,5),breakoutPrice real(15,5),volume real(15,5));")
# mycursor.execute("CREATE TABLE IF NOT EXISTS broughtThreeMin (stock varchar(20),targetOrder varchar(20) primary key,stopOrder varchar(20));")
# mycursor.execute("CREATE TABLE IF NOT EXISTS shortedThreeMin (stock varchar(20),targetOrder varchar(20) primary key,stopOrder varchar(20));")
mycursor.execute("CREATE TABLE IF NOT EXISTS websocket_buy_stocks (stock varchar(20) primary key, ts datetime,validityPrice real(15,5),breakoutPrice real(15,5),volume real(15,5), candles varchar(20),breakoutHeight real(15,5));")
mycursor.execute("CREATE TABLE IF NOT EXISTS websocket_sell_stocks (stock varchar(20) primary key, ts datetime,validityPrice real(15,5),breakoutPrice real(15,5),volume real(15,5), candles varchar(20),breakoutHeight real(15,5));")
mycursor.execute("CREATE TABLE IF NOT EXISTS stocks_brought (stock varchar(20),targetOrder varchar(20) primary key,stopOrder varchar(20));")
mycursor.execute("CREATE TABLE IF NOT EXISTS stocks_brought_sell (stock varchar(20),targetOrder varchar(20) primary key,stopOrder varchar(20));")
mycursor.execute("CREATE TABLE IF NOT EXISTS stocksCircuitInformation (stock varchar(20),upper_circuit real(15,5),lower_circuit real(15,5));")

# -------------------------- Upstorx databases -------------
# mycursor.execute("CREATE TABLE IF NOT EXISTS websocket_buy_stocks_up (stock varchar(20) primary key, ts datetime,validityPrice real(15,5),breakoutPrice real(15,5),volume real(15,5), candles varchar(20),breakoutHeight real(15,5));")
# mycursor.execute("CREATE TABLE IF NOT EXISTS websocket_sell_stocks_up (stock varchar(20) primary key, ts datetime,validityPrice real(15,5),breakoutPrice real(15,5),volume real(15,5), candles varchar(20),breakoutHeight real(15,5));")
# mycursor.execute("CREATE TABLE IF NOT EXISTS stocks_brought_up (stock varchar(20),targetOrder varchar(20) primary key,stopOrder varchar(20));")
# mycursor.execute("CREATE TABLE IF NOT EXISTS stocks_brought_sell_up (stock varchar(20),targetOrder varchar(20) primary key,stopOrder varchar(20));")
# mycursor.execute("CREATE TABLE IF NOT EXISTS stocksCircuitInformation_up (stock varchar(20),upper_circuit real(15,5),lower_circuit real(15,5));")



# -------------------------- Upstorx databases -------------


mydb.commit()
quote_data = {}

for v in vv:
    try:
        quote_data[v] = kite.quote('NSE:{}'.format(v))
        uppercircuit = quote_data[v]['NSE:{}'.format(v)]["upper_circuit_limit"]
        lowerCircuit = quote_data[v]['NSE:{}'.format(v)]["lower_circuit_limit"]
        vals = [v,uppercircuit,lowerCircuit]
        query = "INSERT INTO stocksCircuitInformation (stock,upper_circuit,lower_circuit) VALUES (%s,%s,%s)"
        mycursor.execute(query,vals)
        mydb.commit()
        # query = "INSERT INTO stocksCircuitInformation_up (stock,upper_circuit,lower_circuit) VALUES (%s,%s,%s)"
        # mycursor.execute(query,vals)
        # mydb.commit()
        time.sleep(0.1)
    except Exception as e:
        print(e)
        
mydb.commit()
mycursor.close()


"""
mycursor.execute("Select upper_circuit from stocksCircuitInformation where stock = 'RELIANCE'")
mycursor.fetchone()[0]

"""