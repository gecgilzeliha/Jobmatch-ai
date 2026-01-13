import math
from typing import List, Dict, Tuple
import re

class JobRecommender:
    """AI tabanlı iş önerme sistemi"""
    
    def __init__(self):
        self.weights = {
            'location': 0.25,      # Konum uyumu
            'skills': 0.30,        # Beceri eşleşmesi
            'salary': 0.20,        # Ücret uyumu
            'job_type': 0.15,      # İş tipi (part-time, remote, etc.)
            'freshness': 0.10      # İlanın ne kadar yeni olduğu
        }
    
    def calculate_distance(self, lat1: float, lon1: float, 
                          lat2: float, lon2: float) -> float:
        """İki nokta arası mesafe (Haversine formula) - km cinsinden"""
        
        if not all([lat1, lon1, lat2, lon2]):
            return float('inf')
        
        R = 6371  # Dünya yarıçapı (km)
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        return distance
    
    def score_location(self, user_profile: Dict, job: Dict) -> float:
        """Konum uyumu skoru (0-1)"""
        
        # Remote işler için maksimum skor
        if job.get('job_is_remote', False):
            if user_profile.get('remote_preference') in ['Remote', 'No Preference']:
                return 1.0
            else:
                return 0.7  # Remote tercih etmese bile kabul edilebilir
        
        # Kullanıcı konumu yoksa düşük skor
        user_loc = user_profile.get('location', {})
        if not user_loc.get('lat') or not user_loc.get('lon'):
            return 0.5  # Varsayılan orta skor
        
        # İş konumu parse et (job_latitude ve job_longitude API'den geliyor)
        job_lat = job.get('job_latitude')
        job_lon = job.get('job_longitude')
        
        if not job_lat or not job_lon:
            return 0.5
        
        # Mesafe hesapla
        distance = self.calculate_distance(
            user_loc['lat'], user_loc['lon'],
            job_lat, job_lon
        )
        
        max_distance = user_profile.get('max_distance_km', 20)
        
        if distance <= max_distance:
            # Mesafe ne kadar kısa o kadar yüksek skor
            return max(0.0, 1.0 - (distance / max_distance))
        else:
            # Maksimum mesafenin dışında azalan skor
            return max(0.0, 0.3 - (distance - max_distance) / 100)
    
    def score_skills(self, user_profile: Dict, job: Dict) -> float:
        """Beceri eşleşmesi skoru (0-1)"""
        
        user_skills = set([s.lower() for s in user_profile.get('skills', [])])
        
        if not user_skills:
            return 0.5  # Beceri bilgisi yoksa orta skor
        
        # İş açıklamasından beceri çıkar
        job_desc = job.get('job_description', '').lower()
        job_title = job.get('job_title', '').lower()
        
        # API'den gelen required_skills varsa kullan
        job_skills = job.get('job_required_skills', [])
        if job_skills:
            job_skills = set([s.lower() for s in job_skills])
        else:
            # Açıklamadan beceri çıkar (basit keyword matching)
            job_skills = set()
        
        # Açıklamada kullanıcının becerilerini ara
        matched_skills = 0
        for skill in user_skills:
            if skill in job_desc or skill in job_title:
                matched_skills += 1
        
        if len(user_skills) == 0:
            return 0.5
        
        match_ratio = matched_skills / len(user_skills)
        
        # En az bir beceri eşleşirse bonus
        if matched_skills > 0:
            return min(1.0, 0.5 + match_ratio * 0.5)
        else:
            return 0.3
    
    def score_salary(self, user_profile: Dict, job: Dict) -> float:
        """Ücret uyumu skoru (0-1)"""
        
        min_wage = user_profile.get('min_hourly_wage')
        
        if not min_wage:
            return 0.7  # Ücret tercihi belirtmemişse nötr skor
        
        job_min = job.get('job_min_salary')
        job_max = job.get('job_max_salary')
        
        # Maaş bilgisi yoksa orta skor
        if not job_min and not job_max:
            return 0.6
        
        # Aylık/yıllık maaşı saatlik ücrete çevir (yaklaşık)
        salary_period = job.get('job_salary_period', '').upper()
        
        if salary_period == 'YEAR' and job_min:
            job_min = job_min / (52 * 40)  # Yıllık -> saatlik
        elif salary_period == 'MONTH' and job_min:
            job_min = job_min / (4 * 40)  # Aylık -> saatlik
        
        if job_min and job_min >= min_wage:
            # Beklentinin üzerindeyse yüksek skor
            return min(1.0, 0.7 + (job_min - min_wage) / min_wage * 0.3)
        elif job_max and job_max >= min_wage:
            return 0.8
        else:
            return 0.4  # Beklentinin altında
    
    def score_job_type(self, user_profile: Dict, job: Dict) -> float:
        """İş tipi uyumu skoru (0-1)"""
        
        preferred_types = user_profile.get('preferred_job_types', [])
        
        if not preferred_types:
            return 0.7  # Tercih belirtmemişse nötr
        
        job_type = job.get('job_employment_type', '').upper()
        
        # Tercih edilen tipleri kontrol et
        type_mapping = {
            'PART-TIME': ['PARTTIME', 'PART_TIME', 'PART-TIME'],
            'FULL-TIME': ['FULLTIME', 'FULL_TIME', 'FULL-TIME'],
            'FREELANCE': ['CONTRACTOR', 'FREELANCE'],
            'INTERNSHIP': ['INTERN', 'INTERNSHIP']
        }
        
        for pref in preferred_types:
            pref_upper = pref.upper()
            for key, variations in type_mapping.items():
                if pref_upper in key and job_type in variations:
                    return 1.0
        
        return 0.5
    
    def score_freshness(self, job: Dict) -> float:
        """İlanın ne kadar yeni olduğu skoru (0-1)"""
        
        posted_at = job.get('job_posted_at_timestamp')
        
        if not posted_at:
            return 0.5
        
        import time
        current_time = time.time()
        age_hours = (current_time - posted_at) / 3600
        
        # 24 saat içinde: 1.0
        # 1 hafta içinde: 0.7
        # 1 ay içinde: 0.4
        if age_hours <= 24:
            return 1.0
        elif age_hours <= 168:  # 1 hafta
            return 0.9 - (age_hours - 24) / 168 * 0.2
        elif age_hours <= 720:  # 1 ay
            return 0.7 - (age_hours - 168) / 720 * 0.3
        else:
            return 0.4
    
    def calculate_match_score(self, user_profile: Dict, job: Dict) -> Tuple[float, Dict]:
        """Toplam eşleşme skoru ve detaylar"""
        
        scores = {
            'location': self.score_location(user_profile, job),
            'skills': self.score_skills(user_profile, job),
            'salary': self.score_salary(user_profile, job),
            'job_type': self.score_job_type(user_profile, job),
            'freshness': self.score_freshness(job)
        }
        
        # Ağırlıklı toplam
        total_score = sum(scores[k] * self.weights[k] for k in scores)
        
        # 0-100 skalasına çevir
        final_score = total_score * 100
        
        return final_score, scores
    
    def recommend_jobs(self, user_profile: Dict, jobs: List[Dict], 
                      top_n: int = 10) -> List[Dict]:
        """Kullanıcıya en uygun işleri öner"""
        
        recommendations = []
        
        for job in jobs:
            score, score_details = self.calculate_match_score(user_profile, job)
            
            recommendations.append({
                'job': job,
                'match_score': round(score, 2),
                'score_breakdown': {k: round(v * 100, 1) for k, v in score_details.items()}
            })
        
        # Skora göre sırala (yüksekten düşüğe)
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        
        return recommendations[:top_n]


# Test
if __name__ == "__main__":
    recommender = JobRecommender()
    
    # Örnek kullanıcı profili
    user = {
        "skills": ["Python", "JavaScript", "React"],
        "location": {"lat": 41.0082, "lon": 28.9784},  # İstanbul
        "min_hourly_wage": 75,
        "max_distance_km": 15,
        "preferred_job_types": ["Part-time", "Remote"],
        "remote_preference": "Hybrid"
    }
    
    # Örnek iş
    job = {
        "job_id": "123",
        "job_title": "Junior Python Developer",
        "job_description": "Looking for a Python developer with React experience",
        "job_latitude": 41.0150,
        "job_longitude": 28.9800,
        "job_is_remote": False,
        "job_employment_type": "PARTTIME",
        "job_min_salary": 80,
        "job_posted_at_timestamp": 1767830400
    }
    
    score, details = recommender.calculate_match_score(user, job)
    
    print(f"Eşleşme Skoru: {score:.1f}/100")
    print("\nDetaylar:")
    for key, value in details.items():
        print(f"  {key}: {value*100:.1f}/100")