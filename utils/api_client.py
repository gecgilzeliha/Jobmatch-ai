import requests
import os

class JSearchClient:
    def __init__(self):
        # Hizalamaya dikkat: 8 boşluk içerde olmalı
        self.api_key = "6a978f8cbfmsh775d328e57abedap1d66cejsnbB8b1fc74949"
        self.base_url = "https://jsearch.p.rapidapi.com"
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }
    
    def search_jobs(self, query="Software Engineer", location="USA", num_pages=1, date_posted="all"):
        url = f"{self.base_url}/search"
        params = {
            "query": f"{query} in {location}",
            "page": "1",
            "num_pages": str(num_pages),
            "date_posted": date_posted
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            jobs = []
            if "data" in data:
                for job in data["data"]:
                    jobs.append(self._format_job(
