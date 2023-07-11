import pandas as pd
import re
df = pd.read_csv(r'results.csv')

clean_df = df.replace(to_replace = r',,\s,', value = r', ', regex = True) # clean commas in address column
clean_df['unit_price ($ per sqft)'] = clean_df['price']/clean_df['sqft'] # mutate a row called unit_price
clean_df['zipcode'] = clean_df['address'].str.extract(r'.*([0-9]{5})') # extract zipcode from address
clean_df = clean_df.sort_values(by='zipcode') # sort by zipcode
clean_df

#now, we could group/order by zipcode/area if needed using SQL