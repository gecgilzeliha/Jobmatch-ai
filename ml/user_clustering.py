import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from typing import List, Dict
import json

class UserClusterer:
    """K-Means ile kullanıcı segmentasyonu"""
    
    def __init__(self, n_clusters=3):
        self.n_clusters = n_clusters
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        self.scaler = StandardScaler()     #Btüm özelliklere eşit mesafede yaklaşır.#
        self.feature_names = []
        
    def extract_features(self, users: List[Dict]) -> np.ndarray:
        ##kullanıcıyı sayı dizine dönüştürüyor
        
        features = []
        self.feature_names = [
            'age', 'skill_count', 'min_wage', 'max_distance',
            'experience_months', 'gpa', 'prefers_remote', 'prefers_parttime'
        ]
        
        for user in users:
            profile = user.get('profile', {})
            
            # Yaş
            age = profile.get('age', 21)
            
            # Beceri sayısı
            skill_count = len(profile.get('skills', []))
            
            # Ücret beklentisi
            min_wage = profile.get('min_hourly_wage', 75)
            
            # Maksimum mesafe
            max_distance = profile.get('max_distance_km', 15)
            
            # Deneyim (ay)
            experience = profile.get('experience_months', 0)
            
            # GPA
            gpa = profile.get('gpa', 3.0) if profile.get('gpa') else 3.0
            
            # Remote tercihi (0-1)
            remote_pref = 1 if profile.get('remote_preference') in ['Remote', 'Hybrid'] else 0
            
            # Part-time tercihi (0-1)
            job_types = profile.get('preferred_job_types', [])
            parttime_pref = 1 if any('part' in jt.lower() for jt in job_types) else 0
            
            features.append([
                age, skill_count, min_wage, max_distance,
                experience, gpa, remote_pref, parttime_pref
            ])
        
        return np.array(features)
    
    def fit(self, users: List[Dict]):
        """Kullanıcıları kümelere ayır"""
        
        if len(users) < self.n_clusters:
            print(f"⚠️ Kullanıcı sayısı ({len(users)}) küme sayısından ({self.n_clusters}) az!")
            return
        
        # Özellik çıkar
        X = self.extract_features(users)
        
        # Normalize et
        X_scaled = self.scaler.fit_transform(X)
        
        # K-Means fit
        self.kmeans.fit(X_scaled)
        
        return self
    
    def predict(self, user: Dict) -> int:
        """Tek bir kullanıcının kümesini tahmin et"""
        
        X = self.extract_features([user])
        X_scaled = self.scaler.transform(X)
        cluster = self.kmeans.predict(X_scaled)[0]
        
        return cluster
    
    def get_cluster_stats(self, users: List[Dict]) -> Dict:
        """Her kümenin özelliklerini analiz et"""
        
        X = self.extract_features(users)
        X_scaled = self.scaler.fit_transform(X)
        labels = self.kmeans.fit_predict(X_scaled)
        
        stats = {}
        
        for cluster_id in range(self.n_clusters):
            cluster_mask = labels == cluster_id
            cluster_data = X[cluster_mask]
            
            if len(cluster_data) == 0:
                continue
            
            # Her özellik için ortalama
            avg_features = np.mean(cluster_data, axis=0)
            
            stats[f"Cluster {cluster_id}"] = {
                'count': int(np.sum(cluster_mask)),
                'features': {
                    name: round(float(value), 2)
                    for name, value in zip(self.feature_names, avg_features)
                },
                'label': self._get_cluster_label(avg_features)
            }
        
        return stats
    
    def _get_cluster_label(self, features: np.ndarray) -> str:    ##kümelere isim veriyor
        
        
        age, skill_count, min_wage, max_distance, experience, gpa, remote, parttime = features
        
        # Basit kural tabanlı etiketleme
        if experience < 6 and skill_count < 4:
            return "🌱 Yeni Başlayanlar"
        elif remote > 0.5 and min_wage > 100:
            return "💻 Remote Profesyoneller"
        elif parttime > 0.5 and max_distance < 10:
            return "🎓 Part-time Öğrenciler"
        elif skill_count >= 5 and experience >= 12:
            return "⭐ Deneyimliler"
        elif min_wage < 80 and max_distance > 15:
            return "🚀 Esnek ve Uyumlu"
        else:
            return "👥 Genel Grup"
    
    def find_similar_users(self, user: Dict, all_users: List[Dict], top_n=5) -> List[Dict]:  ##x 1. kümede, y de 1. kümede. O zaman x'in beğendiği işi y'e de önerelim
        """Bir kullanıcıya benzer kullanıcıları bul (aynı kümeden)"""
        
        user_cluster = self.predict(user)
        
        similar = []
        for other_user in all_users:
            if other_user['email'] != user['email']:
                other_cluster = self.predict(other_user)
                if other_cluster == user_cluster:
                    similar.append(other_user)
        
        return similar[:top_n]


# Test
if __name__ == "__main__":
    # Örnek kullanıcılar
    test_users = [
        {
            "email": "user1@test.com",
            "name": "User 1",
            "profile": {
                "age": 20,
                "skills": ["Python", "Java"],
                "min_hourly_wage": 60,
                "max_distance_km": 10,
                "experience_months": 3,
                "gpa": 3.2,
                "remote_preference": "On-site",
                "preferred_job_types": ["Part-time"]
            }
        },
        {
            "email": "user2@test.com",
            "name": "User 2",
            "profile": {
                "age": 24,
                "skills": ["Python", "React", "Node", "AWS", "Docker"],
                "min_hourly_wage": 120,
                "max_distance_km": 25,
                "experience_months": 18,
                "gpa": 3.7,
                "remote_preference": "Remote",
                "preferred_job_types": ["Full-time", "Remote"]
            }
        },
        {
            "email": "user3@test.com",
            "name": "User 3",
            "profile": {
                "age": 21,
                "skills": ["Excel", "PowerPoint"],
                "min_hourly_wage": 50,
                "max_distance_km": 8,
                "experience_months": 0,
                "gpa": 2.8,
                "remote_preference": "On-site",
                "preferred_job_types": ["Part-time", "Internship"]
            }
        }
    ]
    
    clusterer = UserClusterer(n_clusters=2)
    clusterer.fit(test_users)
    
    stats = clusterer.get_cluster_stats(test_users)
    
    print("📊 Küme İstatistikleri:\n")
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    print("\n🔍 User 1 hangi kümede?")
    cluster = clusterer.predict(test_users[0])
    print(f"Küme: {cluster}")