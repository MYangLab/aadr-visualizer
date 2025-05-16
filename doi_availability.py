import pandas as pd
import requests
from requests.exceptions import RequestException

df = pd.read_csv("aadr_noRefPresent_v62.csv")
dois = df['doi_link'].dropna().unique()

results = []
for doi in dois:
    try:
        response = requests.head(doi, allow_redirects=True, timeout=5)
        status = response.status_code
    except RequestException as e:
        status = str(e)
    results.append((doi, status))

results_df = pd.DataFrame(results, columns=["doi_link", "status"])
results_df.to_csv("doi_link_check_v62.csv", index=False)