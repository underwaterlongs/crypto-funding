# -*- coding: utf-8 -*-
"""
Created on Sun Jan 17 23:14:16 2021

@author: yukih

Python naming convention:
UpperCamelCase for class names, 
CAPITALIZED_WITH_UNDERSCORES for constants, 
lowercase_separated_by_underscores for other names.

"""
import time
import hmac
from requests import Request, Session, Response
from typing import Optional, Dict, Any, List
import os

os_api_key = os.environ['FTX_API_KEY']
os_api_secret = os.environ['FTX_API_SECRET']

class FTXClient:
    _ENDPOINT = 'https://ftx.com/api/'
    
    def __init__(self, api_key=None, api_secret=None, subaccount_name=None) -> None:
        self._session = Session()
        self._api_key = api_key
        self._api_secret = api_secret
        self._subaccount_name = subaccount_name
        
    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request('GET', path, params=params)        
    
    def _request(self, method: str, path: str, **kwargs) -> Any:
        request = Request(method, self._ENDPOINT + path, **kwargs)
        self._sign_request(request)
        response = self._session.send(request.prepare())
        return self._process_response(response)

    def _sign_request(self, request: Request) -> None:
        ts = int(time.time() * 1000)
        prepared = request.prepare()
        signature_payload = f'{ts}{prepared.method}{prepared.path_url}'.encode()
        if prepared.body:
            signature_payload += prepared.body
        signature = hmac.new(self._api_secret.encode(), signature_payload, 'sha256').hexdigest()
        request.headers['FTX-KEY'] = self._api_key
        request.headers['FTX-SIGN'] = signature
        request.headers['FTX-TS'] = str(ts)
        if self._subaccount_name:
            request.headers['FTX-SUBACCOUNT'] = urllib.parse.quote(self._subaccount_name)

    def _process_response(self, response: Response) -> Any:
        try:
            data = response.json()
        except ValueError:
            response.raise_for_status()
            raise
        else:
            if not data['success']:
                raise Exception(data['error'])
            return data['result']
        
    def get_balances(self) -> List[dict]:
        return self._get('wallet/balances')
    
    # get mark price of a single future
    def get_price(self, future: str) -> float:
        return self._get(f'/futures/{future}')['mark']
    
    # get a list of futures dict
    def get_futures(self) -> List[dict]:
        return self._get(f'futures')
    
    def get_future(self, future: str) -> dict:
        return self._get(f'futures/{future}')
    
    # get stats for a single future
    def get_stats(self, future: str) -> dict:
        return self._get(f'/futures/{future}/stats')
    
    # get a list of markets
    def get_markets(self) -> List[dict]:
        return self._get(f'markets')    
    
    # get a specific market by passing in the market name
    def get_market(self, market: str) -> dict:
        return self._get(f'markets/{market}')
    
