# tasks.py

from datetime import datetime, timedelta
import requests

# Subtract 5 days from today
today = datetime.now()
five_days_ago = today - timedelta(days=1)

# Format the dates to the required format
current_date = today.strftime('%b%%20%d,%%20%Y%%2000:00:AM')
filter_from_date = five_days_ago.strftime('%b%%20%d,%%20%Y%%2000:00:AM')
filter_to_date = today.strftime('%b%%20%d,%%20%Y%%2000:00:AM')

url = f'https://andon.sageclarity.com/AndonCenter/getAndonEntryDataTable.do?lineIds=1383,1384,1385,1386,1387,1388,1389,1390,1391,1392,1393,1394,1395,1396,1397,1398,1399,1400,1401,1402,1403,1404,1405,1406,1407,1408,1409,1410,1411,1412,1413,1414,1415,1416,1417,1419,1420,1421,1423,1424,1425,1426,1427,1428,1429,1430,1431,1437,1438,1440,1442,1444,1446,1448,1450,1452,1454,1455,1456,1457,1459,1461,1463,1572,1573,1574,1575,1576,1577,1578,1579,1580&currentDate={current_date}&companyId=71&pageNumber=1&statusIds=421,422,423,424,425,426&order=0&rowsPerPage=5125&filterFromDate={filter_from_date}&filterToDate={filter_to_date}&_dc=1718803882854'
print(url)
response = requests.get(url)
print(response.status_code)  # Print the status code to see if the request is successful
print(response.text)  # Print the response text to see the content retrieved
