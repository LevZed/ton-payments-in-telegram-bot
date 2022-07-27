# ton-footstep-8

after cloning the repository, you can run the following command to install the dependencies:

`pip install -r requirements.txt`

Insert your tokens and wallets in the `config.json` file.

to start bot localy, run the following command:

`py bot/main.py`

It starts in testnet mode by default.
To run in mainnet mode, change "WORKMODE" in config.json from "testnet" to "mainnet".:

This repository is not for production. if you deploy it to heroku in this state you can lose data in `bot/local.db` database from time to time.
---
Articles with explanations
- [ru](https://github.com/LevZed/ton-footstep-8/blob/main/ton%20payments%20example%20(en).md) 
- [en](https://github.com/LevZed/ton-footstep-8/blob/main/ton%20payments%20example%20(en).md) 
