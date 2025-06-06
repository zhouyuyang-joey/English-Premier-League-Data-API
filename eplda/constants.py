"""
Constants and static data for EPLDA (English Premier League Data API)
"""
from typing import Dict, List


class StatTypes:
    """Available statistic types for rankings and data retrieval"""
    
    # Club ranking stat types
    CLUB_STATS = {
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
    
    # Player ranking stat types
    PLAYER_STATS = {
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
    
    # Individual club stat types for detailed statistics
    CLUB_DETAIL_STATS = {
        "Basic Stats": ["gameweek", "wins", "losses", "draws", "goals", "goals_conceded", "clean_sheet"],
        "Passing": ["total_pass", "accurate_pass", "poss_won_att_3rd", "poss_won_mid_3rd", "poss_won_def_3rd"],
        "Attacking": ["total_scoring_att", "ontarget_scoring_att", "big_chance_created", "big_chance_missed", 
                     "goal_assist", "goals_openplay", "goal_fastbreak", "hit_woodwork"],
        "Defending": ["saves", "interception", "tackles", "blocked_scoring_att", "total_clearance", 
                     "head_clearance", "effective_clearance"],
        "Discipline": ["yellow_card", "total_yel_card", "red_card", "total_red_card"],
        "Attendance": ["attendance_average", "attendance_highest", "attendance_lowest"]
    }


class APIEndpoints:
    """API endpoint paths"""
    
    # Season endpoints
    SEASONS = "competitions/{}/compseasons"
    
    # Club endpoints
    CLUBS_IN_SEASON = "compseasons/{}/teams"
    CLUB_INFO = "clubs/{}"
    CLUB_RANKINGS = "stats/ranked/teams/{}"
    CLUB_STATS = "stats/team/{}"
    CLUB_SEASON_TABLE = "compseasons/{}/standings"
    
    # Player endpoints
    PLAYERS = "players"
    PLAYER_RANKINGS = "stats/ranked/players/{}"
    PLAYER_STATS = "stats/player/{}"


class DataKeys:
    """Standard keys used in API responses"""
    
    # Common response keys
    CONTENT = "content"
    STATS = "stats"
    ID = "id"
    NAME = "name"
    DISPLAY_NAME = "display"
    
    # Club specific keys
    TEAM_TYPE = "teamType"
    FIRST_TEAM = "FIRST"
    SHORT_NAME = "shortName"
    CURRENT_TEAM = "currentTeam"
    
    # Player specific keys
    NATIONAL_TEAM = "nationalTeam"
    COUNTRY = "country"
    INFO = "info"
    POSITION = "position"
    SHIRT_NUM = "shirtNum"
    AGE = "age"
    
    # Statistics keys
    OWNER = "owner"
    RANK = "rank"
    VALUE = "value"
    ENTITY = "entity"


class OutputFormats:
    """Available output formats"""
    
    JSON = "json"
    DATAFRAME = "df"
    
    @classmethod
    def is_valid(cls, format_type: str) -> bool:
        """Check if output format is valid"""
        return format_type in [cls.JSON, cls.DATAFRAME]


class Positions:
    """Player positions"""
    
    GOALKEEPER = "Goalkeeper"
    DEFENDER = "Defender"
    MIDFIELDER = "Midfielder"
    FORWARD = "Forward"
    
    ALL = [GOALKEEPER, DEFENDER, MIDFIELDER, FORWARD]


# Utility functions for constants
def get_all_club_stat_types() -> List[str]:
    """Get all available club statistic types as a flat list"""
    all_stats = []
    for category in StatTypes.CLUB_STATS.values():
        all_stats.extend(category)
    return all_stats


def get_all_player_stat_types() -> List[str]:
    """Get all available player statistic types as a flat list"""
    all_stats = []
    for category in StatTypes.PLAYER_STATS.values():
        all_stats.extend(category)
    return all_stats


def validate_stat_type(stat_type: str, stat_category: str = "club") -> bool:
    """
    Validate if a statistic type is available
    
    Args:
        stat_type: The statistic type to validate
        stat_category: Either 'club' or 'player'
        
    Returns:
        True if valid, False otherwise
    """
    if stat_category.lower() == "club":
        return stat_type in get_all_club_stat_types()
    elif stat_category.lower() == "player":
        return stat_type in get_all_player_stat_types()
    else:
        return False