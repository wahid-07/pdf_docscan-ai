# import requests

# # Download PDF from database
# response = requests.get('http://127.0.0.1:8000/api/pdf/1')

# print(f'Status Code: {response.status_code}')
# print(f'Content-Type: {response.headers.get("content-type")}')
# print(f'Content-Disposition: {response.headers.get("content-disposition")}')
# print(f'Downloaded bytes: {len(response.content)}')
# print(f'First 10 bytes: {response.content[:10]}')

# # Save downloaded PDF to verify
# with open('downloaded.pdf', 'wb') as f:
#     f.write(response.content)
# print(f'\n✓ PDF downloaded and saved to downloaded.pdf')
