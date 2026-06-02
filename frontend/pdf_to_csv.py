import pdfplumber
import pandas as pd

with pdfplumber.open("transaction_table.pdf") as pdf:
    text = pdf.pages[0].extract_text()

rows = [line.split() for line in text.split("\n")[1:]]

df = pd.DataFrame(rows, columns=[
    "User_ID",
    "Transaction_Type",
    "Amount",
    "Date",
    "Time1",
    "Time2"
])

df["Time"] = df["Time1"] + " " + df["Time2"]

df = df.drop(columns=["Time1", "Time2"])

credit_df = df[df["Transaction_Type"] == "Credit"]
debit_df = df[df["Transaction_Type"] == "Debit"]

with open("transactions.csv", "w", newline="") as file:

    file.write("CREDIT TRANSACTIONS\n")
    credit_df.to_csv(file, index=False)
  
    file.write("\n")
  
    file.write("DEBIT TRANSACTIONS\n")
    debit_df.to_csv(file, index=False)

print("Single CSV file created successfully")