# ⚽ English-Premier-League-Data-API



`EPL-Data` is an unofficial lightweight Python client library based on the Premier League Data API, which provides quick access to data on Premier League players and clubs. Great for data analysis and visualisation.

**Please note that this project was made solely for personal interest and learning purposes. Any commercial related use is unacceptable.**


> Created by Zhou Yuyang

> Inspired by Erick Ghuron's [premier-league-data](https://github.com/ghurone/premier-league-data)


## Features

- ✅ Player/Club data
- ✅ Support JSON / pandas DataFrame dual output format
- ✅ Suitable for the current 2024/25 season

## Setup Instructions:
```
pip install requests
pip install pandas
```
Alternatively, you can run ``pip install -r requirements.txt`` in the terminal. You can also complete the setup in the [examples.ipynb](examples.ipynb).
## Installation

```
pip install epl-data
```

## Brief Guide
Gets the corresponding ID of the specified season.
```python
from epldata import EPLAPI

epl = EPLAPI()
season_id = epl.get_season_id("2024/25")
```


Get the top scorer's list and quickly convert it to a pandas DataFrame.
```python
df_goals = epl.player_rankings("goals", season_id, output="df")
```

Search for a player ID by name to get information about the player.
```python
player_id = epl.player_id("Erling Haaland", season_id)
player_info = epl.player_info(player_id, season_id)
```

More specific demonstrations can be found at [examples.ipynb](examples.ipynb)