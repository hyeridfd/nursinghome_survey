import streamlit as st
import json
from datetime import datetime

def show_basic_survey(supabase, elderly_id, surveyor_id, nursing_home_id):
    st.title("📝 1. 기초 조사표 (건강설문 조사표)")
    
    # 진행 상태 초기화
    if 'basic_page' not in st.session_state:
        st.session_state.basic_page = 1
    
    # 기존 데이터 불러오기
    if 'basic_data' not in st.session_state:
        try:
            response = supabase.table('basic_survey').select('*').eq('elderly_id', elderly_id).execute()
            if response.data:
                st.session_state.basic_data = response.data[0]
            else:
                st.session_state.basic_data = {}
        except:
            st.session_state.basic_data = {}
    
    # 페이지 진행 표시
    total_pages = 5
    st.progress(st.session_state.basic_page / total_pages)
    st.caption(f"페이지 {st.session_state.basic_page} / {total_pages}")
    
    # 페이지별 내용
    if st.session_state.basic_page == 1:
        show_page1()
    elif st.session_state.basic_page == 2:
        show_page2()
    elif st.session_state.basic_page == 3:
        show_page3()
    elif st.session_state.basic_page == 4:
        show_page4()
    elif st.session_state.basic_page == 5:
        show_page5(supabase, elderly_id, surveyor_id, nursing_home_id)

def show_page1():
    """1페이지: 인구통계학적 특성"""
    st.subheader("인구통계학적 특성")
    
    data = st.session_state.basic_data
    
    col1, col2 = st.columns(2)
    
    with col1:
        gender = st.radio(
            "1. 성별",
            options=["남자", "여자"],
            index=0 if data.get('gender') == "남자" else 1 if data.get('gender') == "여자" else 0,
            key="gender"
        )
        
        age = st.number_input(
            "2. 연령 (만 나이)",
            min_value=0,
            max_value=120,
            value=int(data.get('age', 0)) if data.get('age') else 0,
            key="age"
        )
        
        care_grade = st.selectbox(
            "3. 노인장기요양등급",
            options=["인지지원등급", "5등급", "4등급", "3등급", "2등급", "1등급", "기타"],
            index=0,
            key="care_grade"
        )
    
    with col2:
        residence_duration = st.selectbox(
            "4. 시설 거주 기간",
            options=["1년 미만", "1년 이상 ~ 2년 미만", "2년 이상 ~ 3년 미만", "3년 이상"],
            index=0,
            key="residence_duration"
        )
        
        education = st.selectbox(
            "5. 교육수준",
            options=["무학", "초등학교", "중학교", "고등학교", "대학교 이상"],
            index=0,
            key="education"
        )
        
        drinking_smoking = st.selectbox(
            "6. 음주/흡연",
            options=["안함", "과거에 했음", "현재 하고 있음"],
            index=0,
            key="drinking_smoking"
        )
    
    # 데이터 저장
    st.session_state.basic_data.update({
        'gender': gender,
        'age': age,
        'care_grade': care_grade,
        'residence_duration': residence_duration,
        'education': education,
        'drinking_smoking': drinking_smoking
    })
    
    navigation_buttons()

def show_page2():
    """2페이지: 질환 정보"""
    st.subheader("질환 정보")
    
    data = st.session_state.basic_data
    
    st.write("**7. 현재 앓고 있는 질환 (복수 선택 가능)**")
    
    disease_options = [
        "고혈압", "당뇨병", "고지혈증", "심혈관 질환(심근경색, 협심증, 부정맥 등)",
        "뇌혈관 질환(뇌졸중, 뇌경색, 뇌출혈 등)", "갑상선 질환", "골다공증", "골관절염/류마티스 관절염",
        "암", "만성 폐쇄성 폐질환", "신장 질환", "간 질환", "위장 질환", "빈혈", "치매",
        "파킨슨병", "우울증", "기타"
    ]
    
    existing_diseases = data.get('diseases', [])
    if isinstance(existing_diseases, str):
        existing_diseases = json.loads(existing_diseases) if existing_diseases else []
    
    col1, col2, col3 = st.columns(3)
    selected_diseases = []
    
    for i, disease in enumerate(disease_options):
        with [col1, col2, col3][i % 3]:
            if st.checkbox(disease, value=disease in existing_diseases, key=f"disease_{i}"):
                selected_diseases.append(disease)
    
    if "기타" in selected_diseases:
        other_disease = st.text_input("기타 질환 입력", key="other_disease")
        if other_disease:
            selected_diseases.append(f"기타: {other_disease}")
    
    st.markdown("---")
    
    st.write("**8. 현재 복용 중인 약물 (복수 선택 가능)**")
    
    medication_options = [
        "고혈압약", "당뇨병약", "고지혈증약", "항혈전제", "심장약",
        "갑상선약", "골다공증약", "진통소염제", "항암제", "천식약",
        "신장약", "간약", "위장약", "철분제", "치매약",
        "파킨슨약", "항우울제", "기타"
    ]
    
    existing_medications = data.get('medications', [])
    if isinstance(existing_medications, str):
        existing_medications = json.loads(existing_medications) if existing_medications else []
    
    col1, col2, col3 = st.columns(3)
    selected_medications = []
    
    for i, medication in enumerate(medication_options):
        with [col1, col2, col3][i % 3]:
            if st.checkbox(medication, value=medication in existing_medications, key=f"med_{i}"):
                selected_medications.append(medication)
    
    if "기타" in selected_medications:
        other_medication = st.text_input("기타 약물 입력", key="other_medication")
        if other_medication:
            selected_medications.append(f"기타: {other_medication}")
    
    st.markdown("---")
    
    medication_count = st.selectbox(
        "9. 약물 복용 개수",
        options=["5개 미만", "5개 이상"],
        index=0,
        key="medication_count"
    )
    
    # 데이터 저장
    st.session_state.basic_data.update({
        'diseases': json.dumps(selected_diseases, ensure_ascii=False),
        'medications': json.dumps(selected_medications, ensure_ascii=False),
        'medication_count': medication_count
    })
    
    navigation_buttons()

def show_page3():
    """3페이지: 식사 관련 특성"""
    st.subheader("식사 관련 특성")
    
    data = st.session_state.basic_data
    
    col1, col2 = st.columns(2)
    
    with col1:
        chewing_difficulty = st.radio(
            "10. 씹기 어려움",
            options=["예", "아니오"],
            index=0 if data.get('chewing_difficulty') == True else 1,
            key="chewing_difficulty"
        )
        
        swallowing_difficulty = st.radio(
            "11. 삼키기 어려움",
            options=["예", "아니오"],
            index=0 if data.get('swallowing_difficulty') == True else 1,
            key="swallowing_difficulty"
        )
        
        food_preparation_method = st.selectbox(
            "12. 음식 조리 형태",
            options=["일반식", "잘게 썬 음식", "갈은 음식", "믹서 음식(유동식)", "기타"],
            index=0,
            key="food_preparation_method"
        )
    
    with col2:
        eating_independence = st.selectbox(
            "13. 식사 독립성",
            options=["독립적", "부분 도움 필요", "전적으로 도움 필요"],
            index=0,
            key="eating_independence"
        )
        
        meal_type = st.selectbox(
            "14. 식사 유형",
            options=["일반식", "치료식(당뇨식, 저염식 등)", "연하곤란식", "기타"],
            index=0,
            key="meal_type"
        )
    
    # 데이터 저장
    st.session_state.basic_data.update({
        'chewing_difficulty': chewing_difficulty == "예",
        'swallowing_difficulty': swallowing_difficulty == "예",
        'food_preparation_method': food_preparation_method,
        'eating_independence': eating_independence,
        'meal_type': meal_type
    })
    
    navigation_buttons()

def show_page4():
    """4페이지: 기능/건강 상태"""
    st.subheader("기능/건강 상태")
    
    data = st.session_state.basic_data
    
    col1, col2 = st.columns(2)
    
    with col1:
        height = st.number_input(
            "15. 신장 (cm)",
            min_value=0.0,
            max_value=250.0,
            value=float(data.get('height', 0)) if data.get('height') else 0.0,
            step=0.1,
            key="height"
        )
        
        weight = st.number_input(
            "16. 체중 (kg)",
            min_value=0.0,
            max_value=200.0,
            value=float(data.get('weight', 0)) if data.get('weight') else 0.0,
            step=0.1,
            key="weight"
        )
        
        waist = st.number_input(
            "17. 허리둘레 (cm)",
            min_value=0.0,
            max_value=200.0,
            value=float(data.get('waist_circumference', 0)) if data.get('waist_circumference') else 0.0,
            step=0.1,
            key="waist"
        )
        
        # BMI 자동 계산
        if height > 0 and weight > 0:
            bmi = weight / ((height / 100) ** 2)
            st.info(f"BMI: {bmi:.2f} kg/m²")
    
    with col2:
        systolic_bp = st.number_input(
            "18. 수축기 혈압 (mmHg)",
            min_value=0,
            max_value=300,
            value=int(data.get('systolic_bp', 0)) if data.get('systolic_bp') else 0,
            key="systolic_bp"
        )
        
        diastolic_bp = st.number_input(
            "19. 이완기 혈압 (mmHg)",
            min_value=0,
            max_value=200,
            value=int(data.get('diastolic_bp', 0)) if data.get('diastolic_bp') else 0,
            key="diastolic_bp"
        )
        
        k_mbi = st.number_input(
            "20. K-MBI 점수 (0-100점)",
            min_value=0,
            max_value=100,
            value=int(data.get('k_mbi_score', 0)) if data.get('k_mbi_score') else 0,
            key="k_mbi",
            help="한국판 수정 바델 지수 (Korean Modified Barthel Index)"
        )
        
        mmse = st.number_input(
            "21. MMSE-K 점수 (0-30점)",
            min_value=0,
            max_value=30,
            value=int(data.get('mmse_score', 0)) if data.get('mmse_score') else 0,
            key="mmse",
            help="간이정신상태검사 한국판 (Mini-Mental State Examination-Korean)"
        )
    
    # 데이터 저장
    st.session_state.basic_data.update({
        'height': height,
        'weight': weight,
        'waist_circumference': waist,
        'systolic_bp': systolic_bp,
        'diastolic_bp': diastolic_bp,
        'k_mbi_score': k_mbi,
        'mmse_score': mmse
    })
    
    navigation_buttons()

def show_page5(supabase, elderly_id, surveyor_id, nursing_home_id):
    """5페이지: 시설 특성 및 제출"""
    st.subheader("시설 특성")
    
    data = st.session_state.basic_data
    
    col1, col2 = st.columns(2)
    
    with col1:
        facility_capacity = st.number_input(
            "22. 시설 정원 (명)",
            min_value=0,
            max_value=1000,
            value=int(data.get('facility_capacity', 0)) if data.get('facility_capacity') else 0,
            key="facility_capacity"
        )
        
        facility_location = st.selectbox(
            "23. 시설 소재지",
            options=["서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종",
                    "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"],
            index=0,
            key="facility_location"
        )
    
    with col2:
        nutritionist_present = st.radio(
            "24. 영양사 배치 여부",
            options=["예", "아니오"],
            index=0 if data.get('nutritionist_present') == True else 1,
            key="nutritionist_present"
        )
    
    # 데이터 저장
    st.session_state.basic_data.update({
        'facility_capacity': facility_capacity,
        'facility_location': facility_location,
        'nutritionist_present': nutritionist_present == "예"
    })
    
    st.markdown("---")
    
    # 제출 버튼
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("⬅️ 이전", use_container_width=True):
            st.session_state.basic_page -= 1
            st.rerun()
    
    with col2:
        pass
    
    with col3:
        if st.button("✅ 제출", use_container_width=True, type="primary"):
            # 필수 항목 검증
            required_fields = ['gender', 'age', 'care_grade']
            missing = [f for f in required_fields if not st.session_state.basic_data.get(f)]
            
            if missing:
                st.error(f"필수 항목을 입력해주세요: {', '.join(missing)}")
            else:
                save_basic_survey(supabase, elderly_id, surveyor_id, nursing_home_id)

def save_basic_survey(supabase, elderly_id, surveyor_id, nursing_home_id):
    """설문 데이터 저장"""
    try:
        data = st.session_state.basic_data.copy()
        data.update({
            'elderly_id': elderly_id,
            'surveyor_id': surveyor_id,
            'nursing_home_id': nursing_home_id,
            'updated_at': datetime.now().isoformat()
        })
        
        # 기존 데이터 확인
        response = supabase.table('basic_survey').select('id').eq('elderly_id', elderly_id).execute()
        
        if response.data:
            # 업데이트
            supabase.table('basic_survey').update(data).eq('elderly_id', elderly_id).execute()
        else:
            # 새로 추가
            supabase.table('basic_survey').insert(data).execute()
        
        # 진행 상황 업데이트
        supabase.table('survey_progress').update({
            'basic_survey_completed': True,
            'last_updated': datetime.now().isoformat()
        }).eq('elderly_id', elderly_id).execute()
        
        st.success("✅ 기초 조사표가 저장되었습니다!")
        
        # 세션 초기화
        del st.session_state.basic_data
        del st.session_state.basic_page
        st.session_state.current_survey = None
        
        st.balloons()
        
        if st.button("대시보드로 돌아가기"):
            st.rerun()
        
    except Exception as e:
        st.error(f"저장 중 오류가 발생했습니다: {str(e)}")

def navigation_buttons():
    """페이지 이동 버튼"""
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.session_state.basic_page > 1:
            if st.button("⬅️ 이전", use_container_width=True):
                st.session_state.basic_page -= 1
                st.rerun()
    
    with col2:
        if st.button("🏠 대시보드", use_container_width=True):
            # 세션 초기화
            if 'basic_data' in st.session_state:
                del st.session_state.basic_data
            if 'basic_page' in st.session_state:
                del st.session_state.basic_page
            st.session_state.current_survey = None
            st.rerun()
    
    with col3:
        if st.session_state.basic_page < 5:
            if st.button("다음 ➡️", use_container_width=True, type="primary"):
                st.session_state.basic_page += 1
                st.rerun()
