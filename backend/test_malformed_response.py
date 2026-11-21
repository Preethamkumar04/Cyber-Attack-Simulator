"""Test malformed Ollama response handling."""

from unittest.mock import patch, MagicMock
from app.services.ai_generator.ollama_client import OllamaClient


def test_markdown_json():
    """Test JSON wrapped in markdown code blocks."""
    client = OllamaClient()

    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'response': '```json\n{"attack_mode": "active", "attack_chain": ["test"], "hidden_objectives": ["test"], "expected_findings": ["test"], "expected_commands": ["test"], "expected_root_cause": "test", "expected_severity": "Medium", "expected_mitigation": ["test"]}\n```'
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        scenario = client.generate_scenario('BEGINNER')
        print(f'Test 1 (markdown JSON): {scenario.attack_mode}')
        assert scenario.attack_mode == "active"


def test_extra_text():
    """Test JSON with extra surrounding text."""
    client = OllamaClient()

    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'response': 'Here is the scenario: {"attack_mode": "active", "attack_chain": ["test"], "hidden_objectives": ["test"], "expected_findings": ["test"], "expected_commands": ["test"], "expected_root_cause": "test", "expected_severity": "Medium", "expected_mitigation": ["test"]} And some more text'
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        scenario = client.generate_scenario('BEGINNER')
        print(f'Test 2 (extra text): {scenario.attack_mode}')
        assert scenario.attack_mode == "active"


def test_invalid_json():
    """Test completely invalid JSON - should retry and fail."""
    client = OllamaClient()

    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {'response': 'not valid json at all'}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        try:
            scenario = client.generate_scenario('BEGINNER')
            print('Test 3 FAILED: Should have raised RuntimeError')
        except RuntimeError as e:
            print(f'Test 3 (invalid JSON): Correctly failed with RuntimeError')
            assert "Failed to generate valid scenario after 3 attempts" in str(e)


def test_missing_fields():
    """Test JSON missing required fields - validation should catch it."""
    client = OllamaClient()

    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'response': '{"attack_mode": "active", "attack_chain": ["test"]}'
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        try:
            scenario = client.generate_scenario('BEGINNER')
            print('Test 4 FAILED: Should have raised validation error')
        except (RuntimeError, ValueError) as e:
            print(f'Test 4 (missing fields): Correctly failed with validation error')


if __name__ == '__main__':
    test_markdown_json()
    test_extra_text()
    test_invalid_json()
    test_missing_fields()
    print('\nAll malformed response tests passed!')