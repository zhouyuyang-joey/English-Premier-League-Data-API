'''
    Created by Zhou Yuyang
    Based on Erick Ghuron's premier-league-data API client("https://github.com/ghurone/premier-league-data").
'''

from typing import Any, Optional, Dict, List
import json
import time
import pandas as pd
import requests
from typing import Union
from .config import config
from .constants import StatTypes, APIEndpoints, DataKeys, OutputFormats, get_all_club_stat_types, validate_stat_type


class EPLAPI:
    def __init__(self, custom_config: Optional[str] = None):
        # Update config if provided
        if custom_config:
            for key, value in custom_config.items():
                config.set(key, value)

    
    def _make_request(self, endpoint, params: Dict[str, Any] = None) -> Dict[str, Any]:
        url = config.ROOT_URL + endpoint
        params = params or {}

        for attempt in range(config.max_retries + 1):
            try:
                response = requests.get(
                    url, 
                    headers=config.HEADERS, 
                    params=params,
                    timeout=config.request_timeout
                )
                
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    if attempt < config.max_retries:
                        print(f"Rate limit exceeded. Waiting {retry_after} seconds...")
                        time.sleep(retry_after)
                        continue
                    raise ValueError(f"Rate limit exceeded. Please wait {retry_after} seconds before retrying.")
                
                if response.status_code == 200:
                    try:
                        return json.loads(response.text)
                    except json.JSONDecodeError:
                        raise ValueError("Invalid JSON response from API")
                else:
                    raise ValueError(f"API request failed with status code {response.status_code}")
                    
            except requests.exceptions.Timeout:
                if attempt < config.max_retries:
                    print(f"Request timeout. Retrying in {config.retry_delay} seconds... (Attempt {attempt + 1}/{config.max_retries + 1})")
                    time.sleep(config.retry_delay)
                    continue
                raise ValueError("Request timeout. Please check your internet connection.")
            
            except requests.exceptions.ConnectionError:
                if attempt < config.max_retries:
                    print(f"Connection error. Retrying in {config.retry_delay} seconds... (Attempt {attempt + 1}/{config.max_retries + 1})")
                    time.sleep(config.retry_delay)
                    continue
                raise ValueError("Connection error. Please check your internet connection.")
            
            except requests.exceptions.RequestException as e:
                raise ValueError(f"Network error: {str(e)}")
            
    def _validate_output_format(self, output_format: str) -> None:
        """Validate output format parameter"""
        if not OutputFormats.is_valid(output_format):
            raise ValueError(f"Invalid output format '{output_format}'. Valid options are: 'json', 'df'")
        

    def _format_output(self, data: List[Dict], output_format: str) -> Union[List[Dict], pd.DataFrame]:
        """
        Format output data according to specified format
        
        Args:
            data: Data to format
            output_format: Output format ('json' or 'df')
            
        Returns:
            Formatted data
        """
        self._validate_output_format(output_format)
        
        if output_format == OutputFormats.DATAFRAME:
            return pd.DataFrame(data)
        return data


    def get_season_id(self, season_label: str = None) -> str:
        """
        Get season ID based on season label
        
        Args:
            season_label: Season label (e.g., "2024/25", "2023/24")
                         If None, returns the latest season ID
                         
        Returns:
            Season ID as string
            
        Raises:
            ValueError: When season is not found or API request fails
        """
        try:
            endpoint = APIEndpoints.SEASONS.format(config.premier_league_id)
            seasons_data = self._make_request(endpoint)
            
            if DataKeys.CONTENT not in seasons_data:
                raise ValueError("Invalid season data response from API")
            
            seasons = seasons_data[DataKeys.CONTENT]
            
            if season_label:
                for season in seasons:
                    if season.get("label") == season_label:
                        return str(int(season[DataKeys.ID]))
                raise ValueError(f"Season '{season_label}' not found. Please check the season format (e.g., '2024/25')")
            
            # Return latest season ID
            if not seasons:
                raise ValueError("No seasons available from API")
                
            latest_season = max(seasons, key=lambda x: x[DataKeys.ID])
            return str(int(latest_season[DataKeys.ID]))
            
        except (KeyError, ValueError, TypeError) as e:
            if "Season" in str(e) or "not found" in str(e) or "Invalid" in str(e):
                raise e
            raise ValueError(f"Error processing season data: {str(e)}")



    """
    ==================== Club Data ⬇️ ====================
    """

    def _get_clubs_in_season(self, season_id: str) -> List[Dict]:
        """Get raw club data for a season"""
        endpoint = APIEndpoints.CLUBS_IN_SEASON.format(season_id)
        return self._make_request(endpoint)


    def get_club_ids(self, season_id: str, output: str = None) -> Union[List[Dict], pd.DataFrame]:
        """
        Returns the name and ID of clubs in the specified season's Premier League.
        """
        if output is None:
            output = config.default_output_format
            
        try:
            clubs_data = self._get_clubs_in_season(season_id)
            
            team_data = []
            for team in clubs_data:
                if team.get(DataKeys.TEAM_TYPE) == DataKeys.FIRST_TEAM:
                    team_data.append({
                        "Name": team.get(DataKeys.SHORT_NAME),
                        "Team ID": str(int(team.get(DataKeys.ID)))
                    })
            
            if not team_data:
                raise ValueError(f"No clubs found for season {season_id}")
            
            return self._format_output(team_data, output)
            
        except (KeyError, ValueError, TypeError) as e:
            if "No clubs found" in str(e):
                raise e
            raise ValueError(f"Error processing club data: {str(e)}")
    

    def club_playedgames(self, compseason:str, teamId:str, altIds:str = 'true') -> dict:
        """
        Returns information of completed matches of a specified club.
        """
        res = self.__api_call(f'compseasons/{compseason}/standings/team/{teamId}?altIds={altIds}')

        return res
    

    def get_club_info(self, club_id: str) -> dict:
        """
        Returns deatiled information of a specified club.

        Args:
            club_id: Club ID
            
        Returns:
            Club information dictionary
        """
        try:
            endpoint = APIEndpoints.CLUB_INFO.format(club_id)
            return self._make_request(endpoint)
        except Exception as e:
            raise ValueError(f"Error getting club information for ID '{club_id}': {str(e)}")


    def club_rankings_list_stat_types(self) -> dict:
        """
        Returns a list of available stat_type values for use with get_club_rankings().
        These can be passed to .club_rankings(stat_type, compseason).
        """
        return {
            "General": [
                "wins", "losses", "draws", "goals", "total_red_card", "total_yel_card"
            ],
            "Attack": [
                "total_scoring_att", "ontarget_scoring_att", "hit_woodwork", "att_hd_goal", 
                "att_pen_goal", "att_freekick_goal", "att_ibox_goal", "att_obox_goal",
                "goal_fastbreak", "total_offside"
            ],
            "Defence": [
                "goals_conceded", "clean_sheet", "saves", "outfielder_block", 
                "interceptions", "total_tackle", "penalty_save",
                "last_man_tackle", "total_clearance", "Headed clearances", "clearance_off_line",
                "own_goals", "penalty_conceded", "pen_goals_conceded", "dispossessed", 
                "total_high_claim", "punches"
            ],
            "Teamplay": [
                "total_pass", "total_through_ball", "touches", "total_long_balls",
                "backward_pass", "total_cross", "corner_taken"
            ]
        }


    def get_club_rankings(self, stat_type: str, season_id: str, output: str = None) -> Union[List[Dict], pd.DataFrame]:
        """
        Get club rankings for a specific statistic
        
        Args:
            stat_type: Type of statistic (e.g., 'goals', 'total_pass')
            season_id: Season ID
            output: Output format ('json' or 'df')
            
        Returns:
            Club rankings data
            
        Raises:
            ValueError: When stat_type is invalid
        """
        if output is None:
            output = config.default_output_format
            
        # Validate stat type
        if not validate_stat_type(stat_type, "club"):
            valid_stats = get_all_club_stat_types()[:10]  # Show first 10 examples
            raise ValueError(f"Invalid statistic type '{stat_type}'. Valid examples include: {', '.join(valid_stats)}")
        
        try:
            params = {
                "pageSize": config.club_page_size,
                "compSeasons": season_id,
                "comps": config.premier_league_id,
                "altIds": "true"
            }
            
            endpoint = APIEndpoints.CLUB_RANKINGS.format(stat_type)
            response = self._make_request(endpoint, params)
            
            data = []
            stats_content = response.get(DataKeys.STATS, {}).get(DataKeys.CONTENT, [])
            
            for item in stats_content:
                team = item.get(DataKeys.OWNER, {})
                data.append({
                    "Rank": item.get(DataKeys.RANK),
                    "Club": team.get(DataKeys.NAME),
                    "Stat": item.get(DataKeys.VALUE)
                })
            
            if not data:
                raise ValueError(f"No ranking data found for statistic '{stat_type}' in season '{season_id}'")
            
            return self._format_output(data, output)
            
        except (KeyError, TypeError) as e:
            raise ValueError(f"Error processing club rankings for '{stat_type}': {str(e)}")
        

    def club_stats_list_stat_types(self) -> list:
        """
        Returns a list of stat_type that can be used in get_club_stats(club_id, season_id, stat_type=...).
        """
        return [
            "gameweek", "wins", "losses", "draws", "goals", "goals_conceded", "clean_sheet",
            "total_pass", "accurate_pass", "poss_won_att_3rd", "poss_won_mid_3rd", "poss_won_def_3rd",
            "total_cross", "accurate_cross", "total_through_ball", "accurate_through_ball",
            "total_scoring_att", "ontarget_scoring_att", "big_chance_created", "big_chance_missed",
            "goal_assist", "goal_assist_openplay", "goal_assist_setplay", "goal_assist_deadball",
            "goals_openplay", "goal_fastbreak", "subs_goals", "hit_woodwork", "saves",
            "penalty_won", "penalty_conceded", "penalty_save", "penalty_faced",
            "yellow_card", "total_yel_card", "red_card", "total_red_card",
            "att_freekick_total", "att_post_left", "att_post_right", "att_miss_high_left", "att_miss_high_right",
            "total_long_balls", "accurate_long_balls", "interception", "tackles", "blocked_scoring_att",
            "aerial_won", "aerial_lost", "duel_won", "duel_lost",
            "total_launches", "accurate_launches", "final_third_entries", "ball_recovery",
            "total_clearance", "head_clearance", "effective_clearance", "clearance_off_line",
            "error_lead_to_goal", "error_lead_to_shot",
            "attendance_average", "attendance_highest", "attendance_lowest"
        ]


    def get_club_stats(self, club_id: str, season_id: str, stat_type: str = None, output: str = None) -> Union[Dict, int, pd.DataFrame]:
        """
        Get statistics for a specific club in a season
        
        Args:
            club_id: Club ID
            season_id: Season ID
            stat_type: Specific statistic type (optional)
            output: Output format ('json' or 'df')
            
        Returns:
            Club statistics data
        """
        if output is None:
            output = config.default_output_format
            
        try:
            params = {
                "comps": config.premier_league_id,
                "compSeasons": season_id
            }
            
            endpoint = APIEndpoints.CLUB_STATS.format(club_id)
            response = self._make_request(endpoint, params)
            
            stats_list = response.get(DataKeys.STATS, [])
            stats_dict = {item[DataKeys.NAME]: item[DataKeys.VALUE] for item in stats_list}
            
            if stat_type:
                if stat_type not in stats_dict:
                    available_stats = list(stats_dict.keys())[:10]  # Show first 10 examples
                    raise ValueError(f"Statistic '{stat_type}' not found for this club. Available examples: {', '.join(available_stats)}")
                return stats_dict.get(stat_type)
            
            if output == OutputFormats.DATAFRAME:
                df = pd.DataFrame(list(stats_dict.items()), columns=["Stat", "Value"])
                return df.sort_values("Stat").reset_index(drop=True)
            
            return stats_dict
            
        except (KeyError, TypeError) as e:
            if "not found" in str(e):
                raise e
            raise ValueError(f"Error processing club statistics: {str(e)}")


    """
    ==================== Player Data ⬇️ ====================
    """



    def player_rankings_list_stat_types(self) -> dict:
        """
        Returns a list of parameters that can be used in the player_rankings().
        """
        return {
            "General": [
                "appearances", "wins", "losses", "draws", "minsPlayed"
            ],
            "Attack": [
                "goals", "goal_assist", "total_scoring_att", "ontarget_scoring_att",
                "hit_woodwork", "big_chance_created", "big_chance_missed",
                "att_pen_goal", "att_freekick_goal","att_hd_goal", "att_ibox_goal", 
                "att_obox_goal", "total_offside","oal_fastbreak", "corner_taken"
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


    def player_rankings(self, stat_type: str, compseason: str, output:str = 'json') -> Union[list, pd.DataFrame]:
        """
        Returns a ranking of players based on the given stat_type (e.g., "goals", "clean_sheet").
        """
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
    
        
    
    def player_list(self, compseason: str, output:str = 'json') -> Union[list, pd.DataFrame]:
        """
        Get all Premier League first team players (filter non-Premier League clubs/non-first team) for a given season.
        """
        team_id = self.club_id(compseason)
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
    

    def player_search_by_name(self, name: str, compseason: str, output:str = 'json') -> Union[list, pd.DataFrame]:
        """
        Search for players by name. All matching results will be returned.
        """
        all_players = self.player_list(compseason)
        filtered = [p for p in all_players if name.lower() in p["Name"].lower()]

        if output == "df":
            return pd.DataFrame(filtered)
        
        return filtered
    

    def player_id(self, name: str, compseason: str) -> str:
        """
        This function quickly returns the ID of first result of the search by default. 
        It is recommended to enter the full name of the player to avoid confusion.
        """
        matches = self.player_search_by_name(name, compseason)
        if not matches:
            raise ValueError(f"No match for {name}")
        return matches[0]["ID"]


    def player_stats(self, player_id: str, compseason: str) -> dict:
        """
        Gets the details of the specified player for the given season.
        """
        url = f"stats/player/{player_id}"
        params = {
            "comps": 1,
            "compSeasons": compseason
        }

        res = self.__api_call(url, qparams=params)
        return res