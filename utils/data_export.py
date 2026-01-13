import pandas as pd
import json
from datetime import datetime
from typing import List, Dict

class DataExporter:
    """Verileri CSV/Excel'e aktarma"""
    
    def __init__(self):
        self.export_folder = "exports"
        
    def export_users_to_csv(self, users_data: Dict) -> str:
        """Kullanıcıları CSV'ye aktar"""
        
        # Kullanıcı verilerini düzleştir (flatten)
        rows = []
        for email, user in users_data.items():
            profile = user.get('profile', {})
            
            row = {
                'ID': user.get('id'),
                'Name': user.get('name'),
                'Email': user.get('email'),
                'Created At': user.get('created_at', '')[:10],
                'Age': profile.get('age'),
                'City': profile.get('city'),
                'District': profile.get('district'),
                'University': profile.get('university'),
                'Skills': ', '.join(profile.get('skills', [])),
                'Education Level': profile.get('education_level'),
                'Department': profile.get('department'),
                'GPA': profile.get('gpa'),
                'Min Hourly Wage': profile.get('min_hourly_wage'),
                'Max Distance (km)': profile.get('max_distance_km'),
                'Preferred Job Types': ', '.join(profile.get('preferred_job_types', [])),
                'Remote Preference': profile.get('remote_preference'),
                'Experience (months)': profile.get('experience_months'),
                'Total Applications': len(user.get('application_history', []))
            }
            rows.append(row)
        
        df = pd.DataFrame(rows)
        
        # CSV'ye kaydet
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"users_export_{timestamp}.csv"
        
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        return filename
    
    def export_jobs_to_csv(self, jobs: List[Dict]) -> str:
        """İş ilanlarını CSV'ye aktar"""
        
        rows = []
        for job in jobs:
            row = {
                'Job ID': job.get('id'),
                'Title': job.get('title'),
                'Company': job.get('company'),
                'Location': job.get('location'),
                'City': job.get('job_city'),
                'State': job.get('job_state'),
                'Country': job.get('job_country'),
                'Employment Type': job.get('employment_type'),
                'Is Remote': 'Yes' if job.get('is_remote') else 'No',
                'Posted Date': job.get('posted_date', '')[:10],
                'Min Salary': job.get('salary', {}).get('min'),
                'Max Salary': job.get('salary', {}).get('max'),
                'Currency': job.get('salary', {}).get('currency'),
                'Required Skills': ', '.join(job.get('required_skills', [])),
                'Apply Link': job.get('apply_link'),
                'Description': job.get('description', '')[:200] + '...'  # İlk 200 karakter
            }
            rows.append(row)
        
        df = pd.DataFrame(rows)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"jobs_export_{timestamp}.csv"
        
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        return filename
    
    def export_recommendations_to_csv(self, recommendations: List[Dict]) -> str:
        """AI önerilerini CSV'ye aktar"""
        
        rows = []
        for rec in recommendations:
            job = rec['job']
            
            row = {
                'Match Score': rec['match_score'],
                'Job Title': job.get('title'),
                'Company': job.get('company'),
                'Location': job.get('location'),
                'Employment Type': job.get('employment_type'),
                'Is Remote': 'Yes' if job.get('is_remote') else 'No',
                'Location Score': rec['score_breakdown'].get('location', 0),
                'Skills Score': rec['score_breakdown'].get('skills', 0),
                'Salary Score': rec['score_breakdown'].get('salary', 0),
                'Job Type Score': rec['score_breakdown'].get('job_type', 0),
                'Freshness Score': rec['score_breakdown'].get('freshness', 0),
                'Apply Link': job.get('apply_link')
            }
            rows.append(row)
        
        df = pd.DataFrame(rows)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recommendations_export_{timestamp}.csv"
        
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        return filename
    
    def export_to_excel(self, users_data: Dict, jobs: List[Dict], 
                       recommendations: List[Dict] = None) -> str:
        """Tüm verileri tek Excel dosyasına aktar (multiple sheets)"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"jobmatch_data_export_{timestamp}.xlsx"
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            
            # Sheet 1: Users
            user_rows = []
            for email, user in users_data.items():
                profile = user.get('profile', {})
                user_rows.append({
                    'ID': user.get('id'),
                    'Name': user.get('name'),
                    'Email': user.get('email'),
                    'Age': profile.get('age'),
                    'City': profile.get('city'),
                    'Skills': ', '.join(profile.get('skills', [])),
                    'Min Wage': profile.get('min_hourly_wage'),
                    'Applications': len(user.get('application_history', []))
                })
            
            df_users = pd.DataFrame(user_rows)
            df_users.to_excel(writer, sheet_name='Users', index=False)
            
            # Sheet 2: Jobs
            job_rows = []
            for job in jobs:
                job_rows.append({
                    'Title': job.get('title'),
                    'Company': job.get('company'),
                    'Location': job.get('location'),
                    'Type': job.get('employment_type'),
                    'Remote': 'Yes' if job.get('is_remote') else 'No',
                    'Posted': job.get('posted_date', '')[:10]
                })
            
            df_jobs = pd.DataFrame(job_rows)
            df_jobs.to_excel(writer, sheet_name='Jobs', index=False)
            
            # Sheet 3: Recommendations (if available)
            if recommendations:
                rec_rows = []
                for rec in recommendations:
                    job = rec['job']
                    rec_rows.append({
                        'Score': rec['match_score'],
                        'Job': job.get('title'),
                        'Company': job.get('company'),
                        'Location': job.get('location')
                    })
                
                df_recs = pd.DataFrame(rec_rows)
                df_recs.to_excel(writer, sheet_name='Recommendations', index=False)
        
        return filename


# Test
if __name__ == "__main__":
    exporter = DataExporter()
    
    # Test data
    test_users = {
        "test@student.com": {
            "id": "U001",
            "name": "Test User",
            "email": "test@student.com",
            "created_at": "2026-01-08",
            "profile": {
                "age": 21,
                "city": "Istanbul",
                "skills": ["Python", "JavaScript"],
                "min_hourly_wage": 75
            },
            "application_history": []
        }
    }
    
    filename = exporter.export_users_to_csv(test_users)
    print(f"✅ CSV oluşturuldu: {filename}")