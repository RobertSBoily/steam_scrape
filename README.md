# steam_scraper
This is a Python script to:
- Open the "Followed Games" page of a Steam profile, with the username as user input
- Webscrape, from Steam, various information on each game.
- Export that information to a spreadsheet (steam.xlsx).

Usage:
```
import steam
scraper = Steam.SteamScraper("YOUR_STEAM_USERNAME_HERE")
scraper.main()
```


Style and structure problems existing in this code (TO FIX):
- SteamScraper is a god object (this relic of this code originally being procedural).
- Related to the above: use Page Object Design.
- Global constants should be moved into class variables (some should be left as user input).
- Determine a policy on using webdriver in classes - maybe allow it in any function, including __init__(), but when a function is run, instantiate a new driver, and then close it at the end?
