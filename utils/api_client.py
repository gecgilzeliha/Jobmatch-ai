import requests
import os
from dotenv import load_dotenv

load_dotenv()

class JSearchClient:
    """JSearch API (RapidAPI) ile iş ilanlarını çeker"""
    
    def __init__(self):
        self.api_key = os.getenv("RAPIDAPI_KEY")
        self.base_url = "https://jsearch.p.rapidapi.com"
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }
    
    def search_jobs(self, query="part time student", location="Turkey", 
                    num_pages=1, date_posted="today"):
        """İş ilanlarını ara"""
        
        url = f"{self.base_url}/search"
        
        params = {
            "query": query,
            "page": "1",
            "num_pages": str(num_pages),
            "date_posted": date_posted
        }
        
        if location:
            params["query"] = f"{query} in {location}"
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            jobs = []
            if "data" in data:
                for job in data["data"]:
                    formatted_job = self._format_job(job)
                    jobs.append(formatted_job)
            
            return jobs
        
        except requests.exceptions.RequestException as e:
            print(f"API Hatası: {e}")
            return []
    
    def _format_job(self, raw_job):
        """API'den gelen ham veriyi düzenle"""
        
        return {
            "id": raw_job.get("job_id", ""),
            "title": raw_job.get("job_title", ""),
            "company": raw_job.get("employer_name", ""),
            "location": raw_job.get("job_city", "") or raw_job.get("job_country", ""),
            "description": raw_job.get("job_description", ""),
            "employment_type": raw_job.get("job_employment_type", ""),
            "posted_date": raw_job.get("job_posted_at_datetime_utc", ""),
            "salary": {
                "min": raw_job.get("job_min_salary"),
                "max": raw_job.get("job_max_salary"),
                "currency": raw_job.get("job_salary_currency", "USD")
            },
            "required_skills": raw_job.get("job_required_skills", []),
            "apply_link": raw_job.get("job_apply_link", ""),
            "is_remote": raw_job.get("job_is_remote", False),
            "job_google_link": raw_job.get("job_google_link", ""),
            "raw_data": raw_job
        }


def test_api():
    """API'yi test et"""
    
    client = JSearchClient()
    
    print("🔍 İş ilanları aranıyor...")
    jobs = client.search_jobs(
        query="part time student",
        location="Istanbul, Turkey",
        num_pages=1,
        date_posted="week"
    )
    
    print(f"\n✅ {len(jobs)} iş ilanı bulundu!\n")
    
    if jobs:
        print("📋 İlk 3 ilan:")
        for i, job in enumerate(jobs[:3], 1):
            print(f"\n{i}. {job['title']}")
            print(f"   Şirket: {job['company']}")
            print(f"   Konum: {job['location']}")
            print(f"   Tür: {job['employment_type']}")
            print(f"   Remote: {'Evet' if job['is_remote'] else 'Hayır'}")


if __name__ == "__main__":
    test_api()
