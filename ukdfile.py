import requests

url = "https://uploads.brookfieldcomfort.com/xStockFile1.csv"
local_filename = "C:/brookfieldcomfort/xStockFile1.csv"

try:
    response = requests.get(url)
    response.raise_for_status()

    with open(local_filename, 'wb') as f:
        f.write(response.content)

    print("Success")
except Exception as e:
    print("Error:", e)
