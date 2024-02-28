[![python](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python&logoColor=FFD43B)](https://docs.python.org/3.10/)
![gmail](https://img.shields.io/badge/gmail-API-white?style=for-the-badge&logo=gmail)

# Gmail Reporting

Report on (unread) emails from your Gmail account.

Provides output as a list of emails, grouped by from-address and ordered by number of unread.

## Setup

Requires Python 3.10 or greater.

Setup your Gmail account to use the built-in Google API by following the instructions at https://developers.google.com/gmail/api/quickstart/python#set_up_your_environment.

Then install the application:

```sh
python -m venv venv
pip install -r requirements.txt
```

## Usage

Remove old files:

```sh
rm messages.csv
rm token.json
```

Get latest data:

```sh
$ python quickstart.py
from_address
notifications@email.com     23
no-reply@bank.com           14
support@it.com               5
info@this.com                1
info@that.com                1
foo@bar.com                  1
```

The unread email list is saved locally after download as `messages.csv`.  
Delete this file before running the script to pull an updated list.

## About

Inspired by Gmail's poor sorting ability and based on the [Gmail API Python Quickstart](https://developers.google.com/gmail/api/quickstart/python).
