from pathlib import Path
import re
import pdfplumber
import pandas as pd

pdfs = []
for pdf in Path("../Bank Statements/Chase College Checking/pdfs/").glob("*.pdf"):
    pdfs.append(pdf)


transaction_date = re.compile(r'^\d+\/\d\d') #handle dates in MM/DD format
transaction_amount = re.compile(r'(\d+\,)?\d+\.\d\d$') #handle amounts over 1000, including commas

dates = []
merchants = []
amounts = []

openfile = sorted(pdfs)[0]

with pdfplumber.open(openfile) as pdf:
    pages = pdf.pages

    first_page = pdf.pages[0]
    lines = first_page.extract_text().split("\n")
    year = None
    while not year:
        for line in lines:
            if "through" in line:
                year = re.search(r"\d{4}", line).group()

    for page in pdf.pages:
        text = page.extract_text()

        month_for_prev_transaction = None

        for line in text.split('\n'):
            has_date = transaction_date.search(line) #if line starts with a date of format MM/DD
            actual_transaction = transaction_amount.search(line) #if line ends with a dollar amount of format DD+.DD
            print(line)
            if has_date:
                if actual_transaction:

                    month = has_date.group().split('/')[0]
                    day = has_date.group().split('/')[1]

                    if month == '01' and month_for_prev_transaction == '12':
                        year = str(int(year) + 1)

                    dates += [f"{year}-{month}-{day}"]
                    merchants.append(line[5:-5])
                    amounts += [actual_transaction.group()]

                    month_for_prev_transaction = month

#print (dates, merchants, amounts)
zipped = list(zip(dates, merchants, amounts))
df = pd.DataFrame(zipped, columns=['Date', 'Description', 'Amount'])

df.Description.iloc[0]
