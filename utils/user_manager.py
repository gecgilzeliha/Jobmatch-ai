import json
import os
from datetime import datetime
from typing import Optional, Dict, List

class UserManager:
    """Kullanıcı kayıt ve profil yönetimi"""
    
    def __init__(self, data_file="data/users.json"):
        self.data_file = data_file
        self.users = self._load_users()
    
    def _load_users(self) -> Dict:
        """Kullanıcıları dosyadan yükle"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_users(self):
        """Kullanıcıları dosyaya kaydet"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, ensure_ascii=False, indent=2)
    
    def create_user(self, email: str, name: str, profile_data: Dict) -> bool:
        """Yeni kullanıcı oluştur"""
        
        if email in self.users:
            return False  # Kullanıcı zaten var
        
        user_id = f"U{len(self.users) + 1:03d}"
        
        self.users[email] = {
            "id": user_id,
            "email": email,
            "name": name,
            "created_at": datetime.now().isoformat(),
            "profile": profile_data,
            "application_history": []
        }
        
        self._save_users()
        return True
    
    def get_user(self, email: str) -> Optional[Dict]:
        """Kullanıcı bilgilerini getir"""
        return self.users.get(email)
    
    def update_profile(self, email: str, profile_data: Dict) -> bool:
        """Kullanıcı profilini güncelle"""
        
        if email not in self.users:
            return False
        
        self.users[email]["profile"].update(profile_data)
        self._save_users()
        return True
    
    def add_application(self, email: str, job_id: str, job_title: str):
        """Başvuru geçmişine ekle"""
        
        if email not in self.users:
            return False
        
        application = {
            "job_id": job_id,
            "job_title": job_title,
            "applied_at": datetime.now().isoformat()
        }
        
        self.users[email]["application_history"].append(application)
        self._save_users()
        return True
    
    def get_all_users(self) -> List[Dict]:
        """Tüm kullanıcıları listele"""
        return list(self.users.values())


def create_user_profile_template():
    """Kullanıcı profili için template"""
    return {
        # Kişisel Bilgiler
        "age": None,
        "city": "",
        "district": "",
        "location": {
            "lat": None,
            "lon": None
        },
        
        # Beceriler ve Deneyim
        "skills": [],  # ["Python", "Java", "İngilizce"]
        "education_level": "",  # "Lisans", "Yüksek Lisans"
        "department": "",  # "Bilgisayar Mühendisliği"
        "university": "",
        "gpa": None,
        "graduation_year": None,
        
        # Çalışma Tercihleri
        "available_days": [],  # ["Pazartesi", "Salı", "Çarşamba"]
        "available_hours": [],  # ["09:00-13:00", "14:00-18:00"]
        "preferred_job_types": [],  # ["Part-time", "Freelance", "Internship"]
        "preferred_categories": [],  # ["Software Development", "Data Entry"]
        "min_hourly_wage": None,
        "max_distance_km": None,
        "remote_preference": "",  # "Remote", "Hybrid", "On-site", "No Preference"
        
        # Deneyim
        "experience_months": 0,
        "previous_jobs": [],  # Liste of job descriptions
        "languages": [],  # [{"language": "İngilizce", "level": "Advanced"}]
        
        # İletişim
        "phone": "",
        "linkedin": "",
        "github": "",
        "portfolio": ""
    }


# Test
if __name__ == "__main__":
    manager = UserManager()
    
    # Örnek kullanıcı oluştur
    profile = create_user_profile_template()
    profile.update({
        "age": 21,
        "city": "Istanbul",
        "district": "Kadıköy",
        "skills": ["Python", "JavaScript", "React"],
        "education_level": "Lisans",
        "department": "Bilgisayar Mühendisliği",
        "available_days": ["Pazartesi", "Çarşamba", "Cuma"],
        "preferred_job_types": ["Part-time", "Remote"],
        "min_hourly_wage": 75,
        "max_distance_km": 15
    })
    
    success = manager.create_user(
        email="test@university.edu",
        name="Test User",
        profile_data=profile
    )
    
    if success:
        print("✅ Kullanıcı oluşturuldu!")
        user = manager.get_user("test@university.edu")
        print(json.dumps(user, ensure_ascii=False, indent=2))
    else:
        print("❌ Kullanıcı zaten mevcut!")