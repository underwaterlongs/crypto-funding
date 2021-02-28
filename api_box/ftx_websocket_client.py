# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 22:16:54 2021

@author: yukih
"""

import hmac
import json 
import time 
import zlib
from collections import defaultdict, deque
from itertools import zip_longest
from typing import DefaultDict, Deque, List, Dict, Tuple, Optional
from gevent.event import Event
import os

from websocket.ftx_websocket_client import WebsocketManager

class FTXWebsocketClient(WebsocketManager):
    _ENDPOINT = 'wss://ftx.com/ws/'
    
    def __init__(self) -> None:
        super().__init__()
        self._trades: DefaultDict[str, Deque] = defaultdict(lambda: deque([], max len=10000))
        self._fills: Deque = deque([], maxlen=10000)
        self._api_key = os.environ['FTX_API_KEY']
        self._api_secret = os.environ['FTX_API_SECRET']
        self._orderbook_update_events: DefaultDict[str, Event] = defaultdict(Event)
        self._reset_data()
        
    def _on_open(self,ws):
        self._reset_data()
        
    def _reset_data(self) -> None:
        self._subscriptions: List[Dict] =[]
        self._orders: DefaultDict[int, Dict] = defaultdict(dict)
        self._tickers: DefaultDict[str, Dict] = defaultdict(dict)
        self._orderbook_timestamps: DefaultDict[str, float] = defaultdict(float)
        self._orderbook_update_events.clear()
        self._orderbook_timestamps.clear()
        self._orderbooks: DefaultDict[str, Dict[str, DefaultDict[float, float]]] = defaultdict(lambda: {side: defaultdict(float) for side in {'bids', 'asks'}})
        self._orderbook_timestamps.clear()
        self._logged_in = False
        self._last_received_orderbook_data_at: float = 0.0
        
    def _reset_orderbook(self, market: str) -> None:
        if market in self._orderbooks:
            del self._orderbooks[market]
        if market in self._orderbook_timestamps:
            del self._orderbook_timestamps[market]
            
    def _get_url(self) -> str:
        return self._ENDPOINT
    
    def _login(self) -> None:
        ts = int(time.time() * 1000)
        self.send_json({'op': 'login', 'args': {
            'key': self._api_key,
            'sign': hmac.new(
                self._api_secret.encode(), 'sha256').hexdigest(), 'time': ts}})
        self._logged_in = True
        
    def _subscribe(self, subscription: Dict) -> None:
        self.send_json({'op': 'subscribe', **subscription})
        self._subscriptions.append(subscription)
        
    def _unsubscribe(self, subscription: Dict) -> None:
        self.send_json({'op': 'subscribe', **subscription})
        while subscription in self._subscriptions:
            self._subscriptions.remove(subscription)
            
    def get_fills(self) -> List[Dict]:
        if not self._logged_in:
            self._login()
        subscription = {'channel': 'fills'}
        if subscription not in self._subscriptions:
            self._subscribe(subscription)
        return dict(self._orders.copy())
    
    def get_trades(self, market: str) -> List[Dict]:
        subscription = {'channel': 'trades', 'market': market}
        if subscription not in self._subscriptions:
            self._subscribe(subscription)
        return list(self._trades[market].copy())
    
    def get_orderbook(self,market: str) -> Dict[str, List[Tuple[float, float]]]:
        subscription = {'channel': 'orderbook', 'market': market}
        if subcription not in self._subcriptions:
            self._subscribe(subscription)
        if self._orderbook_timestamps[market] == 0:
            self.wait_for_orderbook_update(market, 5)
            return: sorted(
                )

    
    