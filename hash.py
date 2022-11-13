import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests

# Get hashrate data from NASDAQ API
hr_response = requests.get('https://data.nasdaq.com/api/v3/datasets/BCHAIN/HRATE.json?api_key=CEZ47Us4M6dvsFYzReoG')
hr_data = hr_response.json()['dataset']['data']
hr_df = pd.DataFrame.from_records(hr_data, columns=['Date', 'Hashrate'])
hr_df['Day'] = list(reversed(range(0, len(hr_df.index))))
hr_df.sort_values(by='Day', ascending=True, inplace=True)
hr_df.reset_index(drop=True, inplace=True)

# Plot hashrate
fig, ax = plt.subplots(1, 1)
ax.plot(hr_df['Day'].loc[3000:], hr_df['Hashrate'].loc[3000:])
plt.show()
