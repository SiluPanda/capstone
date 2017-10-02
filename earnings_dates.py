import requests
from io import StringIO
import pandas as pd
import pathlib
from pandas.tseries.offsets import *

def download_earnings_dates(ticker_list):

    if pathlib.Path('earnings_release_dates.csv').exists():
        print('earnings_release_dates.csv found, loading from it.\nIf you want to download from NSE, delete this file')
        earnings_dates = pd.read_csv('earnings_release_dates.csv',parse_dates = ['BoardMeetingDate'])
        return earnings_dates

    earnings_dates = pd.DataFrame()
    i = 0
    for ticker in ticker_list:
        i = i + 1
        print('downloading ticker %d of %d: %s' %(i,len(ticker_list),ticker))
        response1 = requests.get('https://www.nseindia.com/corporates/datafiles/BM_' + ticker + 'Last_24_MonthsResults.csv')
        response2 = requests.get('https://www.nseindia.com/corporates/datafiles/BM_' + ticker + 'More_than_24_MonthsResults.csv')
        earnings_dates_last_24months = pd.DataFrame()
        earnings_dates_prior_to_24months = pd.DataFrame()
        if response1.content.decode().find('The requested object does not exist on this server') < 0:
            earnings_dates_last_24months = pd.read_csv(StringIO(response1.content.decode()))
        if response2.content.decode().find('The requested object does not exist on this server') < 0:
            earnings_dates_prior_to_24months = pd.read_csv(StringIO(response2.content.decode()))
        earnings_dates = pd.concat([earnings_dates,earnings_dates_last_24months,earnings_dates_prior_to_24months])
    print('Saving earnings_dates in earnings_release_dates.csv')
    earnings_dates.to_csv('earnings_release_dates.csv')
    return earnings_dates

def guess_quarter_end_date(earnings_dates):
    '''The earnings release dates downloaded from download_earnings_dates() have the BoardMeetingDate, 
    the date on which financial results are made public after the close of market-hours for the day. 

    But unfortunately, it does not explicitly state which quarter does the BoardMeetingDate
    refer to. We have checked for a few cases and found that earnings are released in within 
    #the next quarter. 

    So lets make an assumption here that QuarterEndDate is that of the immediately prior 
    quarter before the BoardMeetingDate and add such a column to earnings_dates and return'''

    ##The below is a class from offets module in pandas.tseries
    quarterEnd = QuarterEnd()

    #quarterEnd.rollback() is an instance method that takes a date and rolls it back to 
    #most recent quarter end date, exactly what we need! 
    earnings_dates['QuarterEndDate'] = earnings_dates.BoardMeetingDate.apply(quarterEnd.rollback)
    return earnings_dates

if __name__ == '__main__':
    tickers = ['RELIANCE', 'ICICIBANK']
    earnings_dates_list = download_earnings_dates(tickers)
    print(earnings_dates_list.head())