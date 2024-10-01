import re
from pathlib import Path

import pandas as pd
import pdfplumber

transaction_date = re.compile(r"^\d+\/\d\d")  # handle dates in MM/DD format
transaction_amount = re.compile(
    r"(\d+\,)?\d+\.\d\d$"
)  # handle amounts over 1000, including commas

pdfs = []
for pdf in Path("../Bank Statements/Chase College Checking/pdfs/").glob("*.pdf"):
    pdfs.append(pdf)
pdfs = sorted(pdfs)

for file in pdfs:
    with open(file, "rb") as f:

        with pdfplumber.open(f) as pdf:
            print(file)

            dates = []
            merchants = []
            amounts = []
            balances = []

            first_page = pdf.pages[0]
            lines = first_page.extract_text().split("\n")
            year = None
            while not year:
                for line in lines:
                    if "through" in line:
                        startdate, enddate = line.split("through")
                        year = startdate.split()[-1]
                        break

            for page in pdf.pages:
                text = page.extract_text()

                month_for_prev_transaction = None

                for line in text.split("\n"):
                    has_date = transaction_date.search(
                        line
                    )  # if line starts with a date of format MM/DD
                    actual_transaction = transaction_amount.search(
                        line
                    )  # if line ends with a dollar amount of format DD+.DD

                    if has_date:
                        if actual_transaction:
                            # print(line.split())
                            month = has_date.group().split("/")[0]
                            day = has_date.group().split("/")[1]

                            if month == "01" and month_for_prev_transaction == "12":
                                year = str(int(year) + 1)

                            dates += [f"{year}-{month}-{day}"]
                            merchants.append(" ".join(line.split()[1:-2]))
                            amounts += [line.split()[-2]]
                            balances += [actual_transaction.group()]

                            month_for_prev_transaction = month

            zipped = list(zip(dates, merchants, amounts, balances))
            df = pd.DataFrame(
                zipped, columns=["Date", "Description", "Amount", "Balance"]
            )

            df.to_csv(
                f"../Bank Statements/Chase College Checking/csvs/{year}-{month}.csv"
            )
