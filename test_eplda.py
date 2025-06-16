import unittest
from unittest.mock import Mock, patch
import pandas as pd
import json
import sys
import os
import time

# Add the eplda package to the path for testing
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from eplda import EPLAPI
    from eplda.constants import StatTypes, OutputFormats
    from eplda.config import config
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure the eplda package is properly installed or in the Python path")
    sys.exit(1)


class TestEPLAPI(unittest.TestCase):
    """Test cases for EPLAPI class functionality"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.api = EPLAPI()
        
        # Mock season data
        self.mock_seasons_response = {
            "content": [
                {"id": 777, "label": "2025/26"},
                {"id": 719, "label": "2024/25"},
                {"id": 578, "label": "2023/24"}
            ]
        }
        
        # Mock club data
        self.mock_clubs_response = [
            {"id": 1, "shortName": "Arsenal", "teamType": "FIRST"},
            {"id": 4, "shortName": "Chelsea", "teamType": "FIRST"},
            {"id": 10, "shortName": "Liverpool", "teamType": "FIRST"}
        ]
        
        # Mock club table data
        self.mock_table_response = {
            "tables": [{
                "entries": [
                    {
                        "position": 1,
                        "team": {"id": 1, "name": "Arsenal"},
                        "overall": {
                            "played": 10, "won": 8, "drawn": 1, "lost": 1,
                            "goalsFor": 25, "goalsAgainst": 8, "goalsDifference": 17, "points": 25
                        }
                    },
                    {
                        "position": 2,
                        "team": {"id": 4, "name": "Chelsea"},
                        "overall": {
                            "played": 10, "won": 7, "drawn": 2, "lost": 1,
                            "goalsFor": 22, "goalsAgainst": 10, "goalsDifference": 12, "points": 23
                        }
                    }
                ]
            }]
        }
        
        # Mock player data
        self.mock_players_response = {
            "content": [
                {
                    "id": 65970,
                    "name": {"display": "Erling Haaland"},
                    "info": {"position": "Forward"},
                    "currentTeam": {"id": 11, "name": "Manchester City"},
                    "nationalTeam": {"country": "Norway"}
                },
                {
                    "id": 5178,
                    "name": {"display": "Mohamed Salah"},
                    "info": {"position": "Forward"},
                    "currentTeam": {"id": 10, "name": "Liverpool"},
                    "nationalTeam": {"country": "Egypt"}
                }
            ]
        }
        
        # Mock rankings data
        self.mock_rankings_response = {
            "stats": {
                "content": [
                    {
                        "rank": 1,
                        "owner": {
                            "name": {"display": "Erling Haaland"},
                            "currentTeam": {"name": "Manchester City"},
                            "nationalTeam": {"country": "Norway"}
                        },
                        "value": 15
                    },
                    {
                        "rank": 2,
                        "owner": {
                            "name": {"display": "Mohamed Salah"},
                            "currentTeam": {"name": "Liverpool"},
                            "nationalTeam": {"country": "Egypt"}
                        },
                        "value": 12
                    }
                ]
            }
        }
        
        # Mock player stats data
        self.mock_player_stats_response = {
            "stats": [
                {"name": "appearances", "value": 10},
                {"name": "goals", "value": 15},
                {"name": "goal_assist", "value": 3},
                {"name": "mins_played", "value": 850}
            ]
        }
        
        # Mock club rankings data
        self.mock_club_rankings_response = {
            "stats": {
                "content": [
                    {
                        "rank": 1,
                        "owner": {"name": "Arsenal"},
                        "value": 25
                    },
                    {
                        "rank": 2,
                        "owner": {"name": "Chelsea"},
                        "value": 22
                    }
                ]
            }
        }


class TestSeasonManagement(TestEPLAPI):
    """Test season-related functionality"""
    
    @patch('eplda.api.EPLAPI._make_request')
    def test_get_season_id_with_label(self, mock_request):
        """Test getting season ID with specific season label"""
        mock_request.return_value = self.mock_seasons_response
        
        season_id = self.api.get_season_id("2024/25")
        
        self.assertEqual(season_id, "719")
        mock_request.assert_called_once()
    
    @patch('eplda.api.EPLAPI._make_request')
    def test_get_season_id_latest(self, mock_request):
        """Test getting latest season ID when no label provided"""
        mock_request.return_value = self.mock_seasons_response
        
        season_id = self.api.get_season_id()
        
        self.assertEqual(season_id, "777")  # Latest season
    
    @patch('eplda.api.EPLAPI._make_request')
    def test_get_season_id_not_found(self, mock_request):
        """Test error handling when season not found"""
        mock_request.return_value = self.mock_seasons_response
        
        with self.assertRaises(ValueError) as context:
            self.api.get_season_id("2026/27")
        
        self.assertIn("Season '2026/27' not found", str(context.exception))
    
    @patch('eplda.api.EPLAPI._make_request')
    def test_get_season_id_empty_response(self, mock_request):
        """Test error handling when API returns empty seasons"""
        mock_request.return_value = {"content": []}
        
        with self.assertRaises(ValueError) as context:
            self.api.get_season_id()
        
        self.assertIn("No seasons available", str(context.exception))


class TestClubData(TestEPLAPI):
    """Test club-related functionality"""
    
    @patch('eplda.api.EPLAPI._make_request')
    def test_get_club_ids_json(self, mock_request):
        """Test getting club IDs in JSON format"""
        mock_request.return_value = self.mock_clubs_response
        
        result = self.api.get_club_ids("719", "json")
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["Name"], "Arsenal")
        self.assertEqual(result[0]["Club ID"], "1")
    
    @patch('eplda.api.EPLAPI._make_request')
    def test_get_club_ids_dataframe(self, mock_request):
        """Test getting club IDs in DataFrame format"""
        mock_request.return_value = self.mock_clubs_response
        
        result = self.api.get_club_ids("719", "df")
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 3)
        self.assertEqual(result.iloc[0]["Name"], "Arsenal")
    
    @patch('eplda.api.EPLAPI._make_request')
    def test_get_club_tables(self, mock_request):
        """Test getting club league table"""
        mock_request.return_value = self.mock_table_response
        
        result = self.api.get_club_tables("719", "json")
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["Position"], 1)
        self.assertEqual(result[0]["Club"], "Arsenal")
        self.assertEqual(result[0]["Points"], 25)
    
    @patch('eplda.api.EPLAPI._make_request')
    def test_get_club_rankings(self, mock_request):
        """Test getting club rankings for specific statistic"""
        mock_request.return_value = self.mock_club_rankings_response
        
        result = self.api.get_club_rankings("goals", "719", "json")
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["Rank"], 1)
        self.assertEqual(result[0]["Club"], "Arsenal")
        self.assertEqual(result[0]["Stat"], 25)
    
    def test_get_club_rankings_invalid_stat(self):
        """Test error handling for invalid club statistic type"""
        with self.assertRaises(ValueError) as context:
            self.api.get_club_rankings("invalid_stat", "719")
        
        self.assertIn("Invalid statistic type", str(context.exception))


class TestPlayerData(TestEPLAPI):
    """Test player-related functionality"""
    
    @patch('eplda.api.EPLAPI._make_request')
    def test_get_player_rankings_json(self, mock_request):
        """Test getting player rankings in JSON format"""
        mock_request.return_value = self.mock_rankings_response
        
        result = self.api.get_player_rankings("goals", "719", "json")
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["Rank"], 1)
        self.assertEqual(result[0]["Player"], "Erling Haaland")
        self.assertEqual(result[0]["Club"], "Manchester City")
        self.assertEqual(result[0]["Stat"], 15)
    
    @patch('eplda.api.EPLAPI._make_request')
    def test_get_player_rankings_dataframe(self, mock_request):
        """Test getting player rankings in DataFrame format"""
        mock_request.return_value = self.mock_rankings_response
        
        result = self.api.get_player_rankings(stat_type="goals", season_id="719", output="df")
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertEqual(result.iloc[0]["Player"], "Erling Haaland")
    
    def test_get_player_rankings_invalid_stat(self):
        """Test error handling for invalid player statistic type"""
        with self.assertRaises(ValueError) as context:
            self.api.get_player_rankings("invalid_stat", "719")
        
        self.assertIn("Invalid statistic type", str(context.exception))
    
    @patch('eplda.api.EPLAPI.get_club_ids')
    @patch('eplda.api.EPLAPI._make_request')
    def test_get_player_list(self, mock_request, mock_club_ids):
        """Test getting list of players"""
        mock_club_ids.return_value = [{"Club ID": "1"}, {"Club ID": "10"}]

        mock_request.side_effect = [self.mock_players_response,{"content": []}]
        
        result = self.api.get_player_list("719", "json")
        
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) >= 1)
        self.assertIn("ID", result[0])
        self.assertIn("Name", result[0])
        self.assertIn("Position", result[0])
    
    @patch('eplda.api.EPLAPI.get_player_list')
    def test_search_player_by_name(self, mock_get_players):
        """Test searching for players by name"""
        mock_get_players.return_value = [
            {"ID": "65970", "Name": "Erling Haaland", "Position": "Forward"},
            {"ID": "5178", "Name": "Mohamed Salah", "Position": "Forward"}
        ]
        
        result = self.api.search_player_by_name("Haaland", "719", "json")
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["Name"], "Erling Haaland")
    
    @patch('eplda.api.EPLAPI.search_player_by_name')
    def test_get_player_id(self, mock_search):
        """Test getting player ID by name"""
        mock_search.return_value = [{"ID": "65970", "Name": "Erling Haaland"}]
        
        player_id = self.api.get_player_id("Erling Haaland", "719")
        
        self.assertEqual(player_id, "65970")
    
    @patch('eplda.api.EPLAPI._make_request')
    def test_get_player_stats(self, mock_request):
        """Test getting detailed player statistics"""
        mock_request.return_value = self.mock_player_stats_response
        
        result = self.api.get_player_stats("100", "719")
        
        self.assertIsInstance(result, dict)
        self.assertIn("stats", result)
    
    @patch('eplda.api.EPLAPI.get_player_list')
    @patch('eplda.api.EPLAPI.get_player_stats')
    def test_get_player_comparison(self, mock_stats, mock_players):
        """Test comparing multiple players"""
        # Mock player list
        mock_players.return_value = [
            {"ID": "65970", "Name": "Erling Haaland", "Position": "Forward", "Current Team": "Manchester City"},
            {"ID": "5178", "Name": "Mohamed Salah", "Position": "Forward", "Current Team": "Liverpool"}
        ]
        
        # Mock player stats
        mock_stats.side_effect = [
            {"stats": [{"name": "goals", "value": 15}, {"name": "appearances", "value": 10}]},
            {"stats": [{"name": "goals", "value": 12}, {"name": "appearances", "value": 11}]}
        ]
        
        result = self.api.get_player_comparison(
            ["Erling Haaland", "Mohamed Salah"], 
            "719", 
            ["goals", "appearances"], 
            "json"
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn("players", result)
        self.assertIn("stats_compared", result)
        self.assertEqual(len(result["players"]), 2)


class TestErrorHandling(TestEPLAPI):
    """Test error handling and validation"""
    
    def test_invalid_output_format(self):
        """Test error handling for invalid output format"""
        with self.assertRaises(ValueError):
            self.api._validate_output_format("invalid")
    
    def test_valid_output_formats(self):
        """Test validation of valid output formats"""
        try:
            self.api._validate_output_format("json")
            self.api._validate_output_format("df")
        except ValueError:
            self.fail("Valid output formats should not raise ValueError")
    
    @patch('eplda.api.EPLAPI._make_request')
    def test_api_request_error_handling(self, mock_request):
        """Test handling of API request errors"""
        mock_request.side_effect = ValueError("API request failed")
        
        with self.assertRaises(ValueError):
            self.api.get_season_id("2024/25")
    
    @patch('eplda.api.EPLAPI.search_player_by_name')
    def test_player_not_found_error(self, mock_search):
        """Test error when player is not found"""
        mock_search.side_effect = ValueError("No players found matching 'NonExistent'")
        
        with self.assertRaises(ValueError) as context:
            self.api.get_player_id("NonExistent Player", "719")
        
        self.assertIn("No players found matching", str(context.exception))


class TestOutputFormatting(TestEPLAPI):
    """Test output format conversion functionality"""
    
    def test_format_output_json(self):
        """Test formatting data as JSON"""
        test_data = [{"name": "test", "value": 1}]
        result = self.api._format_output(test_data, "json")
        
        self.assertEqual(result, test_data)
        self.assertIsInstance(result, list)
    
    def test_format_output_dataframe(self):
        """Test formatting data as DataFrame"""
        test_data = [{"name": "test1", "value": 1}, {"name": "test2", "value": 2}]
        result = self.api._format_output(test_data, "df")
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertEqual(result.iloc[0]["name"], "test1")


class TestUtilityMethods(TestEPLAPI):
    """Test utility and helper methods"""
    
    def test_get_club_ranking_stats_pretty(self):
        """Test getting club ranking statistics in pretty format"""
        # This should print to console and return None
        result = self.api.get_club_ranking_stats("pretty")
        self.assertIsNone(result)
    
    def test_get_club_ranking_stats_list(self):
        """Test getting club ranking statistics as list"""
        result = self.api.get_club_ranking_stats("list")
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)
        self.assertIn("goals", result)
    
    def test_get_club_ranking_stats_dict(self):
        """Test getting club ranking statistics as dictionary"""
        result = self.api.get_club_ranking_stats("dict")
        self.assertIsInstance(result, dict)
        self.assertIn("General", result)
        self.assertIn("goals", result["General"])
    
    def test_get_player_ranking_stats_list(self):
        """Test getting player ranking statistics as list"""
        result = self.api.get_player_ranking_stats("list")
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)
        self.assertIn("goals", result)


class TestAPIInitialization(TestEPLAPI):
    """Test API initialization and configuration"""
    
    def test_api_initialization_default(self):
        """Test API initialization with default configuration"""
        api = EPLAPI()
        self.assertIsInstance(api, EPLAPI)
    
    def test_api_initialization_custom_config(self):
        """Test API initialization with custom configuration"""
        custom_config = {"request.timeout": 60}
        api = EPLAPI(custom_config)
        self.assertIsInstance(api, EPLAPI)


class TestMockRequestMethod(TestEPLAPI):
    """Test the _make_request method with various scenarios"""
    
    @patch('time.sleep')  # Mock sleep to avoid waiting in retry logic
    @patch('requests.get')
    def test_make_request_success(self, mock_get, mock_sleep):
        """Test successful API request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"test": "data"}'
        mock_get.return_value = mock_response
        
        result = self.api._make_request("/test")
        
        self.assertEqual(result, {"test": "data"})
        mock_sleep.assert_not_called()
    
    @patch('time.sleep')  # Mock sleep to avoid waiting
    @patch('requests.get')
    def test_make_request_rate_limit(self, mock_get, mock_sleep):
        """Test handling of rate limit response"""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {'Retry-After': '60'}
        mock_get.return_value = mock_response
        
        with self.assertRaises(ValueError) as context:
            self.api._make_request("/test")
        
        self.assertIn("Rate limit exceeded", str(context.exception))
        # Verify that sleep was called with correct duration
        mock_sleep.assert_called_with(60)
    
    @patch('time.sleep')  # Mock sleep to avoid waiting in retry logic
    @patch('requests.get')
    def test_make_request_invalid_json(self, mock_get, mock_sleep):
        """Test handling of invalid JSON response"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = 'invalid json'
        mock_get.return_value = mock_response
        
        with self.assertRaises(ValueError) as context:
            self.api._make_request("/test")
        
        self.assertIn("Invalid JSON response", str(context.exception))


def run_tests():
    # Create test suite
    test_classes = [
        TestSeasonManagement,
        TestClubData,
        TestPlayerData,
        TestErrorHandling,
        TestOutputFormatting,
        TestUtilityMethods,
        TestAPIInitialization,
        TestMockRequestMethod
    ]
    
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"{'='*50}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)