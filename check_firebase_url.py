import json
with open('firebase-key.json') as f:
    creds = json.load(f)
    project_id = creds.get('project_id')
    print(f'Project ID: {project_id}')
    print(f'Database URL: https://{project_id}-default-rtdb.firebaseio.com')

# Check if we're using the right URL in app.py
import app as app_module
print(f'\nApp is initializing with hardcoded URL')
print(f'Expected URL: https://ethiohealthcare-6ad15-default-rtdb.firebaseio.com')
