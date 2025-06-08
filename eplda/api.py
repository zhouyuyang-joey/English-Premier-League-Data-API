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
    
    
    def get_club_tables(self, season_id: str = None, output: str = None) -> Union[List[Dict], pd.DataFrame]:
        if output is None:
            output = config.default_output_format
        
        # Get current season if not provided
        if season_id is None:
            season_id = self.get_season_id()
            
        try:
            endpoint = APIEndpoints.CLUB_SEASON_TABLE.format(season_id)
            response = self._make_request(endpoint)
            
            # Extract table data from response
            tables = response.get("tables", [])
            if not tables:
                raise ValueError(f"No table data found for season {season_id}")
            
            # Get the main league table (usually the first one)
            main_table = tables[0]
            entries = main_table.get("entries", [])
            
            if not entries:
                raise ValueError(f"No standings entries found for season {season_id}")
            
            table_data = []
            for entry in entries:
                team = entry.get("team", {})
                overall = entry.get("overall", {})
                
                table_data.append({
                    "Position": entry.get("position"),
                    "Club": team.get("name"),
                    "Club ID": str(team.get("id", "")),
                    "Played": overall.get("played", 0),
                    "Won": overall.get("won", 0),
                    "Drawn": overall.get("drawn", 0),
                    "Lost": overall.get("lost", 0),
                    "Goals For": overall.get("goalsFor", 0),
                    "Goals Against": overall.get("goalsAgainst", 0),
                    "Goal Difference": overall.get("goalsDifference", 0),
                    "Points": overall.get("points", 0)
                })
            
            # Sort by position to ensure correct order
            table_data.sort(key=lambda x: x["Position"])
            
            return self._format_output(table_data, output)
            
        except (KeyError, TypeError) as e:
            raise ValueError(f"Error processing club table data: {str(e)}")
    

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


    def get_player_rankings(self, stat_type: str, season_id: str, output: str = None) -> Union[List[Dict], pd.DataFrame]:
        """
        Get player rankings for a specific statistic
        
        Args:
            stat_type: Type of statistic (e.g., 'goals', 'clean_sheet')
            season_id: Season ID
            output: Output format ('json' or 'df')
            
        Returns:
            Player rankings data
            
        Raises:
            ValueError: When stat_type is invalid
        """
        if output is None:
            output = config.default_output_format
            
        # Validate stat type
        if not validate_stat_type(stat_type, "player"):
            from .constants import get_all_player_stat_types
            valid_stats = get_all_player_stat_types()[:10]  # Show first 10 examples
            raise ValueError(f"Invalid statistic type '{stat_type}'. Valid examples include: {', '.join(valid_stats)}")
        
        try:
            params = {
                "pageSize": config.player_page_size,
                "compSeasons": season_id,
                "comps": config.premier_league_id,
                "compCodeForActivePlayer": config.comp_code,
                "altIds": "true"
            }
            
            endpoint = APIEndpoints.PLAYER_RANKINGS.format(stat_type)
            response = self._make_request(endpoint, params)
            
            data = []
            stats_content = response.get(DataKeys.STATS, {}).get(DataKeys.CONTENT, [])
            
            for item in stats_content:
                player = item.get(DataKeys.OWNER, {})
                player_data = {
                    "Rank": item.get(DataKeys.RANK),
                    "Player": player.get(DataKeys.NAME, {}).get(DataKeys.DISPLAY_NAME),
                    "Club": player.get(DataKeys.CURRENT_TEAM, {}).get(DataKeys.NAME),
                    "Stat": item.get(DataKeys.VALUE)
                }
                
                # Add nationality if configured
                if config.include_nationality:
                    player_data["Nationality"] = player.get(DataKeys.NATIONAL_TEAM, {}).get(DataKeys.COUNTRY)
                
                data.append(player_data)
            
            if not data:
                raise ValueError(f"No ranking data found for statistic '{stat_type}' in season '{season_id}'")
            
            return self._format_output(data, output)
            
        except (KeyError, TypeError) as e:
            if "No ranking data found" in str(e):
                raise e
            raise ValueError(f"Error processing player rankings for '{stat_type}': {str(e)}")
    
        
    def get_player_list(self, season_id: str, output: str = None, club_id: Union[str, int] = None) -> Union[List[Dict], pd.DataFrame]:
        """
        Get Premier League players for a season, optionally filtered by club
        
        Args:
            season_id: Season ID
            output: Output format ('json' or 'df')
            club_id: Club ID to filter players (can be string or int, optional)
            
        Returns:
            List of players with basic information
            
        Raises:
            ValueError: When no players found or invalid club_id
        """
        if output is None:
            output = config.default_output_format
            
        try:
            # If club_id is provided, validate it first
            if club_id is not None:
                # Convert club_id to string for consistent handling
                club_id = str(club_id)
                
                club_ids_data = self.get_club_ids(season_id, "json")
                valid_club_ids = {club["Team ID"] for club in club_ids_data}
                
                if club_id not in valid_club_ids:
                    raise ValueError(f"Club ID '{club_id}' not found. Use get_club_ids() or get_club_tables() to find valid club IDs.")
            
            # Get valid team IDs for filtering (only if not filtering by specific club)
            if club_id is None:
                club_ids_data = self.get_club_ids(season_id, "json")
                valid_team_ids = {club["Team ID"] for club in club_ids_data}
            else:
                valid_team_ids = {club_id}
            
            players = []
            page = 0
            
            while True:
                params = {
                    "pageSize": config.default_page_size,
                    "page": page,
                    "compSeasons": season_id
                }
                
                response = self._make_request(APIEndpoints.PLAYERS, params)
                content = response.get(DataKeys.CONTENT, [])
                
                if not content:
                    break
                
                for player in content:
                    team = player.get(DataKeys.CURRENT_TEAM, {})
                    team_id = str(int(team.get(DataKeys.ID))) if team and team.get(DataKeys.ID) is not None else None
                    
                    # Apply filtering logic
                    if club_id is not None:
                        # Filter by specific club
                        if team_id != club_id:
                            continue
                    else:
                        # Filter only first team players if configured (original logic)
                        if config.filter_first_team_only and team_id not in valid_team_ids:
                            continue
                    
                    player_data = {
                        "ID": str(int(player[DataKeys.ID])),
                        "Name": player[DataKeys.NAME][DataKeys.DISPLAY_NAME],
                        "Position": player.get(DataKeys.INFO, {}).get(DataKeys.POSITION),
                        "Current Team": team.get(DataKeys.NAME)
                    }
                    
                    # Add nationality if configured
                    if config.include_nationality:
                        player_data["Nationality"] = player.get(DataKeys.NATIONAL_TEAM, {}).get(DataKeys.COUNTRY)
                    
                    players.append(player_data)
                
                page += 1
            
            if not players:
                if club_id is not None:
                    # Get club name for better error message
                    club_name = "Unknown"
                    try:
                        club_info = self.get_club_info(club_id)
                        club_name = club_info.get("name", club_id)
                    except:
                        pass
                    raise ValueError(f"No players found for club '{club_name}' (ID: {club_id}) in season {season_id}")
                else:
                    raise ValueError(f"No players found for season {season_id}")
            
            return self._format_output(players, output)
            
        except (KeyError, ValueError, TypeError) as e:
            if "not found" in str(e) or "No players found" in str(e):
                raise e
            raise ValueError(f"Error processing player list: {str(e)}")

    

    def search_player_by_name(self, name: str, season_id: str, output: str = None) -> Union[List[Dict], pd.DataFrame]:
        """
        Search for players by name
        
        Args:
            name: Player name to search for
            season_id: Season ID
            output: Output format ('json' or 'df')
            
        Returns:
            List of matching players
        """
        if output is None:
            output = config.default_output_format
            
        try:
            all_players = self.get_player_list(season_id, "json")
            filtered_players = [
                player for player in all_players 
                if name.lower() in player["Name"].lower()
            ]
            
            if not filtered_players:
                raise ValueError(f"No players found matching '{name}' in season {season_id}. Please check the spelling or try a different name format.")
            
            return self._format_output(filtered_players, output)
            
        except Exception as e:
            if "No players found matching" in str(e):
                raise e
            raise ValueError(f"Error searching for player '{name}': {str(e)}")
    

    def get_player_id(self, name: str, season_id: str) -> str:
        """
        Get player ID by name (returns first match)
        
        Args:
            name: Player name
            season_id: Season ID
            
        Returns:
            Player ID
            
        Raises:
            ValueError: When player is not found
        """
        matches = self.search_player_by_name(name, season_id, "json")
        # Will raise ValueError from search_player_by_name if no matches
        return matches[0]["ID"]


    def get_player_stats(self, player_id: str, season_id: str) -> Dict[str, Any]:
        """
        Get detailed statistics for a specific player
        
        Args:
            player_id: Player ID
            season_id: Season ID
            
        Returns:
            Player statistics data
        """
        try:
            params = {
                "comps": config.premier_league_id,
                "compSeasons": season_id
            }
            
            endpoint = APIEndpoints.PLAYER_STATS.format(player_id)
            return self._make_request(endpoint, params)
            
        except Exception as e:
            raise ValueError(f"Error getting statistics for player ID '{player_id}': {str(e)}")
        

    def get_player_comparison(self, player_names: List[str], season_id: str, stats_to_compare: List[str] = None, output: str = None) -> Union[Dict[str, Any], pd.DataFrame]:
        """
        Compare multiple players' statistics
        
        Args:
            player_names: List of player names to compare
            season_id: Season ID
            stats_to_compare: List of statistics to compare (optional)
            output: Output format ('json' or 'df')
            
        Returns:
            Comparison data in specified format
            
        Raises:
            ValueError: When players not found or invalid parameters
        """
        if output is None:
            output = config.default_output_format
        
        # Default comparison statistics
        if stats_to_compare is None:
            stats_to_compare = ["appearances", "mins_played", "goals", "goal_assist"]
        
        # Validate inputs
        if len(player_names) < 2:
            raise ValueError("At least 2 players are required for comparison")
        
        if len(set(player_names)) != len(player_names):
            raise ValueError("Duplicate player names found in the list")
        
        # Get all players list to extract team and position info
        try:
            all_players_list = self.get_player_list(season_id, "json")
            players_info_map = {}
            
            # Create a mapping of player names to their info
            for player in all_players_list:
                player_name_variations = [
                    player["Name"],
                    player["Name"].lower(),
                    player["Name"].replace(" ", "").lower()
                ]
                for variation in player_name_variations:
                    players_info_map[variation] = {
                        "id": player["ID"],
                        "name": player["Name"],
                        "position": player.get("Position"),
                        "team": player.get("Current Team")
                    }
            
        except Exception as e:
            raise ValueError(f"Failed to get players list: {str(e)}")
        
        # Get player data
        players_data = {}
        failed_players = []
        stats_info = {}
        
        for player_name in player_names:
            try:
                # Try to find player info from the players list
                player_info = None
                search_variations = [
                    player_name,
                    player_name.lower(),
                    player_name.replace(" ", "").lower()
                ]
                
                for variation in search_variations:
                    if variation in players_info_map:
                        player_info = players_info_map[variation]
                        break
                
                if not player_info:
                    # Fallback: search by name similarity
                    for list_player in all_players_list:
                        if player_name.lower() in list_player["Name"].lower():
                            player_info = {
                                "id": list_player["ID"],
                                "name": list_player["Name"],
                                "position": list_player.get("Position"),
                                "team": list_player.get("Current Team")
                            }
                            break
                
                if not player_info:
                    raise ValueError(f"Player '{player_name}' not found in season {season_id}")
                
                player_id = player_info["id"]
                
                # Get player stats
                player_stats_response = self.get_player_stats(player_id, season_id)
                
                # Extract stats
                stats_list = player_stats_response.get('stats', [])
                
                # Convert stats list to dictionary
                stats_dict = {stat['name']: stat['value'] for stat in stats_list}
                
                # Extract requested statistics
                player_comparison_data = {}
                for stat in stats_to_compare:
                    value = stats_dict.get(stat, 0)  # Use 0 for missing stats
                    player_comparison_data[stat] = value
                
                # Use player info from the players list (more reliable)
                final_player_info = {
                    "name": player_info["name"],
                    "position": player_info["position"],
                    "team": player_info["team"],
                    "stats": player_comparison_data
                }
                
                players_data[player_name] = final_player_info
                
            except Exception as e:
                failed_players.append({"name": player_name, "error": str(e)})
        
        # Check if we have enough successful players
        if len(players_data) < 2:
            error_msg = f"Failed to get data for enough players. Successful: {len(players_data)}, Failed: {len(failed_players)}"
            if failed_players:
                error_msg += f"\nFailed players: {[fp['name'] + ' (' + fp['error'] + ')' for fp in failed_players]}"
            raise ValueError(error_msg)
        
        # Warn about failed players but continue with successful ones
        if failed_players:
            print(f"Warning: Failed to get data for {len(failed_players)} player(s): {[fp['name'] for fp in failed_players]}")
        
        # Calculate stats info (min, max, mean for each statistic)
        all_stats_values = {stat: [] for stat in stats_to_compare}
        
        # Collect all values for each statistic
        for player_data in players_data.values():
            for stat in stats_to_compare:
                value = player_data["stats"].get(stat, 0)
                all_stats_values[stat].append(value)
        
        for stat in stats_to_compare:
            values = all_stats_values[stat]
            stats_info[stat] = {
                "min": min(values),
                "max": max(values),
                "mean": sum(values) / len(values) if values else 0
            }
        
        # Prepare return data
        result_data = {
            "players": players_data,
            "stats_compared": stats_to_compare,
            "stats_info": stats_info,
            "season_id": season_id
        }
        
        # Add failed players info if any
        if failed_players:
            result_data["failed_players"] = failed_players
        
        # Format output
        if output == OutputFormats.DATAFRAME:
            # Create DataFrame with players as rows and stats as columns
            df_data = []
            for player_name, player_data in players_data.items():
                row = {"Player": player_data["name"], "Position": player_data.get("position"), "Team": player_data.get("team")}
                row.update(player_data["stats"])
                df_data.append(row)
            
            df = pd.DataFrame(df_data)
            # Set player names as index for easier plotting
            df.set_index("Player", inplace=True)
            return df
        
        return result_data

        
    
    """
    ==================== Utility ⬇️ ====================
    """


    def get_club_ranking_stats(self, output: str = "pretty") -> Union[Dict, List, None]:
        """
        Get available statistic types for club rankings (used in get_club_rankings)
        
        Args:
            output: Output format - "dict", "list", or "pretty" (prints to console)
            
        Returns:
            Available statistics for club rankings
        """
        stats = StatTypes.CLUB_STATS
        
        if output == "pretty":
            print("Available Statistics for Club Rankings (get_club_rankings)")
            print("=" * 60)
            for category, stat_list in stats.items():
                print(f"\n{category}:")
                for i, stat in enumerate(stat_list, 1):
                    print(f"   {i:2d}. {stat}")
            print(f"\nUsage: epl.get_club_rankings('stat_name', season_id)")
            return None
        elif output == "list":
            # Return flat list of all stats
            all_stats = []
            for stat_list in stats.values():
                all_stats.extend(stat_list)
            return sorted(all_stats)
        # dict format
        else:
            return stats


    def get_club_detail_stats(self, output: str = "pretty") -> Union[List, None]:
        """
        Get available statistic types for club detailed statistics (used in get_club_stats)
        
        Args:
            output: Output format - "list" or "pretty" (prints to console)
            
        Returns:
            Available statistics for club detailed stats
        """
        stats = StatTypes.CLUB_DETAIL_STATS
        
        if output == "pretty":
            print("Available Statistics for Club Detailed Stats (get_club_stats)")
            print("=" * 65)
            
            # Use categories from constants
            categories = StatTypes.CLUB_DETAIL_STATS
            
            for category, category_stats in categories.items():
                available_in_category = [stat for stat in category_stats if stat in stats]
                if available_in_category:
                    print(f"\n{category}:")
                    for i, stat in enumerate(available_in_category, 1):
                        print(f"   {i:2d}. {stat}")
            
            # Show remaining stats not categorized
            categorized_stats = set()
            for category_stats in categories.values():
                categorized_stats.update(category_stats)
            
            remaining_stats = [stat for stat in stats if stat not in categorized_stats]
            if remaining_stats:
                print(f"\nOther:")
                for i, stat in enumerate(remaining_stats, 1):
                    print(f"   {i:2d}. {stat}")
            
            print(f"\nUsage: epl.get_club_stats(club_id, season_id, stat_type='stat_name')")
            return None
        else:  # list format
            return sorted(stats)


    def get_player_ranking_stats(self, output: str = "pretty") -> Union[Dict, List, None]:
        """
        Get available statistic types for player rankings (used in get_player_rankings)
        
        Args:
            output: Output format - "dict", "list", or "pretty" (prints to console)
            
        Returns:
            Available statistics for player rankings
        """
        stats = StatTypes.PLAYER_STATS
        
        if output == "pretty":
            print("Available Statistics for Player Rankings (get_player_rankings)")
            print("=" * 65)
            for category, stat_list in stats.items():
                print(f"\n{category}:")
                for i, stat in enumerate(stat_list, 1):
                    print(f"   {i:2d}. {stat}")
            print(f"\nUsage: epl.get_player_rankings('stat_name', season_id)")
            return None
        elif output == "list":
            # Return flat list of all stats
            all_stats = []
            for stat_list in stats.values():
                all_stats.extend(stat_list)
            return sorted(all_stats)
        # dict format
        else:
            return stats