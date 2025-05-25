import requests

url = "http://localhost:8979/api/user/register"
payload = {
    "email": "ducanhvna@outlook.com",
    "password": "yourpassword123",
    "full_name": "Test User Production"
}
response = requests.post(url, json=payload)
print("Status code:", response.status_code)
print("Response:", response.text)
