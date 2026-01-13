import requests
import os

# .env dosyası varsa yükle, yoksa direkt key kullan
try:
    from dotenv import load_dotenv
    load_dotenv()
    USE_ENV = True
except ImportError:
    USE_ENV = False
    print("⚠️  python-dotenv kurulu değil, direkt API key kullanılacak")

class JSearchClient:
    """JSearch API (RapidAPI) ile iş ilanlarını çeker"""
    
    def __init__(self):
        # Alttaki satırı direkt böyle yaz, os.getenv falan kullanma:
        self.api_key = "6a978f8cbfmsh775d328e57abedap1d66cejsnbB8b1fc74949"
        
        self.base_url = "https://jsearch.p.rapidapi.com"
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }
        
            # Geçici çözüm: API key'i buraya yazın
            # Mevcut os.getenv satırını sil, yerine bunu yapıştır:
    
    
    def search_jobs(self, query="part time student", location="Turkey", 
                    num_pages=1, date_posted="today"):
        """
        İş ilanlarını ara
        
        Args:
            query: Arama terimi (örn: "part time student", "freelance")
            location: Konum (örn: "Istanbul, Turkey", "Turkey")
            num_pages: Kaç sayfa sonuç (her sayfa ~10 ilan)
            date_posted: "all", "today", "3days", "week", "month"
        
        Returns:
            List of job dictionaries
        """
        
        url = f"{self.base_url}/search"
        
        params = {
            "query": query,
            "page": "1",
            "num_pages": str(num_pages),
            "date_posted": date_posted
        }
        
        # Eğer location belirtildiyse ekle
        if location:
            params["query"] = f"{query} in {location}"
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # API'den gelen veriyi temizle ve formatla
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
            "employment_type": raw_job.get("job_employment_type", ""),  # FULLTIME, PARTTIME, etc.
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
            
            # Ek bilgiler
            "raw_data": raw_job  # Tüm ham veriyi sakla (gerekirse)
        }
    
    def get_job_details(self, job_id):
        """Belirli bir iş ilanının detaylarını getir"""
        
        url = f"{self.base_url}/job-details"
        
        params = {
            "job_id": job_id
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if "data" in data and len(data["data"]) > 0:
                return self._format_job(data["data"][0])
            
            return None
        
        except requests.exceptions.RequestException as e:
            print(f"API Hatası: {e}")
            return None
    
    def search_multiple_queries(self, queries, location="Turkey"):
        """
        Birden fazla arama terimi için iş ara
        
        Args:
            queries: Liste ["part time", "freelance", "student job"]
            location: Konum
        
        Returns:
            Tüm sonuçların birleşimi
        """
        
        all_jobs = []
        seen_ids = set()
        
        for query in queries:
            jobs = self.search_jobs(query=query, location=location, num_pages=1)
            
            # Tekrar eden ilanları filtrele
            for job in jobs:
                if job["id"] not in seen_ids:
                    all_jobs.append(job)
                    seen_ids.add(job["id"])
        
        return all_jobs


# Test fonksiyonu
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
