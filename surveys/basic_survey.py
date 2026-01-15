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
    total_pages = 7  # 5페이지에서 7페이지로 증가
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
        show_page5_kmbi()  # K-MBI 평가
    elif st.session_state.basic_page == 6:
        show_page6_mmse()  # MMSE-K 평가
    elif st.session_state.basic_page == 7:
        show_page7(supabase, elderly_id, surveyor_id, nursing_home_id)  # 시설 특성 및 제출

def show_page1():
    """1페이지: 인구통계학적 특성"""
    st.subheader("인구통계학적 특성")
    
    data = st.session_state.basic_data
    
    col1, col2 = st.columns(2)
    
    with col1:
        gender = st.radio(
            "1. 귀하의 성별은 선택해 주십시오",
            options=["남자", "여자"],
            index=0 if data.get('gender') == "남자" else 1 if data.get('gender') == "여자" else 0,
            key="gender"
        )
        
        age = st.number_input(
            "2. 귀하의 연령을 작성해 주십시오(만 나이)",
            min_value=0,
            max_value=120,
            value=int(data.get('age', 0)) if data.get('age') else 0,
            key="age"
        )
        
        care_grade = st.selectbox(
            "3. 다음 중 귀하가 받으신 장기요양등급을 선택해 주십시오",
            options=["1등급", "2등급", "3등급", "4등급 이상"],
            index=0,
            key="care_grade"
        )
    
    with col2:
        residence_duration = st.selectbox(
            "4. 귀하가 현재 요양시설에 거주하신 기간은 얼마나 되셨습니까?",
            options=["1년 미만", "1년 이상 ~ 3년 미만", "3년 이상 ~ 5년 미만", "5년 이상 ~ 10년 미만", "10년 이상"],
            index=0,
            key="residence_duration"
        )
        
        education = st.selectbox(
            "5. 귀하의 최종 학력을 선택해 주십시오",
            options=["무학", "초등학교 졸업", "중학교 졸업", "고등학교 졸업", "대학교(전문대 포함) 졸업 이상"],
            index=0,
            key="education"
        )
        
        drinking_smoking = st.selectbox(
            "6. 귀하는 음주 및 흡연을 하고 계십니까?",
            options=["둘 다 안함", "과거에 음주를 했음", "과거에 흡연을 했음", "현재 음주하고 있음", "현재 흡연하고 있음", "둘 다 하고 있음"],
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
    
    st.write("**7. 귀하가 현재 보유하고 계신 질환을 모두 선택해 주십시오**")
    
    disease_options = [
        "없음", "고혈압", "당뇨병", "고지혈증", "심혈관 질환(심근경색, 협심증, 부정맥 등)",
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
        "복용하지 않음", "고혈압약", "당뇨병약", "고지혈증약", "항혈전제", "심장약",
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
        options=["1개", "2개", "3개", "4개 이상"],
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
            "10. 귀하는 음식을 씹는 데 어려움이 있습니까?",
            options=["예", "아니오"],
            index=0 if data.get('chewing_difficulty') == True else 1,
            key="chewing_difficulty"
        )
        
        swallowing_difficulty = st.radio(
            "11. 귀하는 음식을 삼키는 데 어려움이 있습니까?",
            options=["예", "아니오"],
            index=0 if data.get('swallowing_difficulty') == True else 1,
            key="swallowing_difficulty"
        )
        
        food_preparation_method = st.selectbox(
            "12. 씹기 또는 삼키기에 어려움이 있다면, 귀하가 해당하는 음식 섭취 방법을 선택해 주십시오",
            options=["어렵지 않음", "일반식", "잘게 썬 음식", "갈은 음식", "믹서 음식(유동식)", "기타"],
            index=0,
            key="food_preparation_method"
        )
    
    with col2:
        eating_independence = st.selectbox(
            "13. 귀하는 평소 식사하실 때 어떻게 식사하십니까?",
            options=["스스로 식사할 수 있음", "요양보호사 등의 부분적인 도움 필요", "요양보호사 등의 전적인 도움 필요"],
            index=0,
            key="eating_independence"
        )
        
        meal_type = st.selectbox(
            "14. 귀하는 평소 식사하실 때 어떤 형태의 식사를 드십니까?",
            options=["일반식", "다진식", "연하식", "기타"],
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
    """4페이지: 기본 건강 측정치"""
    st.subheader("기본 건강 측정치")
    
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
    
    # 데이터 저장
    st.session_state.basic_data.update({
        'height': height,
        'weight': weight,
        'waist_circumference': waist,
        'systolic_bp': systolic_bp,
        'diastolic_bp': diastolic_bp
    })
    
    navigation_buttons()

def show_page5_kmbi():
    """
    페이지 5: K-MBI (한국판 수정 바델 지수) 평가
    5단계 간편 평가 방식
    """
    st.header("📋 5. K-MBI (한국판 수정 바델 지수)")
    
    st.info("""
    **K-MBI 평가 안내**
    
    각 항목에 대해 대상자의 현재 수행 능력을 평가해주세요.
    """)
    
    # K-MBI 평가 옵션 (5단계)
    kmbi_options = [
        "과제를 수행할 수 없는 경우",
        "최대의 도움이 필요한 경우",
        "중등도의 도움이 필요한 경우",
        "최소한의 도움이 필요하거나 감시가 필요한 경우",
        "완전히 독립적인 경우"
    ]
    
    # 점수 매핑 (5단계 → 0-4점)
    score_mapping = {
        "과제를 수행할 수 없는 경우": 0,
        "최대의 도움이 필요한 경우": 1,
        "중등도의 도움이 필요한 경우": 2,
        "최소한의 도움이 필요하거나 감시가 필요한 경우": 3,
        "완전히 독립적인 경우": 4
    }
    
    # 11개 K-MBI 평가 항목
    kmbi_items = [
        {"name": "개인위생", "description": "세수, 머리 빗기, 칫솔질, 면도 등", "key": "kmbi_1"},
        {"name": "목욕하기", "description": "목욕 또는 샤워", "key": "kmbi_2"},
        {"name": "식사하기", "description": "음식을 먹는 동작", "key": "kmbi_3"},
        {"name": "용변처리", "description": "화장실 사용 및 뒤처리", "key": "kmbi_4"},
        {"name": "계단 오르기", "description": "계단 오르고 내리기", "key": "kmbi_5"},
        {"name": "옷 입기", "description": "옷과 신발 착용", "key": "kmbi_6"},
        {"name": "대변조절", "description": "대변 조절 능력", "key": "kmbi_7"},
        {"name": "소변조절", "description": "소변 조절 능력", "key": "kmbi_8"},
        {"name": "보행", "description": "실내외 이동", "key": "kmbi_9"},
        {"name": "의자차", "description": "휠체어 사용", "key": "kmbi_10"},
        {"name": "의자/침대 이동", "description": "의자나 침대로의 이동", "key": "kmbi_11"}
    ]
    
    data = st.session_state.basic_data
    
    # 각 항목 평가
    st.subheader("📝 항목별 평가")
    
    for idx, item in enumerate(kmbi_items, 1):
        with st.container():
            st.markdown(f"### {idx}. {item['name']}")
            st.caption(f"📌 {item['description']}")
            
            current_value = data.get(item['key'], kmbi_options[0])
            
            selected = st.radio(
                f"{item['name']} 수행 수준",
                options=kmbi_options,
                index=kmbi_options.index(current_value) if current_value in kmbi_options else 0,
                key=f"radio_{item['key']}",
                label_visibility="collapsed",
                horizontal=False
            )
            
            data[item['key']] = selected
            st.divider()
    
    # 총점 계산 (0-44점 → 100점 만점으로 환산)
    total_raw_score = sum(score_mapping.get(data.get(item['key'], kmbi_options[0]), 0) 
                          for item in kmbi_items)
    
    # 100점 만점으로 환산 (44점 만점 * 100/44)
    kmbi_score = round((total_raw_score / 44) * 100, 1)
    data['k_mbi_score'] = kmbi_score
    
    # 결과 해석
    st.subheader("📊 K-MBI 평가 결과")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("원점수", f"{total_raw_score}/44점")
    
    with col2:
        st.metric("환산점수", f"{kmbi_score}/100점")
    
    with col3:
        if kmbi_score >= 90:
            status = "독립"
            status_color = "🟢"
        elif kmbi_score >= 75:
            status = "경도 의존"
            status_color = "🟡"
        elif kmbi_score >= 60:
            status = "중등도 의존"
            status_color = "🟠"
        elif kmbi_score >= 40:
            status = "중증 의존"
            status_color = "🔴"
        else:
            status = "완전 의존"
            status_color = "⚫"
        
        st.metric("의존도", f"{status_color} {status}")
    
    # 상태별 해석
    st.info(f"""
    **해석 기준**
    - 90-100점: 독립 (일상생활 수행 가능)
    - 75-89점: 경도 의존 (약간의 도움 필요)
    - 60-74점: 중등도 의존 (상당한 도움 필요)
    - 40-59점: 중증 의존 (대부분의 활동에 도움 필요)
    - 0-39점: 완전 의존 (거의 모든 활동에 도움 필요)
    
    **현재 평가**: {kmbi_score}점 - {status}
    """)
    
    # 항목별 수행 수준 요약
    st.subheader("📋 항목별 수행 수준 요약")
    
    # 수정된 부분: defaultdict 사용
    from collections import defaultdict
    level_groups = defaultdict(list)
    
    for item in kmbi_items:
        level = data.get(item['key'], kmbi_options[0])
        level_groups[level].append(item['name'])
    
    # 레벨별 항목 표시
    level_colors = {
        "완전히 독립적인 경우": "🟢",
        "최소한의 도움이 필요하거나 감시가 필요한 경우": "🟡",
        "중등도의 도움이 필요한 경우": "🟠",
        "최대의 도움이 필요한 경우": "🔴",
        "과제를 수행할 수 없는 경우": "⚫"
    }
    
    for level in kmbi_options[::-1]:  # 역순으로 표시 (독립 → 의존)
        if level in level_groups and level_groups[level]:
            st.markdown(f"{level_colors.get(level, '⚪')} **{level}**: {', '.join(level_groups[level])}")
    navigation_buttons()



def show_page6_mmse():
    """6페이지: MMSE-K (간이정신상태검사 한국판) 평가"""
    st.subheader("MMSE-K (간이정신상태검사 한국판) 평가")
    
    st.info("📝 인지기능을 평가합니다. 각 문항에 정답이면 해당 점수를 부여합니다.")
    
    data = st.session_state.basic_data
    
    # MMSE-K 평가 항목
    mmse_sections = [
        {
            "category": "지남력 (시간)",
            "items": [
                {"question": "오늘은 몇 년도입니까?", "score": 1},
                {"question": "몇 월입니까?", "score": 1},
                {"question": "몇 일입니까?", "score": 1},
                {"question": "무슨 요일입니까?", "score": 1},
                {"question": "무슨 계절입니까?", "score": 1}
            ]
        },
        {
            "category": "지남력 (장소)",
            "items": [
                {"question": "여기는 무슨 도(시/군)입니까?", "score": 1},
                {"question": "여기는 무슨 시(군/구)입니까?", "score": 1},
                {"question": "여기는 무슨 동(읍/면)입니까?", "score": 1},
                {"question": "여기는 어디입니까? (요양원, 병원 등)", "score": 1},
                {"question": "여기는 무엇을 하는 곳입니까?(예: 치료실)", "score": 1}
            ]
        },
        {
            "category": "기억등록",
            "items": [
                {"question": "세 가지 단어 즉시 따라하기 (나무, 자동차, 모자)", "score": 3}
            ]
        },
        {
            "category": "주의집중 및 계산",
            "items": [
                {"question": "100에서 7을 계속해서 빼세요. (100-7=? 그 다음은?)", "score": 5}
            ],
            "note": "또는 '삼천리강산'을 거꾸로 말하세요."
        },
        {
            "category": "기억회상",
            "items": [
                {"question": "아까 세 가지 단어가 무엇이었습니까? (나무, 자동차, 모자)", "score": 3}
            ]
        },
        {
            "category": "언어기능 - 이름 맞추기",
            "items": [
                {"question": "이것이 무엇입니까? (연필)", "score": 1},
                {"question": "이것이 무엇입니까? (시계)", "score": 1}
            ]
        },
        {
            "category": "언어기능 - 3단계 명령",
            "items": [
                {"question": "오른손으로 종이를 들어서 / 반으로 접어 / 무릎 위에 놓으세요", "score": 3}
            ]
        },
        {
            "category": "언어기능 - 복사",
            "items": [
                {"question": "오각형 2개가 겹쳐진 그림을 따라 그리세요", "score": 1}
            ]
        },
        {
            "category": "언어기능 - 반복",
            "items": [
                {"question": "간장 공장 공장장 따라하기", "score": 1}
            ]
        },
        {
            "category": "이해 및 판단 - 이해",
            "items": [
                {"question": "왜 옷은 빨아서 입습니까?", "score": 1}
            ]
        },
        {
            "category": "이해 및 판단 - 판단",
            "items": [
                {"question": "길에서 주민등록증을 주웠을 때 어떻게 하면 쉽게 주인에게 돌려줄 수 있습니까?", "score": 1}
            ]
        }                
    ]
    
    total_score = 0
    section_index = 0
    
    for section in mmse_sections:
        st.markdown(f"### {section['category']}")
        
        if 'note' in section:
            st.caption(f"💡 {section['note']}")
        
        for item_index, item in enumerate(section['items']):
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.write(item['question'])
            
            with col2:
                key = f"mmse_{section_index}_{item_index}"
                
                if item['score'] == 1:
                    correct = st.checkbox("정답", key=key)
                    if correct:
                        total_score += 1
                else:
                    score_value = st.number_input(
                        f"점수 (0-{item['score']})",
                        min_value=0,
                        max_value=item['score'],
                        value=0,
                        key=key,
                        label_visibility="collapsed"
                    )
                    total_score += score_value
        
        section_index += 1
        st.markdown("---")
    
    # 총점 표시
    st.markdown("### 📊 MMSE-K 총점")
    st.metric("총점", f"{total_score}점 / 30점")
    
    # 해석 (교육 수준별 정상 기준)
    st.markdown("#### 인지기능 평가 결과")
    education = data.get('education', '')
    
    if '무학' in education:
        cutoff = 19
    elif '초등학교' in education:
        cutoff = 22
    elif '중학교' in education or '고등학교' in education:
        cutoff = 24
    else:
        cutoff = 24
    
    if total_score >= cutoff:
        st.success(f"✅ **정상 인지기능**: {total_score}점 (기준: {cutoff}점 이상)")
    elif total_score >= cutoff - 4:
        st.warning(f"⚠️ **경도 인지장애 의심**: {total_score}점 (기준: {cutoff}점 이상)")
    else:
        st.error(f"🚨 **인지장애 의심**: {total_score}점 (기준: {cutoff}점 이상)")
    
    st.info(f"💡 교육 수준별 정상 기준: 무학 ≥19점, 초졸 ≥22점, 중졸 이상 ≥24점")
    
    # 데이터 저장
    st.session_state.basic_data['mmse_score'] = total_score
    
    navigation_buttons()

def show_page7(supabase, elderly_id, surveyor_id, nursing_home_id):
    """7페이지: 시설 특성 및 제출"""
    st.subheader("시설 특성")
    
    data = st.session_state.basic_data
    
    col1, col2 = st.columns(2)
    
    with col1:
        facility_capacity = st.number_input(
            "시설 규모 (어르신 수용 인원(명))",
            min_value=0,
            max_value=1000,
            value=int(data.get('facility_capacity', 0)) if data.get('facility_capacity') else 0,
            key="facility_capacity"
        )
        
        facility_location = st.selectbox(
            "시설 소재지",
            options=["수도권(서울, 경기, 인천)", "충청권(대전, 세종, 충남, 충북)", 
                    "호남권(광주, 전남, 전북)", "영남권(부산, 대구, 울산, 경남, 경북)", 
                    "강원권", "제주권"],
            index=0,
            key="facility_location"
        )
    
    with col2:
        nutritionist_present = st.radio(
            "영양사 배치 여부",
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
    
    # 평가 점수 요약
    st.subheader("📊 평가 점수 요약")
    
    col1, col2 = st.columns(2)
    
    with col1:
        kmbi_score = data.get('k_mbi_score', 0)
        st.metric("K-MBI", f"{kmbi_score}점 / 100점")
        
        if kmbi_score >= 90:
            st.success("독립적")
        elif kmbi_score >= 60:
            st.warning("중등도 의존")
        else:
            st.error("중증 의존")
    
    with col2:
        mmse_score = data.get('mmse_score', 0)
        st.metric("MMSE-K", f"{mmse_score}점 / 30점")
        
        education = data.get('education', '')
        if '무학' in education:
            cutoff = 19
        elif '초등학교' in education:
            cutoff = 22
        else:
            cutoff = 24
        
        if mmse_score >= cutoff:
            st.success("정상 인지기능")
        else:
            st.error("인지장애 의심")
    
    st.markdown("---")
    
    # 제출 버튼
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
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
        if st.button("✅ 제출", use_container_width=True, type="primary"):
            # 필수 항목 검증
            required_fields = ['gender', 'age', 'care_grade', 'k_mbi_score', 'mmse_score']
            missing = [f for f in required_fields if not st.session_state.basic_data.get(f)]
            
            if missing:
                st.error(f"필수 항목을 입력해주세요: {', '.join(missing)}")
            else:
                save_basic_survey(supabase, elderly_id, surveyor_id, nursing_home_id)

def save_basic_survey(supabase, elderly_id, surveyor_id, nursing_home_id):
    """
    기초 조사 데이터를 Supabase에 저장 (K-MBI 텍스트→숫자 변환 포함)
    """
    try:
        data = st.session_state.basic_data
        
        # === K-MBI 텍스트→점수 매핑 ===
        kmbi_score_mapping = {
            "과제를 수행할 수 없는 경우": 0,
            "최대의 도움이 필요한 경우": 1,
            "중등도의 도움이 필요한 경우": 2,
            "최소한의 도움이 필요하거나 감시가 필요한 경우": 3,
            "완전히 독립적인 경우": 4
        }
        
        # === 1단계: 테이블 스키마 조회 ===
        try:
            schema_check = supabase.table('basic_survey').select('*').limit(1).execute()
            available_columns = set(schema_check.data[0].keys()) if schema_check.data else set()
        except:
            available_columns = {
                'elderly_id', 'surveyor_id', 'nursing_home_id', 'updated_at',
                'gender', 'age', 'care_grade', 'residence_duration', 'education',
                'drinking_smoking', 'diseases', 'medications', 'medication_count',
                'chewing_difficulty', 'swallowing_difficulty', 'food_preparation_method',
                'eating_independence', 'meal_type', 'height', 'weight',
                'waist_circumference', 'systolic_bp', 'diastolic_bp',
                'facility_capacity', 'facility_location', 'nutritionist_present'
            }
        
        # === 2단계: 기본 필수 데이터 ===
        survey_data = {
            'elderly_id': elderly_id,
            'surveyor_id': surveyor_id,
            'nursing_home_id': nursing_home_id,
            'updated_at': datetime.now().isoformat()
        }
        
        # === 3단계: 기존 필드 추가 ===
        field_mapping = {
            'gender': 'gender',
            'age': 'age',
            'care_grade': 'care_grade',
            'residence_duration': 'residence_duration',
            'education': 'education',
            'drinking_smoking': 'drinking_smoking',
            'chewing_difficulty': 'chewing_difficulty',
            'swallowing_difficulty': 'swallowing_difficulty',
            'food_preparation_method': 'food_preparation_method',
            'eating_independence': 'eating_independence',
            'meal_type': 'meal_type',
            'height': 'height',
            'weight': 'weight',
            'waist_circumference': 'waist_circumference',
            'systolic_bp': 'systolic_bp',
            'diastolic_bp': 'diastolic_bp',
            'facility_capacity': 'facility_capacity',
            'facility_location': 'facility_location',
            'nutritionist_present': 'nutritionist_present',
            'medication_count': 'medication_count'
        }
        
        for field_key, column_name in field_mapping.items():
            if field_key in data and column_name in available_columns:
                survey_data[column_name] = data[field_key]
        
        # === 4단계: JSON 필드 처리 ===
        if 'diseases' in data and 'diseases' in available_columns:
            survey_data['diseases'] = json.dumps(data['diseases'])
        if 'medications' in data and 'medications' in available_columns:
            survey_data['medications'] = json.dumps(data['medications'])
        
        # === 5단계: K-MBI 데이터 (텍스트→숫자 변환) ===
        if 'k_mbi_score' in available_columns:
            if 'k_mbi_score' in data:
                survey_data['k_mbi_score'] = data['k_mbi_score']
            
            # K-MBI 각 항목 변환 (텍스트 → 점수)
            for i in range(1, 12):
                col_name = f'kmbi_{i}'
                if col_name in available_columns and col_name in data:
                    value = data[col_name]
                    # 텍스트인 경우 점수로 변환
                    if isinstance(value, str):
                        survey_data[col_name] = kmbi_score_mapping.get(value, 0)
                    else:
                        survey_data[col_name] = value
        else:
            st.warning("⚠️ K-MBI 데이터는 저장되지 않았습니다. (데이터베이스 컬럼 없음)")
        
        # === 6단계: MMSE-K 데이터 ===
        mmse_fields = [
            'mmse_score', 'mmse_time_orientation', 'mmse_place_orientation',
            'mmse_registration', 'mmse_attention_calculation', 'mmse_recall',
            'mmse_naming', 'mmse_repetition', 'mmse_comprehension',
            'mmse_reading', 'mmse_writing', 'mmse_drawing'
        ]
        
        mmse_saved = False
        for field in mmse_fields:
            if field in available_columns and field in data:
                survey_data[field] = data[field]
                mmse_saved = True
        
        if not mmse_saved and any(f in data for f in mmse_fields):
            st.warning("⚠️ MMSE-K 데이터는 저장되지 않았습니다. (데이터베이스 컬럼 없음)")
        
        # === 7단계: 기존 데이터 확인 ===
        existing = supabase.table('basic_survey') \
            .select('id') \
            .eq('elderly_id', elderly_id) \
            .execute()
        
        # === 8단계: 저장 실행 ===
        if existing.data:
            result = supabase.table('basic_survey') \
                .update(survey_data) \
                .eq('elderly_id', elderly_id) \
                .execute()
        else:
            result = supabase.table('basic_survey') \
                .insert(survey_data) \
                .execute()
        
        # === 9단계: 진행 상태 업데이트 ===
        try:
            supabase.table('survey_progress') \
                .update({
                    'basic_survey_completed': True,
                    'last_updated': datetime.now().isoformat()
                }) \
                .eq('elderly_id', elderly_id) \
                .execute()
        except Exception as e:
            st.warning(f"진행 상태 업데이트 실패: {str(e)}")
        
        # === 10단계: 성공 처리 ===
        st.success("✅ 기초 조사가 성공적으로 저장되었습니다!")
        
        # 저장된 필드 요약
        with st.expander("📊 저장된 데이터 항목"):
            saved_fields = [k for k in survey_data.keys() 
                          if k not in ['elderly_id', 'surveyor_id', 'nursing_home_id', 'updated_at']]
            st.write(f"총 {len(saved_fields)}개 항목 저장됨")
            
            # K-MBI 점수 표시
            if 'k_mbi_score' in survey_data:
                st.metric("K-MBI 총점", f"{survey_data['k_mbi_score']}/100점")
            
            # MMSE-K 점수 표시
            if 'mmse_score' in survey_data:
                st.metric("MMSE-K 총점", f"{survey_data['mmse_score']}/30점")
        
        
        # 세션 초기화
        if 'basic_data' in st.session_state:
            del st.session_state.basic_data
        if 'basic_page' in st.session_state:
            del st.session_state.basic_page
        st.session_state.current_survey = None
        
        # 대시보드로 돌아가기 버튼
        if st.button("📊 대시보드로 돌아가기", type="primary"):
            st.rerun()
            
    except Exception as e:
        st.error(f"❌ 저장 중 오류 발생: {str(e)}")
        
        with st.expander("🔍 오류 상세 정보"):
            st.write("**저장 시도한 데이터:**")
            # 안전한 출력을 위해 변환
            display_data = {}
            for k, v in survey_data.items():
                if isinstance(v, (list, dict)):
                    display_data[k] = str(v)
                else:
                    display_data[k] = v
            st.json(display_data)
            
            st.write("**오류 메시지:**")
            st.code(str(e))


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
        if st.session_state.basic_page < 7:
            if st.button("다음 ➡️", use_container_width=True, type="primary"):
                st.session_state.basic_page += 1
                st.rerun()
