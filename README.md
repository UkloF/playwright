# Playwright checkout test

Python browser automation for the Sauce Demo checkout flow. The script selects the highest- and lowest-priced products, verifies the checkout totals and 8% tax, and checks the order confirmation.

## Setup (Windows PowerShell)

Requires Python and Microsoft Edge.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m ensurepip --upgrade
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Run

```powershell
.\.venv\Scripts\python.exe 67160152.py
```

The script opens Microsoft Edge with a visible browser window and uses the public Sauce Demo test account.
