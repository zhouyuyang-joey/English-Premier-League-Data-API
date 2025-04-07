'''
    Created by Zhou Yuyang
    Based on Erick Ghuron's premier-league-data API client("https://github.com/ghurone/premier-league-data").
'''


import json
import pandas as pd
import requests
from typing import Union


def req_to_json(req: requests.Response) -> dict:
    if req.status_code == 200:
        return json.loads(req.text)
    else:
        raise ValueError(f'Error! status code:<{req.status_code}>')


class EPLAPI:
    def __init__(self) -> None:
        self.header = {
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://www.premierleague.com',
            'referer': 'https://www.premierleague.com',
        }
        self.root_url = 'https://footballapi.pulselive.com/football/'


    def __api_call(self, path:str, qparams:dict = {}):
        url = self.root_url + path
        res = requests.get(url, headers=self.header, params= qparams)

        return req_to_json(res)


    def get_season_id(self, season_label: str = None) -> str:
        """
        season_label should be something like "2024/25", "2023/24"
        """
        # Call API to get all season data
        seasons_data = self.__api_call("competitions/1/compseasons")

        # Make sure the API returns data
        if "content" not in seasons_data:
            raise ValueError

        # Find the ID of a given season
        if season_label:
            for season in seasons_data["content"]:
                if season["label"] == season_label:
                    return str(int(season["id"]))
            raise ValueError(f"Unable to find the season: {season_label}")

        # Get latest season ID (ID max)
        latest_season = max(seasons_data["content"], key=lambda x: x["id"])
        return str(int(latest_season["id"]))



    """
    Club Data ⬇️
    """


    def get_club_id(self, compseason: str, output:str = 'json') -> Union[list, pd.DataFrame]:
        """
        Returns the ID and name of the current season's Premier League club (shortName + id).
        """
        raw_data = self.club_incompseason(compseason)
        team_data = []

        for team in raw_data:
            if team.get("teamType") == "FIRST":
                team_data.append({
                    "Name": team.get("shortName"),
                    "Team ID": str(int(team.get("id")))
                })
        
        if output == "df":
            return pd.DataFrame(team_data)

        return team_data
    

    def club_incompseason(self, compseason:str) -> list[dict]:
        res = self.__api_call(f'compseasons/{compseason}/teams')

        return res


    def club_playedgames(self, compseason:str, teamId:str, altIds:str = 'true') -> dict:
        res = self.__api_call(f'compseasons/{compseason}/standings/team/{teamId}?altIds={altIds}')

        return res
    

    def club_information(self, teamId:str ) -> dict:
        res = self.__api_call(f'clubs/{teamId}')

        return res



    """
    Player Data ⬇️
    """



    def list_available_stat_types(self) -> dict:
        """
        Returns a list of parameters that can be used in the get_player_stats method.
        """
        return {
            "General": [
                "appearances", "wins", "losses", "draws", "minsPlayed"
            ],
            "Attack": [
                "goals", "goal_assist", "total_scoring_att", "ontarget_scoring_att",
                "hit_woodwork", "big_chance_created", "big_chance_missed",
                "penalty_goal", "freekick_goal", "goal_left_foot", "goal_right_foot",
                "goal_headed", "goals_insidebox", "goals_outsidebox"
            ],
            "Teamplay": [
                "total_pass", "pass_success", "total_cross", "cross_accuracy",
                "total_through_ball", "total_long_balls", "touches", "key_passes"
            ],
            "Defence": [
                "clean_sheet", "goals_conceded", "tackle_success", "last_man_tackle",
                "blocked_scoring_att", "interception", "clearance_off_line",
                "recoveries", "duel_won", "duel_lost", "aerial_won", "aerial_lost",
                "own_goals", "penalty_conceded"
            ],
            "Discipline": [
                "yellow_card", "red_card", "fouls", "offside"
            ],
            "Goalkeeping": [
                "saves", "penalty_save", "punches", "high_claim", "catch",
                "sweeper_clearance", "throw_out", "goal_kicks"
            ]
        }


    def get_player_stats(self, stat_type: str, compseason: str, output:str = 'json') -> Union[list, pd.DataFrame]:
        try:
            # Parameters
            params = {
                "pageSize": 50,
                "compSeasons": compseason,
                "comps": 1,
                "compCodeForActivePlayer": "EN_PR",
                "altIds": "true"
            }
            
            res = self.__api_call(
                f"stats/ranked/players/{stat_type}",
                qparams=params
            )
            
            # Parsing the data
            data = []
            for item in res.get("stats", {}).get("content", []):
                player = item.get("owner", {})
                data.append({
                    "Rank": item.get("rank"),
                    "Player": player.get("name", {}).get("display"),
                    "Club": player.get("currentTeam", {}).get("name"),
                    "Nationality": player.get("nationalTeam", {}).get("country"),
                    "Stat": item.get("value")
                })

            if not res:
                print(f"No response for stat_type {stat_type} in compseason {compseason}")
                return []
            
            if output == "df":
                return pd.DataFrame(data)
            
            return data
        
        except Exception as e:
            print(f"Failed in geting {stat_type}: {str(e)}")
            return []
    
        
    
    def list_all_players(self, compseason: str, output:str = 'json') -> Union[list, pd.DataFrame]:
        """
        Get all Premier League first team players (filter non-Premier League clubs/non-first team) for a given season.
        """
        team_id = self.get_club_id(compseason)
        valid_team_ids = set(team["Team ID"] for team in team_id)

        players = []
        page = 0
        while True:
            params = {
                "pageSize": 100,
                "page": page,
                "compSeasons": compseason
            }
            res = self.__api_call("players", qparams=params)
            content = res.get("content", [])
            if not content:
                break

            for p in content:
                team = p.get("currentTeam", {})
                team_id = str(int(team.get("id"))) if team and team.get("id") is not None else None

                if team_id in valid_team_ids:
                    players.append({
                        "ID": str(int(p["id"])),
                        "Name": p["name"]["display"],
                        "Position": p.get("info", {}).get("position"),
                        "Current Team": team.get("name"),
                        "Nationality": p.get("nationalTeam", {}).get("country")
                    })

            page += 1

        if output == "df":
            return pd.DataFrame(players)
        
        return players
    

    def search_player_by_name(self, name: str, compseason: str, output:str = 'json') -> Union[list, pd.DataFrame]:
        all_players = self.list_all_players(compseason)
        filtered = [p for p in all_players if name.lower() in p["Name"].lower()]

        if output == "df":
            return pd.DataFrame(filtered)
        
        return filtered
    

    def get_player_id(self, name: str, compseason: str) -> str:
        """
        This function quickly returns the first result of the search by default. 
        It is recommended to enter the full name of the player to avoid confusion.
        """
        matches = self.search_player_by_name(name, compseason)
        if not matches:
            raise ValueError(f"No match for {name}")
        return matches[0]["ID"]


    def get_player_info(self, player_id: str, compseason: str) -> dict:
        url = f"stats/player/{player_id}"
        params = {
            "comps": 1,
            "compSeasons": compseason
        }

        res = self.__api_call(url, qparams=params)
        return res
    

if __name__ == "__main__":
    epl = EPLAPI()
    season_id = epl.get_season_id("2024/25")
    
    print("\n List top goal scorers:")
    print(epl.get_player_stats("goals", season_id, output='df').head(10))

    print("\n Search player by name:")
    print(epl.search_player_by_name("Mohamed Salah", season_id, output='df'))

    player_id = epl.get_player_id("Mohamed Salah", season_id)
    print(f"\n Quickly retrieve the player id by full name: {player_id}")

    print("\n player's detailed stats:")

    stats_df = epl.get_player_info(player_id, season_id)
    entity = stats_df['entity']
    stats_list = stats_df['stats']
    stats_dict = {stat['name']: stat['value'] for stat in stats_list}
    player_summary = {
        "name": entity['name']['display'],
        "position": entity['info']['position'],
        "number": entity['info'].get('shirtNum'),
        "age": entity.get('age'),
        "appearances": stats_dict.get('appearances'),
        "goals": stats_dict.get('goals'),
        "goal_assist": stats_dict.get('goal_assist')
    }
    df_player = pd.DataFrame([player_summary])
    print(df_player)