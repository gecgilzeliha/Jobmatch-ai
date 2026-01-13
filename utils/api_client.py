import requests
import os

class JSearchClient:
    def __init__(self):
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
            return [self._format_job(job) for job in data.get("data", [])]
        except Exception as e:
            print(f"API Hatası: {e}")
            return []

    def _format_job(self, raw_job):
        return {
            "id": raw_job.get("job_id", ""),
            "title": raw_job.get("job_title", ""),
            "company": raw_job.get("employer_name", ""),
            "location": f"{raw_job.get('job_city', '')}, {raw_job.get('job_country', '')}",
            "description": raw_job.get("job_description", ""),
            "employment_type": raw_job.get("job_employment_type", ""),
            "posted_date": raw_job.get("job_posted_at_datetime_utc", ""),
            "salary": {"min": raw_job.get("job_min_salary"), "max": raw_job.get("job_max_salary"), "currency": "USD"},
            "apply_link": raw_job.get("job_apply_link", ""),
            "is_remote": raw_job.get("job_is_remote", False)
        }
