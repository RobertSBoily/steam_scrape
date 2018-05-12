# steam_scrape
Style and structure problems existing in this code (TO FIX):
- SteamScraper is a god object (this relic of this code originally being procedural).
- Related to the above: use Page Object Design.
- Global constants should be moved into class variables (some should be left as user input).
- Determine a policy on using webdriver in classes - maybe allow it in any function, including __init__(), but when a function is run, instantiate a new driver, and then close it at the end?
