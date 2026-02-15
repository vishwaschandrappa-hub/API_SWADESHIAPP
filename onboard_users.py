import json
import urllib.request
import urllib.error
import sys

# Configuration
API_URL = "https://api-swadeshiapp.onrender.com" 
DATA_FILE = "onboarding_data.json"

def onboard_users():
    try:
        with open(DATA_FILE, 'r') as f:
            users = json.load(f)
    except FileNotFoundError:
        print(f"Error: File {DATA_FILE} not found.")
        return

    print(f"Found {len(users)} users to onboard...")

    for user in users:
        print(f"Onboarding {user['name']} ({user['email']})...")
        try:
            url = f"{API_URL}/user"
            # Add default password
            user['password'] = "password123"
            data = json.dumps(user).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
            
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    print(f"✅ Success! User ID: {user['user_id']}")
                else:
                    print(f"❌ Failed. Status: {response.status}")
        except urllib.error.HTTPError as e:
             print(f"❌ Failed. Status: {e.code} - {e.reason}")
             print(f"   Response: {e.read().decode('utf-8')}")
        except Exception as e:
            print(f"❌ Error connecting to API: {e}")

if __name__ == "__main__":
    # Allow overriding URL via command line
    if len(sys.argv) > 1:
        API_URL = sys.argv[1]
    
    print(f"Targeting API: {API_URL}")
    onboard_users()
