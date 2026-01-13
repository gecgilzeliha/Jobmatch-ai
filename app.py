import streamlit as st
import sys
sys.path.append('.')

from utils.api_client import JSearchClient
from utils.user_manager import UserManager, create_user_profile_template
from ml.recommender import JobRecommender
from utils.data_export import DataExporter
from ml.user_clustering import UserClusterer

# Sayfa ayarları
st.set_page_config(
    page_title="JobMatch AI - Öğrenciler için İş Bulma",
    page_icon="💼",
    layout="wide"
)

# Session state başlat
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
if 'jobs_cache' not in st.session_state:
    st.session_state.jobs_cache = []

# Managers
user_manager = UserManager()  
api_client = JSearchClient()
recommender = JobRecommender()
exporter = DataExporter()
clusterer = UserClusterer(n_clusters=3)

def login_page():
    """Giriş/Kayıt sayfası"""
    st.title("💼 JobMatch AI")
    st.subheader("Öğrenciler için AI Destekli İş Bulma Platformu")
    
    tab1, tab2 = st.tabs(["Giriş Yap", "Kayıt Ol"])
    
    with tab1:
        st.subheader("Giriş Yap")
        email = st.text_input("Email", key="login_email")
        
        if st.button("Giriş"):
            user = user_manager.get_user(email)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.success("Giriş başarılı!")
                st.rerun()
            else:
                st.error("Kullanıcı bulunamadı! Lütfen kayıt olun.")
    
    with tab2:
        st.subheader("Yeni Kayıt")
        
        with st.form("register_form"):
            name = st.text_input("Ad Soyad")
            email = st.text_input("Email")
            
            st.write("### Temel Bilgiler")
            col1, col2 = st.columns(2)
            with col1:
                age = st.number_input("Yaş", min_value=18, max_value=30, value=21)
                city = st.selectbox("Şehir", ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya"])
            with col2:
                district = st.text_input("İlçe")
                university = st.text_input("Üniversite")
            
            st.write("### Beceriler")
            skills_input = st.text_input("Beceriler (virgülle ayırın)", 
                                         placeholder="Python, JavaScript, İngilizce")
            
            st.write("### Çalışma Tercihleri")
            col1, col2 = st.columns(2)
            with col1:
                job_types = st.multiselect("İş Tipi", 
                                          ["Part-time", "Full-time", "Freelance", "Internship"])
                min_wage = st.number_input("Minimum Saat Ücreti (₺)", min_value=0, value=75)
            with col2:
                remote_pref = st.selectbox("Uzaktan Çalışma", 
                                          ["On-site", "Remote", "Hybrid", "No Preference"])
                max_distance = st.number_input("Maksimum Mesafe (km)", min_value=1, value=15)
            
            submit = st.form_submit_button("Kayıt Ol")
            
            if submit:
                if not name or not email:
                    st.error("Ad Soyad ve Email zorunludur!")
                else:
                    profile = create_user_profile_template()
                    profile.update({
                        "age": age,
                        "city": city,
                        "district": district,
                        "university": university,
                        "skills": [s.strip() for s in skills_input.split(",") if s.strip()],
                        "preferred_job_types": job_types,
                        "min_hourly_wage": min_wage,
                        "max_distance_km": max_distance,
                        "remote_preference": remote_pref
                    })
                    
                    success = user_manager.create_user(email, name, profile)
                    if success:
                        st.success("Kayıt başarılı! Şimdi giriş yapabilirsiniz.")
                    else:
                        st.error("Bu email zaten kayıtlı!")

def main_app():
    """Ana uygulama"""
    user = user_manager.get_user(st.session_state.user_email)
    
    # Sidebar
    with st.sidebar:
        st.title(f"👤 {user['name']}")
        st.write(f"📧 {user['email']}")
        
        if st.button("Çıkış Yap"):
            st.session_state.logged_in = False
            st.session_state.user_email = None
            st.rerun()
        
        st.divider()
        
        st.subheader("📊 Profiliniz")
        profile = user['profile']
        st.write(f"🎓 {profile.get('university', 'Belirtilmemiş')}")
        st.write(f"📍 {profile.get('city', '')}, {profile.get('district', '')}")
        st.write(f"💡 {len(profile.get('skills', []))} beceri")
    
    # Ana sayfa tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔍 İş Ara", "⭐ Öneriler", "👤 Profil", "📊 Veri Export", "🤖 AI Analiz"])
    
    with tab1:
        st.header("İş İlanları")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            search_query = st.text_input("Arama", value="student part time")
        with col2:
            location = st.text_input("Konum", value="Turkey")
        with col3:
            date_filter = st.selectbox("Zaman", ["today", "3days", "week", "month", "all"])
        
        if st.button("🔍 Ara", type="primary"):
            st.info("🚀 Buton tetiklendi, API'ye gidiliyor...")
            with st.spinner("İş ilanları aranıyor..."):
                try:
                    jobs = api_client.search_jobs(
                        query=search_query,
                        location=location,
                        num_pages=1,
                        date_posted=date_filter
                    )
                    st.session_state.jobs_cache = jobs
                    if not jobs:
                        st.warning("⚠️ API'den boş liste döndü. Anahtarını kontrol et!")
                except Exception as e:
                    st.error(f"❌ API Hatası: {e}")
                    
        if st.session_state.jobs_cache:
            st.success(f"✅ {len(st.session_state.jobs_cache)} ilan bulundu!")
            
            for job in st.session_state.jobs_cache[:10]:
                with st.expander(f"📌 {job['title']}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**🏢 Şirket:** {job['company']}")
                        st.write(f"**📍 Konum:** {job['location']}")
                        st.write(f"**💼 Tür:** {job['employment_type']}")
                        st.write(f"**🏠 Remote:** {'✅' if job['is_remote'] else '❌'}")
                        
                        if job['description']:
                            with st.expander("📄 Açıklama"):
                                st.write(job['description'][:500] + "...")
                    
                    with col2:
                        st.write(f"**💰 Maaş:**")
                        if job['salary']['min']:
                            st.write(f"${job['salary']['min']:,} - ${job['salary']['max']:,}")
                        else:
                            st.write("Belirtilmemiş")
                        
                        st.write(f"**📅 Yayın:**")
                        st.write(job['posted_date'][:10])
                        
                        if st.button("Başvur", key=f"apply_{job['id']}"):
                            st.success("Başvuru kaydedildi!")
                            # Başvuruyu kaydet
                            user_manager.add_application(
                                st.session_state.user_email,
                                job['id'],
                                job['title']
                            )
    
    with tab2:
        st.header("⭐ Size Özel İş Önerileri")
        
        if not st.session_state.jobs_cache:
            st.info("👈 Önce 'İş Ara' sekmesinden iş araması yapın!")
        else:
            with st.spinner("AI öneriler hesaplanıyor..."):
                recommendations = recommender.recommend_jobs(
                    user['profile'],
                    st.session_state.jobs_cache,
                    top_n=10
                )
            
            st.success(f"✨ En uygun {len(recommendations)} iş bulundu!")
            
            for i, rec in enumerate(recommendations, 1):
                job = rec['job']
                score = rec['match_score']
                breakdown = rec['score_breakdown']
                
                # Skor rengini belirle
                if score >= 80:
                    color = "🟢"
                elif score >= 60:
                    color = "🟡"
                else:
                    color = "🔴"
                
                with st.expander(f"{color} #{i} - {job['title']} (Eşleşme: %{score:.0f})"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**🏢 Şirket:** {job['company']}")
                        st.write(f"**📍 Konum:** {job['location']}")
                        st.write(f"**💼 Tür:** {job['employment_type']}")
                        st.write(f"**🏠 Remote:** {'✅' if job['is_remote'] else '❌'}")
                        
                        if job['apply_link']:
                            st.link_button("🔗 Başvur", job['apply_link'])
                    
                    with col2:
                        st.write("**📊 Eşleşme Detayları:**")
                        st.progress(score / 100)
                        
                        for key, value in breakdown.items():
                            st.write(f"{key}: %{value:.0f}")
    
    with tab3:
        st.header("👤 Profil Düzenle")
        
        with st.form("profile_edit"):
            profile = user['profile']
            
            st.write("### Beceriler")
            current_skills = ", ".join(profile.get('skills', []))
            new_skills = st.text_input("Beceriler", value=current_skills)
            
            st.write("### Çalışma Tercihleri")
            col1, col2 = st.columns(2)
            with col1:
                new_job_types = st.multiselect(
                    "İş Tipi",
                    ["Part-time", "Full-time", "Freelance", "Internship"],
                    default=profile.get('preferred_job_types', [])
                )
                new_min_wage = st.number_input(
                    "Minimum Saat Ücreti (₺)",
                    value=profile.get('min_hourly_wage', 75)
                )
            with col2:
                new_remote = st.selectbox(
                    "Uzaktan Çalışma",
                    ["On-site", "Remote", "Hybrid", "No Preference"],
                    index=["On-site", "Remote", "Hybrid", "No Preference"].index(
                        profile.get('remote_preference', 'No Preference')
                    )
                )
                new_distance = st.number_input(
                    "Maksimum Mesafe (km)",
                    value=profile.get('max_distance_km', 15)
                )
            
            if st.form_submit_button("💾 Kaydet"):
                updated_profile = {
                    'skills': [s.strip() for s in new_skills.split(",") if s.strip()],
                    'preferred_job_types': new_job_types,
                    'min_hourly_wage': new_min_wage,
                    'max_distance_km': new_distance,
                    'remote_preference': new_remote
                }
                
                user_manager.update_profile(st.session_state.user_email, updated_profile)
                st.success("✅ Profil güncellendi!")
                st.rerun()
        
        st.divider()
        
        st.write("### 📜 Başvuru Geçmişi")
        applications = user.get('application_history', [])
        if applications:
            for app in applications[-5:]:  # Son 5 başvuru
                st.write(f"- {app['job_title']} ({app['applied_at'][:10]})")
        else:
            st.info("Henüz başvuru yapmadınız.")
    
    with tab4:
        st.header("📊 Veri Export")
        st.write("Verilerinizi CSV veya Excel formatında indirin")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("👥 Kullanıcılar")
            if st.button("📥 Kullanıcıları CSV'ye Aktar"):
                try:
                    filename = exporter.export_users_to_csv(user_manager.users)
                    
                    with open(filename, 'rb') as f:
                        st.download_button(
                            label="⬇️ CSV İndir",
                            data=f,
                            file_name=filename,
                            mime='text/csv'
                        )
                    st.success(f"✅ {filename} oluşturuldu!")
                except Exception as e:
                    st.error(f"Hata: {e}")
        
        with col2:
            st.subheader("💼 İş İlanları")
            if st.session_state.jobs_cache:
                if st.button("📥 İlanları CSV'ye Aktar"):
                    try:
                        filename = exporter.export_jobs_to_csv(st.session_state.jobs_cache)
                        
                        with open(filename, 'rb') as f:
                            st.download_button(
                                label="⬇️ CSV İndir",
                                data=f,
                                file_name=filename,
                                mime='text/csv'
                            )
                        st.success(f"✅ {filename} oluşturuldu!")
                    except Exception as e:
                        st.error(f"Hata: {e}")
            else:
                st.info("Önce iş araması yapın")
        
        with col3:
            st.subheader("📊 Tümü (Excel)")
            if st.button("📥 Tüm Verileri Excel'e Aktar"):
                try:
                    filename = exporter.export_to_excel(
                        user_manager.users,
                        st.session_state.jobs_cache if st.session_state.jobs_cache else []
                    )
                    
                    with open(filename, 'rb') as f:
                        st.download_button(
                            label="⬇️ Excel İndir",
                            data=f,
                            file_name=filename,
                            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                        )
                    st.success(f"✅ {filename} oluşturuldu!")
                except Exception as e:
                    st.error(f"Hata: {e}")
        
        st.divider()
        
        st.subheader("📈 Veri İstatistikleri")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Toplam Kullanıcı", len(user_manager.users))
        
        with col2:
            st.metric("Toplam İlan", len(st.session_state.jobs_cache))
        
        with col3:
            total_apps = sum(len(u.get('application_history', [])) 
                           for u in user_manager.users.values())
            st.metric("Toplam Başvuru", total_apps)
    
    with tab5:
        st.header("🤖 AI Analiz & Machine Learning")
        
        st.subheader("📊 K-Means Clustering: Kullanıcı Segmentasyonu")
        
        all_users = list(user_manager.users.values())
        
        if len(all_users) >= 3:
            with st.spinner("Kullanıcılar kümelere ayrılıyor..."):
                clusterer.fit(all_users)
                stats = clusterer.get_cluster_stats(all_users)
            
            st.success("✅ Kullanıcılar başarıyla kümelere ayrıldı!")
            
            # Küme istatistikleri
            for cluster_name, cluster_info in stats.items():
                with st.expander(f"{cluster_info['label']} ({cluster_info['count']} kullanıcı)"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        features = cluster_info['features']
                        st.write("**Ortalama Özellikler:**")
                        st.write(f"- Yaş: {features['age']:.1f}")
                        st.write(f"- Beceri Sayısı: {features['skill_count']:.1f}")
                        st.write(f"- Min Ücret: ₺{features['min_wage']:.0f}/saat")
                        st.write(f"- Maks Mesafe: {features['max_distance']:.0f} km")
                    
                    with col2:
                        st.write(f"- Deneyim: {features['experience_months']:.1f} ay")
                        st.write(f"- GPA: {features['gpa']:.2f}")
                        st.write(f"- Remote Tercihi: %{features['prefers_remote']*100:.0f}")
                        st.write(f"- Part-time Tercihi: %{features['prefers_parttime']*100:.0f}")
            
            st.divider()
            
            # Mevcut kullanıcının kümesi
            st.subheader("📍 Sizin Kümeniz")
            my_cluster = clusterer.predict(user)
            cluster_label = stats[f"Cluster {my_cluster}"]['label']
            
            st.info(f"Siz **{cluster_label}** grubundasınız!")
            
            # Benzer kullanıcılar
            st.subheader("👥 Size Benzer Kullanıcılar")
            similar_users = clusterer.find_similar_users(user, all_users, top_n=5)
            
            if similar_users:
                for sim_user in similar_users:
                    st.write(f"- {sim_user['name']} ({sim_user['email']})")
            else:
                st.write("Şu anda sizinle aynı kümede başka kullanıcı yok.")
        
        else:
            st.warning("⚠️ Clustering için en az 3 kullanıcı gerekli!")
            st.info(f"Şu an {len(all_users)} kullanıcı var. Daha fazla kullanıcı kayıt olduğunda analiz yapılabilir.")
        
        st.divider()
        
        st.subheader("🧠 Neural Network Bilgileri")
        st.write("""
        **Kullanılan ML Teknikleri:**
        
        1. **K-Means Clustering (Unsupervised Learning)**
           - Kullanıcıları otomatik olarak gruplara ayırır
           - 8 farklı özellik kullanır (yaş, beceri, ücret, vb.)
           - StandardScaler ile özellikler normalize edilir
           
        2. **Feature Engineering**
           - Kullanıcı profili → 8 boyutlu vektör
           - İş ilanı → 10 boyutlu vektör
           - Normalizasyon ve ölçekleme
           
        3. **Scoring Algorithm**
           - Weighted sum (ağırlıklı toplam)
           - 5 farklı skor bileşeni
           - 0-100 arası nihai skor
        """)
        
        # Model bilgileri
        with st.expander("🔬 Teknik Detaylar"):
            st.code("""
# K-Means Clustering
n_clusters = 3
algorithm = 'lloyd'
random_state = 42

# Features
- age (normalized)
- skill_count (normalized)  
- min_hourly_wage (normalized)
- max_distance_km (normalized)
- experience_months (normalized)
- gpa (normalized)
- prefers_remote (binary)
- prefers_parttime (binary)

# Preprocessing
StandardScaler() - zero mean, unit variance
            """, language="python")

# Ana akış
if not st.session_state.logged_in:
    login_page()
else:
    main_app()
