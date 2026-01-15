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
    """5페이지: K-MBI (한국판 수정 바델 지수) 평가"""
    st.subheader("K-MBI (한국판 수정 바델 지수) 평가")
    
    st.info("📝 일상생활 수행능력을 평가합니다. 각 항목에서 해당하는 점수를 선택해주세요.")
    
    data = st.session_state.basic_data
    
    # K-MBI 평가 항목
    kmbi_items = [
        {
            "name": "개인위생",
            "options": [
                ("0점", "타인의 도움이 필요함"),
                ("1점", "스스로 가능함 (세수, 머리 빗기, 칫솔질 등)")
            ],
            "key": "kmbi_1"
        },
        {
            "name": "목욕하기",
            "options": [
                ("0점", "타인의 도움이 필요함"),
                ("1점", "스스로 가능함")
            ],
            "key": "kmbi_2"
        },
        {
            "name": "식사하기",
            "options": [
                ("0점", "타인의 도움이 필요함"),
                ("2점", "부분적 도움 필요 (음식 자르기 등)"),
                ("5점", "스스로 가능함"),
                ("8점", "정상 (적당한 시간 내 식사)"),
                ("10점", "완전 독립")
            ],
            "key": "kmbi_3"
        },
        {
            "name": "용변처리",
            "options": [
                ("0점", "타인의 도움이 필요함"),
                ("2점", "부분적 도움 필요"),
                ("5점", "스스로 가능함"),
                ("8점", "정상"),
                ("10점", "완전 독립")
            ],
            "key": "kmbi_4"
        },
        {
            "name": "계단 오르기",
            "options": [
                ("0점", "불가능"),
                ("2점", "상당한 도움 필요"),
                ("5점", "부분적 도움 필요"),
                ("8점", "스스로 가능함"),
                ("10점", "완전 독립")
            ],
            "key": "kmbi_5"
        },
        {
            "name": "옷 입기",
            "options": [
                ("0점", "타인의 도움이 필요함"),
                ("2점", "부분적 도움 필요 (50% 이상 스스로)"),
                ("5점", "스스로 가능함"),
                ("8점", "정상"),
                ("10점", "완전 독립")
            ],
            "key": "kmbi_6"
        },
        {
            "name": "대변조절",
            "options": [
                ("0점", "조절 불가능 또는 도움 필요"),
                ("2점", "가끔 실수 (주 1회 미만)"),
                ("5점", "조절 가능"),
                ("8점", "정상"),
                ("10점", "완전 독립")
            ],
            "key": "kmbi_7"
        },
        {
            "name": "소변조절",
            "options": [
                ("0점", "조절 불가능 또는 도뇨관 사용"),
                ("2점", "가끔 실수 (주 1회 미만)"),
                ("5점", "조절 가능"),
                ("8점", "정상"),
                ("10점", "완전 독립")
            ],
            "key": "kmbi_8"
        },
        {
            "name": "보행",
            "options": [
                ("0점", "불가능"),
                ("3점", "휠체어로 이동 가능"),
                ("8점", "도움 필요 (1인 부축)"),
                ("12점", "스스로 가능 (보조기구 사용)"),
                ("15점", "완전 독립")
            ],
            "key": "kmbi_9"
        },
        {
            "name": "의자/침대 이동",
            "options": [
                ("0점", "불가능 또는 전적인 도움"),
                ("1점", "상당한 도움 필요"),
                ("3점", "부분적 도움 필요"),
                ("4점", "스스로 가능함"),
                ("5점", "완전 독립")
            ],
            "key": "kmbi_10"
        },
        {
            "name": "휠체어/침대 이동",
            "options": [
                ("0점", "불가능 또는 전적인 도움"),
                ("3점", "부분적 도움 필요"),
                ("8점", "감독 필요"),
                ("12점", "스스로 가능함"),
                ("15점", "완전 독립")
            ],
            "key": "kmbi_11"
        }
    ]
    
    total_score = 0
    
    for item in kmbi_items:
        st.markdown(f"### {item['name']}")
        
        # 기존 선택 값 가져오기
        existing_value = data.get(item['key'], 0)
        
        # 라디오 버튼으로 선택
        selected = st.radio(
            "점수 선택",
            options=[opt[0] + " - " + opt[1] for opt in item['options']],
            index=0,
            key=item['key'],
            label_visibility="collapsed"
        )
        
        # 점수 추출
        score = int(selected.split("점")[0])
        total_score += score
        
        st.markdown("---")
    
    # 총점 표시
    st.markdown("### 📊 K-MBI 총점")
    st.metric("총점", f"{total_score}점 / 100점")
    
    # 해석
    if total_score >= 90:
        st.success("✅ **독립적**: 일상생활 수행능력이 우수합니다.")
    elif total_score >= 75:
        st.info("ℹ️ **경도 의존**: 약간의 도움이 필요합니다.")
    elif total_score >= 60:
        st.warning("⚠️ **중등도 의존**: 상당한 도움이 필요합니다.")
    elif total_score >= 40:
        st.warning("⚠️ **중증 의존**: 많은 도움이 필요합니다.")
    else:
        st.error("🚨 **완전 의존**: 전적인 도움이 필요합니다.")
    
    # 데이터 저장
    st.session_state.basic_data['k_mbi_score'] = total_score
    
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
                {"question": "여기는 몇 층입니까?", "score": 1}
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
            "category": "언어기능",
            "items": [
                {"question": "이것이 무엇입니까? (연필)", "score": 1},
                {"question": "이것이 무엇입니까? (시계)", "score": 1}
            ]
        },
        {
            "category": "언어기능 - 따라 말하기",
            "items": [
                {"question": "'하늘이 맑고 파랗습니다' 따라 말하세요", "score": 1}
            ]
        },
        {
            "category": "언어기능 - 3단계 명령",
            "items": [
                {"question": "종이를 받아서 / 반으로 접어 / 무릎 위에 놓으세요", "score": 3}
            ]
        },
        {
            "category": "언어기능 - 읽기",
            "items": [
                {"question": "'눈을 감으시오' 읽고 시행하세요", "score": 1}
            ]
        },
        {
            "category": "언어기능 - 쓰기",
            "items": [
                {"question": "문장을 하나 쓰세요 (주어와 동사 포함)", "score": 1}
            ]
        },
        {
            "category": "시공간 구성",
            "items": [
                {"question": "오각형 2개가 겹쳐진 그림을 따라 그리세요", "score": 1}
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
        st.balloons()
        
        # 세션 초기화
        del st.session_state.basic_data
        del st.session_state.basic_page
        st.session_state.current_survey = None
        
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
        if st.session_state.basic_page < 7:
            if st.button("다음 ➡️", use_container_width=True, type="primary"):
                st.session_state.basic_page += 1
                st.rerun()
