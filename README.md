# ⚽ English-Premier-League-Data-API

[![PyPI version](https://img.shields.io/pypi/v/eplda.svg?style=flat&logo=pypi)](https://pypi.org/project/eplda/)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1O0QOm326n-zfGW0YbGXiH-2fuE0GZhfP?usp=sharing)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

### Name: Yuyang Zhou
### Student Number: 24005480

`EPL-Data` is an unofficial lightweight Python API client for [www.premierleague.com](https://www.premierleague.com/), providing quick access to data on Premier League players and clubs. It is ideal for data analysis and visualization.

**Note:** This project is for personal interest and learning only. Commercial use is strictly not permitted.


## Features
- ✅ Super user-friendly (hopefully)
- ✅ Player and club data access
- ✅ Supports both JSON and pandas DataFrame output formats
- ✅ Live Data

## What's New with the latest version
- Improved documentation and usage examples
- Self-explanatory naming
- More robust error handling and clearer API responses
- Expanded notebook example with step-by-step usage and visualization

## Gradio
I quickly built a Gradio app for Premier League data visualization with limited functionality with the help of LLM. You can run it in Colab easily!

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1O0QOm326n-zfGW0YbGXiH-2fuE0GZhfP?usp=sharing)


## Installation
The easiest way to install the latest version is:
```
pip install eplda
```

## Quick Start Guide
Get the season ID for a specific season:
```python
from eplda import EPLAPI

epl = EPLAPI()
season_id = epl.get_season_id("2024/25")
```

Get the top scorer's list and convert it to a pandas DataFrame:
```python
df_goals = epl.get_player_rankings("goals", season_id, output="df")
```

Search for a player ID by name and get player information:
```python
player_id = epl.get_player_id("Erling Haaland", season_id)
player_info = epl.get_player_details(player_id, season_id)
```

## Example Notebook
A comprehensive demonstration is available in [examples.ipynb](examples.ipynb), including:

- Brief explanation of all methods
- Club and player data queries
- Data visualization

## Known Issues
- For some reason, some players cannot be found by ``search_player_by_name()`` or ``get_player_list()``.
(The temporary solution is to read the player's ID in the URL of the official website, e.g. Bukayo Saka's ID is [49481](https://www.premierleague.com/players/49481/Bukayo-Saka/overview))
- ``interceptions`` and ``Headed clearances`` are not working for ``get_club_rankings()`` (Although it seems to be a typo, I still cannot get the stats correctly after trying to correct it)

## License & Terms of Use

### API Client

The `eplda` is open source with an [MIT License](LICENSE).

### T&C

``www.premierleague.com`` has a [Terms and Conditions](https://www.premierleague.com/terms-and-conditions) regarding the INTELLECTUAL PROPERTY RIGHTS. 

Please note that this project has been created for research purposes only and should not be misused in any way with this project or the data obtained from this it.

## Acknowledgement 
This project is based on Erick Ghuron's [premier-league-data](https://github.com/ghurone/premier-league-data).