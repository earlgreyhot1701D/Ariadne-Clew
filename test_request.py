import requests

response = requests.post(
    "http://127.0.0.1:5000/v1/recap", json={"chat_log": "print('hello world')"}
)

print("Status:", response.status_code)
print("Response:", response.text)
