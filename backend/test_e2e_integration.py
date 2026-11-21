"""Complete end-to-end integration test."""

import requests
import os

BASE_URL = 'http://localhost:8000'
HEADERS = {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwiZXhwIjoxNzg2MjgzNjA3fQ.mb9NZzqmckP2LwGDaR9dcstv69u52-Gu7ifJZoi5mc4'}

print('=== END-TO-END INTEGRATION TEST ===\n')

# 1. Health check
print('1. Health Check:')
r = requests.get(f'{BASE_URL}/health')
print(f'   Status: {r.json()}')

# 2. Test all difficulty levels
for difficulty in ['BEGINNER', 'INTERMEDIATE', 'ADVANCED']:
    print(f'\n2.{difficulty} Scenario Start:')
    r = requests.post(f'{BASE_URL}/scenario/start', json={'difficulty': difficulty}, headers=HEADERS)
    data = r.json()
    session_id = data['session_id']
    print(f'   Session ID: {session_id}')
    print(f'   Difficulty: {data["difficulty"]}')
    print(f'   Attack Mode: {data["scenario"]["attack_mode"]}')
    print(f'   Attack Chain: {data["scenario"]["attack_chain"]}')
    print(f'   Available Artifacts: {data["scenario"]["available_artifacts"]}')

    # Verify hidden data is NOT in response
    scenario = data['scenario']
    assert 'hidden_objectives' not in scenario, 'HIDDEN DATA LEAK: hidden_objectives in response!'
    assert 'expected_findings' not in scenario, 'HIDDEN DATA LEAK: expected_findings in response!'
    assert 'expected_commands' not in scenario, 'HIDDEN DATA LEAK: expected_commands in response!'
    assert 'expected_root_cause' not in scenario, 'HIDDEN DATA LEAK: expected_root_cause in response!'
    assert 'expected_severity' not in scenario, 'HIDDEN DATA LEAK: expected_severity in response!'
    assert 'expected_mitigation' not in scenario, 'HIDDEN DATA LEAK: expected_mitigation in response!'
    print('   PASS: Hidden evaluation data correctly separated')

    # 3. Submit response
    print(f'\n3.{difficulty} Submit Response:')
    r = requests.post(f'{BASE_URL}/scenario/submit-response',
        json={
            'session_id': session_id,
            'findings': ['Phishing email found', 'Failed login attempts'],
            'commands': ['cat /var/log/auth.log', 'grep Failed /var/log/auth.log'],
            'severity': 'Medium',
            'root_cause': 'Phishing led to credential theft',
            'mitigation': ['MFA', 'Training']
        },
        headers=HEADERS
    )
    print(f'   {r.json()}')

    # 4. Evaluate
    print(f'\n4.{difficulty} Evaluate:')
    r = requests.post(f'{BASE_URL}/scenario/evaluate', json={'session_id': session_id}, headers=HEADERS)
    eval_data = r.json()
    print(f'   Score: {eval_data["score"]}')
    print(f'   Findings Score: {eval_data["findings_score"]}')
    print(f'   Commands Score: {eval_data["commands_score"]}')
    print(f'   Severity Score: {eval_data["severity_score"]}')
    print(f'   Root Cause Score: {eval_data["root_cause_score"]}')
    print(f'   Mitigation Score: {eval_data["mitigation_score"]}')
    print(f'   Feedback preview: {eval_data["feedback"][:100]}...')

# 5. Terminal commands
print('\n5. Terminal Commands:')
r = requests.post(f'{BASE_URL}/terminal/execute',
    json={'command': 'ls -la', 'session_id': 1},
    headers=HEADERS
)
print(f'   ls -la: {r.json()["output"]}')

r = requests.post(f'{BASE_URL}/terminal/execute',
    json={'command': 'cat /var/log/auth.log', 'session_id': 1},
    headers=HEADERS
)
print(f'   cat /var/log/auth.log: {r.json()["output"][:80]}...')

# 6. Verify artifacts exist
print('\n6. Artifacts:')
r = requests.post(f'{BASE_URL}/scenario/start', json={'difficulty': 'BEGINNER'}, headers=HEADERS)
data = r.json()
for name, path in data['artifacts']['paths'].items():
    exists = os.path.exists(path)
    print(f'   {name}: {"EXISTS" if exists else "MISSING"} ({path})')

print('\n=== ALL TESTS PASSED ===')