import re

import parse
import pdfplumber
import pandas as pd
from collections import namedtuple

transaction_date = re.compile(r'^\d\d\/\d\d')
transaction_amount = re.compile(r'\d+\.\d\d$')

file = '20210921-statements-0025.pdf'
lines = []
total_check = 0

dates = []
merchants = []
amounts = []


with pdfplumber.open(file) as pdf:
    pages = pdf.pages
    for page in pdf.pages:
        text = page.extract_text()
        for line in text.split('\n'):
            has_date = transaction_date.search(line) #if line starts with a date of format MM/DD
            actual_transaction = transaction_amount.search(line) #if line ends with a dollar amount of format DD+.DD
            if has_date:
                if actual_transaction: 
                    #print(line)
                    dates += [has_date.group()]
                    merchants.append(line[5:-10])
                    amounts += [actual_transaction.group()]

print (dates, merchants, amounts)
zipped = list(zip(dates, merchants, amounts))
df = pd.DataFrame(zipped, columns=['Date', 'Merchant', 'Amount'])

print(df.head())
df.to_csv('20210921-statements-0025.csv', index=False)