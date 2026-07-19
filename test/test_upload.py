# import requests
# import json

# with open('sample.pdf', 'rb') as f:
#     files = {'file': f}
#     response = requests.post('http://127.0.0.1:8000/api/upload', files=files)

# print('Status Code:', response.status_code)
# if response.status_code == 200:
#     data = response.json()
#     print(f"✓ Upload successful!")
#     print(f"  PDF ID: {data['pdf_id']}")
#     print(f"  File: {data['file']}")
#     print(f"  Total Pages: {data['total_pages']}")
#     print(f"  Status: {data['status']}")
#     print(f"  Download URL: {data['file_url']}")
# else:
#     print('Error:', response.json())
