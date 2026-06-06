import urllib.request
import urllib.error
import json

def test_register():
    url = "http://localhost:8000/api/v1/auth/register"
    payload = {
        "email": "demo_test@devsentinel.ai",
        "display_name": "Demo Test",
        "password": "DevSentinel2026!"
    }
    req = urllib.request.Request(
        url, 
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    print("Posting payload:", payload)
    try:
        with urllib.request.urlopen(req) as response:
            print("Status:", response.status)
            print("Response:", json.dumps(json.loads(response.read().decode()), indent=2))
    except urllib.error.HTTPError as e:
        print("Status:", e.code)
        try:
            print("Response JSON:")
            print(json.dumps(json.loads(e.read().decode()), indent=2))
        except Exception as ex:
            print("Error parsing response:", ex)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_register()
