#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 22:12:33 2021

@author: mani
"""

import requests
import json
import datetime

webhook_url = "http://4e1bbb216382.in.ngrok.io"   





data = { 
    "stocks": "AMARAJABAT",
    "trigger_prices": "3.75,541.8,2.1,0.2,329.6,166.8,1.25",
    "triggered_at": "3:00 am",
    "scan_name": "Short term breakouts",
    "scan_url": "short-term-breakouts",
    "alert_name": "sell",
    "webhook_url": "http://your-web-hook-url.com"
}  

r = requests.post(webhook_url, data=json.dumps(data), headers={'Content-Type': 'application/json'})

