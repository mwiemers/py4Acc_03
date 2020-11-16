# -*- coding: utf-8 -*-

"""
A function to scrap income and balance sheets from yahoo finance.

"""

__author__ = 'Michael Wiemers <michael.wiemers84@gmail.com'
__version__ = '0.1'
__revision__ = ''
__date__ = '02/10/2020'



import pandas as pd
from bs4 import BeautifulSoup
import requests


def yf_financials(tkr, type_):
    """
    Scrape and parse the balance sheet or income statement from finance.yahoo.com and
    return as a dataframe with dates as index and financial variables in columns.
    
    Arugments: 
    - tkr : stock ticker
    - type_ : "bs" (balance sheet) or "is" (income statement)
    
    Returns: 
    - financial table as pandas DataFrame
    """
    
    # set url
    if type_=="is":
        url = 'https://finance.yahoo.com/quote/' + tkr +'/financials?p=' + tkr
    elif type_ == "bs":
        url = 'https://finance.yahoo.com/quote/' + tkr +'/balance-sheet?p=' + tkr
    else:
        raise ValueError("Please pass 'bs' or 'is' as type_")
    
    # read html and create soup
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    
    table = soup.find_all('div', class_='D(tbr)')
    fin_list = [[cell.text for cell in table[i].find_all('span')] for i in range(len(table))]
    
    # convert to dataframe
    fin_df = pd.DataFrame(fin_list)
    
    # data wrangling
    fin_df = fin_df.transpose() # transpose df: switch rows and columns
    fin_df.columns = fin_df.iloc[0] # set column names to values in first row
    fin_df.drop(fin_df.index[0], inplace=True) # remove first row
    fin_df.rename(columns={'Breakdown' : 'Date'}, inplace=True) # rename column
    fin_df.set_index('Date', inplace=True) # set Date column as index
    fin_df['Comp'] = tkr # add new column for name of tech company
   
    # reorder columns to put Comp column first
    cols = fin_df.columns.to_list()
    cols = [cols[-1]] + cols[:-1]
    fin_df = fin_df[cols]
    
    # convert numerical values to float
    fin_df.loc[:, fin_df.columns != 'Comp'] = fin_df.loc[:, fin_df.columns != 'Comp'].replace(',', '', regex=True)
    fin_df[fin_df.columns[1:]] = fin_df[fin_df.columns[1:]].astype(float)
    
    return fin_df

