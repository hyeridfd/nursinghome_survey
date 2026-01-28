import streamlit as st
import json
from datetime import datetime

def show_nutrition_survey(supabase, elderly_id, surveyor_id, nursing_home_id):
    st.title("🥗 2. 영양 조사표")
    
    # 진행 상태 초기화
    if 'nutrition_page' not in st.session_state:
        st.session_state.nutrition_page = 1
    
    # 기존 데이터 불러오기
    if 'nutrition_data' not in st.session_state:
        try:
            response = supabase.table('nutrition_survey').select('*').eq('elderly_id', elderly_id).execute()
            if response.data:
                st.session_state.nutrition_data = response.data[0]
            else:
                st.session_state.nutrition_data = {}
        except:
            st.session_state.nutrition_data = {}
    
    # 페이지 진행 표시 (2페이지에서 4페이지로 증가)
    total_pages = 4
    st.progress(st.session_state.nutrition_page / total_pages)
    st.caption(f"페이지 {st.session_state.nutrition_page} / {total_pages}")
    
    # 페이지별 내용
    if st.session_state.nutrition_page == 1:
        show_page1()
    elif st.session_state.nutrition_page == 2:
        show_page2_meal_portions()  # 새로 추가: 5일 식사량 조사
    elif st.session_state.nutrition_page == 3:
        show_page3_plate_waste_visual()  # 목측법으로 변경
    elif st.session_state.nutrition_page == 4:
        show_page4(supabase, elderly_id, surveyor_id, nursing_home_id)  # MNA-SF 및 제출

def create_visual_guide():
    """목측법 원형 가이드 생성"""
    st.markdown("""
    <style>
    .visual-guide {
        display: flex;
        justify-content: space-around;
        align-items: center;
        padding: 20px;
        background-color: #f0f2f6;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .visual-item {
        text-align: center;
        flex: 1;
    }
    .visual-item svg {
        width: 80px;
        height: 80px;
    }
    .visual-label {
        margin-top: 10px;
        font-size: 12px;
        font-weight: bold;
    }
    </style>
    
    <div class="visual-guide">
        <div class="visual-item">
            <svg viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="45" fill="white" stroke="#333" stroke-width="2"/>
            </svg>
            <div class="visual-label">0. 다 먹음</div>
        </div>
        <div class="visual-item">
            <svg viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="45" fill="white" stroke="#333" stroke-width="2"/>
                <path d="M 50 50 L 50 5 A 45 45 0 0 1 95 50 Z" fill="#2c3e50"/>
            </svg>
            <div class="visual-label">1. 조금 남김<br/>(약 25%)</div>
        </div>
        <div class="visual-item">
            <svg viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="45" fill="white" stroke="#333" stroke-width="2"/>
                <path d="M 50 50 L 50 5 A 45 45 0 0 1 50 95 Z" fill="#2c3e50"/>
            </svg>
            <div class="visual-label">2. 반 정도 남김<br/>(약 50%)</div>
        </div>
        <div class="visual-item">
            <svg viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="45" fill="white" stroke="#333" stroke-width="2"/>
                <path d="M 50 50 L 50 5 A 45 45 0 1 1 5 50 Z" fill="#2c3e50"/>
            </svg>
            <div class="visual-label">3. 대부분 남김<br/>(약 75%)</div>
        </div>
        <div class="visual-item">
            <svg viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="45" fill="#2c3e50" stroke="#333" stroke-width="2"/>
            </svg>
            <div class="visual-label">4. 모두 남김<br/>(100%)</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_food_waste_selector(label, key, default_value=0):
    """음식별 잔반량 선택기 (원형 이미지 포함)"""
    st.markdown(f"**{label}**")
    
    # SVG 원형 이미지 정의
    circles = [
        # 0. 다 먹음
        """<svg viewBox="0 0 100 100" style="width:60px;height:60px">
            <circle cx="50" cy="50" r="45" fill="white" stroke="#333" stroke-width="2"/>
        </svg>""",
        # 1. 조금 남김 (25%) - 1/4만 칠하기
        """<svg viewBox="0 0 100 100" style="width:60px;height:60px">
            <circle cx="50" cy="50" r="45" fill="white" stroke="#333" stroke-width="2"/>
            <path d="M 50 50 L 50 5 A 45 45 0 0 1 95 50 Z" fill="#2c3e50"/>
        </svg>""",
        # 2. 반 정도 남김 (50%) - 1/2만 칠하기
        """<svg viewBox="0 0 100 100" style="width:60px;height:60px">
            <circle cx="50" cy="50" r="45" fill="white" stroke="#333" stroke-width="2"/>
            <path d="M 50 50 L 50 5 A 45 45 0 0 1 50 95 Z" fill="#2c3e50"/>
        </svg>""",
        # 3. 대부분 남김 (75%) - 3/4만 칠하기
        """<svg viewBox="0 0 100 100" style="width:60px;height:60px">
            <circle cx="50" cy="50" r="45" fill="white" stroke="#333" stroke-width="2"/>
            <path d="M 50 50 L 50 5 A 45 45 0 1 1 5 50 Z" fill="#2c3e50"/>
        </svg>""",
        # 4. 모두 남김 (100%)
        """<svg viewBox="0 0 100 100" style="width:60px;height:60px">
            <circle cx="50" cy="50" r="45" fill="#2c3e50" stroke="#333" stroke-width="2"/>
        </svg>"""
    ]
    
    labels = ["0. 다 먹음", "1. 조금 남김", "2. 반 정도 남김", "3. 대부분 남김", "4. 모두 남김"]
    
    # 5개 컬럼으로 원형 이미지 배치
    cols = st.columns(5)
    for i, (col, circle, label_text) in enumerate(zip(cols, circles, labels)):
        with col:
            st.markdown(f"""
            <div style="text-align: center; margin-bottom: 8px;">
                {circle}
                <div style="font-size: 11px; margin-top: 5px; color: #666;">{label_text}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # 라디오 버튼을 5개 컬럼으로 나누어 배치
    radio_cols = st.columns(5)
    
    # 임시로 선택 저장
    if f"{key}_selected" not in st.session_state:
        st.session_state[f"{key}_selected"] = default_value
    
    for i, col in enumerate(radio_cols):
        with col:
            button_type = "primary" if st.session_state[f"{key}_selected"] == i else "secondary"
            if st.button(f"{i}", 
                        key=f"{key}_radio_{i}", 
                        use_container_width=True,
                        type=button_type):
                st.session_state[f"{key}_selected"] = i
                st.rerun()
    
    return st.session_state[f"{key}_selected"]

def show_page1():
    """1페이지: 신체 활동 수준 조사 (IPAQ-SF)"""
    st.subheader("신체 활동 수준 조사 (IPAQ-SF)")
    
    st.info("📝 지난 7일 동안의 신체 활동에 대해 응답해주세요.")
    
    data = st.session_state.nutrition_data
    
    st.markdown("### 1. 격렬한 신체 활동")
    st.caption("예: 무거운 물건 들기, 땅 파기, 에어로빅, 빠른 자전거 타기 등")
    
    col1, col2 = st.columns(2)
    with col1:
        vigorous_days = st.number_input(
            "지난 7일 동안 격렬한 신체 활동을 10분 이상 한 날은 며칠입니까?",
            min_value=0,
            max_value=7,
            value=int(data.get('vigorous_activity_days', 0)) if data.get('vigorous_activity_days') else 0,
            key="vigorous_days"
        )
    
    with col2:
        vigorous_time = st.number_input(
            "그러한 날 중 하루에 보통 얼마나 많은 시간을 격렬한 신체 활동을 하는데 보냈습니까? (분)",
            min_value=0,
            max_value=1440,
            value=int(data.get('vigorous_activity_time', 0)) if data.get('vigorous_activity_time') else 0,
            key="vigorous_time"
        )
    
    st.markdown("---")
    st.markdown("### 2. 중간 정도의 신체 활동")
    st.caption("예: 가벼운 물건 나르기, 보통 속도의 자전거 타기, 복식 테니스 등 (걷기는 제외)")
    
    col1, col2 = st.columns(2)
    with col1:
        moderate_days = st.number_input(
            "지난 7일 동안 중간 정도의 신체 활동을 10분 이상 한 날은 며칠입니까?",
            min_value=0,
            max_value=7,
            value=int(data.get('moderate_activity_days', 0)) if data.get('moderate_activity_days') else 0,
            key="moderate_days"
        )
    
    with col2:
        moderate_time = st.number_input(
            "그러한 날 중 하루에 보통 얼마나 많은 시간을 중간 정도의 신체 활동을 하는데 보냈습니까? (분)",
            min_value=0,
            max_value=1440,
            value=int(data.get('moderate_activity_time', 0)) if data.get('moderate_activity_time') else 0,
            key="moderate_time"
        )
    
    st.markdown("---")
    st.markdown("### 3. 걷기")
    st.caption("직장에서, 집에서, 장소 간 이동, 여가 시간의 모든 걷기를 포함")
    
    col1, col2 = st.columns(2)
    with col1:
        walking_days = st.number_input(
            "지난 7일 동안 10분 이상 걸은 날은 며칠입니까?",
            min_value=0,
            max_value=7,
            value=int(data.get('walking_days', 0)) if data.get('walking_days') else 0,
            key="walking_days"
        )
    
    with col2:
        walking_time = st.number_input(
            "그러한 날 중 하루에 보통 얼마나 많은 시간을 걷는데 보냈습니까? (분)",
            min_value=0,
            max_value=1440,
            value=int(data.get('walking_time', 0)) if data.get('walking_time') else 0,
            key="walking_time"
        )
    
    st.markdown("---")
    st.markdown("### 4. 앉아서 보낸 시간")
    
    sitting_time = st.number_input(
        "지난 7일 동안 평일 하루에 앉아서 보낸 시간은 얼마나 됩니까? (분)",
        min_value=0,
        max_value=1440,
        value=int(data.get('sitting_time', 0)) if data.get('sitting_time') else 0,
        key="sitting_time",
        help="직장, 집, 학교에서 공부/독서, TV 시청, 친구 방문 등 앉아서 보낸 모든 시간 포함"
    )
    
    # 데이터 저장
    st.session_state.nutrition_data.update({
        'vigorous_activity_days': vigorous_days,
        'vigorous_activity_time': vigorous_time,
        'moderate_activity_days': moderate_days,
        'moderate_activity_time': moderate_time,
        'walking_days': walking_days,
        'walking_time': walking_time,
        'sitting_time': sitting_time
    })
    
    # 활동량 계산 및 표시
    total_vigorous = vigorous_days * vigorous_time * 8.0  # MET
    total_moderate = moderate_days * moderate_time * 4.0  # MET
    total_walking = walking_days * walking_time * 3.3  # MET
    total_met = total_vigorous + total_moderate + total_walking
    
    st.markdown("---")
    st.subheader("📊 신체 활동량 요약")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("격렬한 활동", f"{total_vigorous:.0f} MET-분/주")
    with col2:
        st.metric("중간 활동", f"{total_moderate:.0f} MET-분/주")
    with col3:
        st.metric("걷기", f"{total_walking:.0f} MET-분/주")
    with col4:
        st.metric("총 활동량", f"{total_met:.0f} MET-분/주")
    
    # 활동 수준 분류
    if total_met >= 3000 or (vigorous_days >= 3 and total_vigorous >= 1500):
        activity_level = "높음 (High)"
    elif total_met >= 600 or (vigorous_days >= 3) or (moderate_days + walking_days >= 5 and total_moderate + total_walking >= 600):
        activity_level = "중간 (Moderate)"
    else:
        activity_level = "낮음 (Low)"
    
    st.info(f"💪 신체 활동 수준: **{activity_level}**")
    
    navigation_buttons()

def show_page2_meal_portions():
    """2페이지: 1인 분량 음식 질량 조사 (5일)"""
    st.subheader("1인 분량 음식 질량 조사 (5일)")
    
    st.info("📝 5일간 제공된 음식의 질량을 측정하여 기록해주세요. (단위: g)")
    
    data = st.session_state.nutrition_data
    
    # 기존 데이터 불러오기
    existing_portions = data.get('meal_portions', {})
    if isinstance(existing_portions, str):
        existing_portions = json.loads(existing_portions) if existing_portions else {}
    
    meal_portions = {}
    
    # 5일간 조사
    for day in range(1, 6):
        st.markdown(f"### 📅 {day}일차")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**아침**")
            breakfast_rice = st.number_input(
                "밥/죽 (g)",
                min_value=0.0,
                max_value=1000.0,
                value=float(existing_portions.get(f'day{day}_breakfast_rice', 0)),
                step=1.0,
                key=f"day{day}_breakfast_rice"
            )
            breakfast_soup = st.number_input(
                "국/탕 (g)",
                min_value=0.0,
                max_value=1000.0,
                value=float(existing_portions.get(f'day{day}_breakfast_soup', 0)),
                step=1.0,
                key=f"day{day}_breakfast_soup"
            )
            breakfast_main = st.number_input(
                "주찬 (g)",
                min_value=0.0,
                max_value=1000.0,
                value=float(existing_portions.get(f'day{day}_breakfast_main', 0)),
                step=1.0,
                key=f"day{day}_breakfast_main"
            )
            breakfast_side1 = st.number_input(
                "부찬1 (g)",
                min_value=0.0,
                max_value=1000.0,
                value=float(existing_portions.get(f'day{day}_breakfast_side1', 0)),
                step=1.0,
                key=f"day{day}_breakfast_side1"
            )
            breakfast_side2 = st.number_input(
                "부찬2 (g)",
                min_value=0.0,
                max_value=1000.0,
                value=float(existing_portions.get(f'day{day}_breakfast_side2', 0)),
                step=1.0,
                key=f"day{day}_breakfast_side2"
            )
            breakfast_kimchi = st.number_input(
                "김치 (g)",
                min_value=0.0,
                max_value=1000.0,
                value=float(existing_portions.get(f'day{day}_breakfast_kimchi', 0)),
                step=1.0,
                key=f"day{day}_breakfast_kimchi"
            )
        
        with col2:
            st.write("**점심**")
            lunch_rice = st.number_input(
                "밥/죽 (g)",
                min_value=0.0,
                max_value=1000.0,
                value=float(existing_portions.get(f'day{day}_lunch_rice', 0)),
                step=1.0,
                key=f"day{day}_lunch_rice"
            )
            lunch_soup = st.number_input(
                "국/탕 (g)",
                min_value=0.0,
                max_value=1000.0,
                value=float(existing_portions.get(f'day{day}_lunch_soup', 0)),
                step=1.0,
                key=f"day{day}_lunch_soup"
            )
            lunch_main = st.number_input(
                "주찬 (g)",
                min_value=0.0,
                max_value=1000.0,
                value=float(existing_portions.get(f'day{day}_lunch_main', 0)),
                step=1.0,
                key=f"day{day}_lunch_main"
            )
            lunch_side1 = st.number_input(
                "부찬1 (g)",
                min_value=0.0,
                max_value=1000.0,
                value=float(existing_portions.get(f'day{day}_lunch_side1', 0)),
                step=1.0,
                key=f"day{day}_lunch_side1"
            )
            lunch_side2 = st.number_input(
                "부찬2 (g)",
                min_value=0.0,
                max_value=1000.0,
                value=float(existing_portions.get(f'day{day}_lunch_side2', 0)),
                step=1.0,
                key=f"day{day}_lunch_side2"
            )
            lunch_kimchi = st.number_input(
                "김치 (g)",
                min_value=0.0,
                max_value=1000.0,
                value=float(existing_portions.get(f'day{day}_lunch_kimchi', 0)),
                step=1.0,
                key=f"day{day}_lunch_kimchi"
            )
        
        with col3:
            st.write("**저녁**")
            dinner_rice = st.number_input(
                "밥/죽 (g)",
                min_value=0.0,
                max_value=1000.0,
                value=float(existing_portions.get(f'day{day}_dinner_rice', 0)),
                step=1.0,
                key=f"day{day}_dinner_rice"
            )
            dinner_soup = st.number_input(
                "국/탕 (g)",
                min_value=0.0,
                max_value=1000.0,
                value=float(existing_portions.get(f'day{day}_dinner_soup', 0)),
                step=1.0,
                key=f"day{day}_dinner_soup"
            )
            dinner_main = st.number_input(
                "주찬 (g)",
                min_value=0.0,
                max_value=1000.0,
                value=float(existing_portions.get(f'day{day}_dinner_main', 0)),
                step=1.0,
                key=f"day{day}_dinner_main"
            )
            dinner_side1 = st.number_input(
                "부찬1 (g)",
                min_value=0.0,
                max_value=1000.0,
                value=float(existing_portions.get(f'day{day}_dinner_side1', 0)),
                step=1.0,
                key=f"day{day}_dinner_side1"
            )
            dinner_side2 = st.number_input(
                "부찬2 (g)",
                min_value=0.0,
                max_value=1000.0,
                value=float(existing_portions.get(f'day{day}_dinner_side2', 0)),
                step=1.0,
                key=f"day{day}_dinner_side2"
            )
            dinner_kimchi = st.number_input(
                "김치 (g)",
                min_value=0.0,
                max_value=1000.0,
                value=float(existing_portions.get(f'day{day}_dinner_kimchi', 0)),
                step=1.0,
                key=f"day{day}_dinner_kimchi"
            )
        
        # 데이터 저장
        meal_portions.update({
            f'day{day}_breakfast_rice': breakfast_rice,
            f'day{day}_breakfast_soup': breakfast_soup,
            f'day{day}_breakfast_main': breakfast_main,
            f'day{day}_breakfast_side1': breakfast_side1,
            f'day{day}_breakfast_side2': breakfast_side2,
            f'day{day}_breakfast_kimchi': breakfast_kimchi,
            f'day{day}_lunch_rice': lunch_rice,
            f'day{day}_lunch_soup': lunch_soup,
            f'day{day}_lunch_main': lunch_main,
            f'day{day}_lunch_side1': lunch_side1,
            f'day{day}_lunch_side2': lunch_side2,
            f'day{day}_lunch_kimchi': lunch_kimchi,
            f'day{day}_dinner_rice': dinner_rice,
            f'day{day}_dinner_soup': dinner_soup,
            f'day{day}_dinner_main': dinner_main,
            f'day{day}_dinner_side1': dinner_side1,
            f'day{day}_dinner_side2': dinner_side2,
            f'day{day}_dinner_kimchi': dinner_kimchi
        })
        
        # 일일 총량 표시
        daily_total = (
            breakfast_rice + breakfast_soup + breakfast_main + breakfast_side1 + breakfast_side2 + breakfast_kimchi +
            lunch_rice + lunch_soup + lunch_main + lunch_side1 + lunch_side2 + lunch_kimchi +
            dinner_rice + dinner_soup + dinner_main + dinner_side1 + dinner_side2 + dinner_kimchi
        )
        st.metric(f"{day}일차 총 제공량", f"{daily_total:.0f}g")
        
        st.markdown("---")
    
    # 5일 총량 계산
    total_portions = sum(meal_portions.values())
    st.subheader("📊 5일간 총 제공량")
    st.metric("총계", f"{total_portions:.0f}g", 
             delta=f"1일 평균 {total_portions/5:.0f}g")
    
    # 데이터 저장
    st.session_state.nutrition_data['meal_portions'] = json.dumps(meal_portions, ensure_ascii=False)
    
    navigation_buttons()

def show_page3_plate_waste_visual():
    """3페이지: 잔반량 조사 (5일) - 목측법"""
    st.subheader("잔반량 조사 (5일) - 목측법")
    
    st.info("📝 5일간 남긴 음식의 양을 원형 이미지를 보고 선택해주세요.")
    
    # 상단에 가이드 표시
    create_visual_guide()
    
    # 목측법 비율 정의
    visual_ratios = [0.0, 0.25, 0.50, 0.75, 1.0]
    
    data = st.session_state.nutrition_data
    
    # 제공량 데이터 불러오기
    meal_portions_data = data.get('meal_portions', {})
    if isinstance(meal_portions_data, str):
        meal_portions_data = json.loads(meal_portions_data) if meal_portions_data else {}
    
    # 기존 잔반 데이터 불러오기
    existing_waste = data.get('plate_waste_visual', {})
    if isinstance(existing_waste, str):
        existing_waste = json.loads(existing_waste) if existing_waste else {}
    
    plate_waste_visual = {}
    plate_waste_grams = {}
    
    # 5일간 조사
    for day in range(1, 6):
        st.markdown(f"### 📅 {day}일차")
        
        # 아침 식사
        st.markdown("#### 🌅 아침")
        breakfast_rice_waste = create_food_waste_selector(
            "밥/죽", 
            f"day{day}_breakfast_rice_waste",
            int(existing_waste.get(f'day{day}_breakfast_rice_waste', 0))
        )
        breakfast_soup_waste = create_food_waste_selector(
            "국/탕", 
            f"day{day}_breakfast_soup_waste",
            int(existing_waste.get(f'day{day}_breakfast_soup_waste', 0))
        )
        breakfast_main_waste = create_food_waste_selector(
            "주찬", 
            f"day{day}_breakfast_main_waste",
            int(existing_waste.get(f'day{day}_breakfast_main_waste', 0))
        )
        breakfast_side1_waste = create_food_waste_selector(
            "부찬1", 
            f"day{day}_breakfast_side1_waste",
            int(existing_waste.get(f'day{day}_breakfast_side1_waste', 0))
        )
        breakfast_side2_waste = create_food_waste_selector(
            "부찬2", 
            f"day{day}_breakfast_side2_waste",
            int(existing_waste.get(f'day{day}_breakfast_side2_waste', 0))
        )
        breakfast_kimchi_waste = create_food_waste_selector(
            "김치", 
            f"day{day}_breakfast_kimchi_waste",
            int(existing_waste.get(f'day{day}_breakfast_kimchi_waste', 0))
        )
        
        st.markdown("---")
        
        # 점심 식사
        st.markdown("#### ☀️ 점심")
        lunch_rice_waste = create_food_waste_selector(
            "밥/죽", 
            f"day{day}_lunch_rice_waste",
            int(existing_waste.get(f'day{day}_lunch_rice_waste', 0))
        )
        lunch_soup_waste = create_food_waste_selector(
            "국/탕", 
            f"day{day}_lunch_soup_waste",
            int(existing_waste.get(f'day{day}_lunch_soup_waste', 0))
        )
        lunch_main_waste = create_food_waste_selector(
            "주찬", 
            f"day{day}_lunch_main_waste",
            int(existing_waste.get(f'day{day}_lunch_main_waste', 0))
        )
        lunch_side1_waste = create_food_waste_selector(
            "부찬1", 
            f"day{day}_lunch_side1_waste",
            int(existing_waste.get(f'day{day}_lunch_side1_waste', 0))
        )
        lunch_side2_waste = create_food_waste_selector(
            "부찬2", 
            f"day{day}_lunch_side2_waste",
            int(existing_waste.get(f'day{day}_lunch_side2_waste', 0))
        )
        lunch_kimchi_waste = create_food_waste_selector(
            "김치", 
            f"day{day}_lunch_kimchi_waste",
            int(existing_waste.get(f'day{day}_lunch_kimchi_waste', 0))
        )
        
        st.markdown("---")
        
        # 저녁 식사
        st.markdown("#### 🌙 저녁")
        dinner_rice_waste = create_food_waste_selector(
            "밥/죽", 
            f"day{day}_dinner_rice_waste",
            int(existing_waste.get(f'day{day}_dinner_rice_waste', 0))
        )
        dinner_soup_waste = create_food_waste_selector(
            "국/탕", 
            f"day{day}_dinner_soup_waste",
            int(existing_waste.get(f'day{day}_dinner_soup_waste', 0))
        )
        dinner_main_waste = create_food_waste_selector(
            "주찬", 
            f"day{day}_dinner_main_waste",
            int(existing_waste.get(f'day{day}_dinner_main_waste', 0))
        )
        dinner_side1_waste = create_food_waste_selector(
            "부찬1", 
            f"day{day}_dinner_side1_waste",
            int(existing_waste.get(f'day{day}_dinner_side1_waste', 0))
        )
        dinner_side2_waste = create_food_waste_selector(
            "부찬2", 
            f"day{day}_dinner_side2_waste",
            int(existing_waste.get(f'day{day}_dinner_side2_waste', 0))
        )
        dinner_kimchi_waste = create_food_waste_selector(
            "김치", 
            f"day{day}_dinner_kimchi_waste",
            int(existing_waste.get(f'day{day}_dinner_kimchi_waste', 0))
        )
        
        # 목측 레벨 저장 (0-4)
        plate_waste_visual.update({
            f'day{day}_breakfast_rice_waste': breakfast_rice_waste,
            f'day{day}_breakfast_soup_waste': breakfast_soup_waste,
            f'day{day}_breakfast_main_waste': breakfast_main_waste,
            f'day{day}_breakfast_side1_waste': breakfast_side1_waste,
            f'day{day}_breakfast_side2_waste': breakfast_side2_waste,
            f'day{day}_breakfast_kimchi_waste': breakfast_kimchi_waste,
            f'day{day}_lunch_rice_waste': lunch_rice_waste,
            f'day{day}_lunch_soup_waste': lunch_soup_waste,
            f'day{day}_lunch_main_waste': lunch_main_waste,
            f'day{day}_lunch_side1_waste': lunch_side1_waste,
            f'day{day}_lunch_side2_waste': lunch_side2_waste,
            f'day{day}_lunch_kimchi_waste': lunch_kimchi_waste,
            f'day{day}_dinner_rice_waste': dinner_rice_waste,
            f'day{day}_dinner_soup_waste': dinner_soup_waste,
            f'day{day}_dinner_main_waste': dinner_main_waste,
            f'day{day}_dinner_side1_waste': dinner_side1_waste,
            f'day{day}_dinner_side2_waste': dinner_side2_waste,
            f'day{day}_dinner_kimchi_waste': dinner_kimchi_waste
        })
        
        # 그램 단위로 변환 (제공량 × 잔반 비율)
        waste_items = {
            'breakfast_rice': (breakfast_rice_waste, f'day{day}_breakfast_rice'),
            'breakfast_soup': (breakfast_soup_waste, f'day{day}_breakfast_soup'),
            'breakfast_main': (breakfast_main_waste, f'day{day}_breakfast_main'),
            'breakfast_side1': (breakfast_side1_waste, f'day{day}_breakfast_side1'),
            'breakfast_side2': (breakfast_side2_waste, f'day{day}_breakfast_side2'),
            'breakfast_kimchi': (breakfast_kimchi_waste, f'day{day}_breakfast_kimchi'),
            'lunch_rice': (lunch_rice_waste, f'day{day}_lunch_rice'),
            'lunch_soup': (lunch_soup_waste, f'day{day}_lunch_soup'),
            'lunch_main': (lunch_main_waste, f'day{day}_lunch_main'),
            'lunch_side1': (lunch_side1_waste, f'day{day}_lunch_side1'),
            'lunch_side2': (lunch_side2_waste, f'day{day}_lunch_side2'),
            'lunch_kimchi': (lunch_kimchi_waste, f'day{day}_lunch_kimchi'),
            'dinner_rice': (dinner_rice_waste, f'day{day}_dinner_rice'),
            'dinner_soup': (dinner_soup_waste, f'day{day}_dinner_soup'),
            'dinner_main': (dinner_main_waste, f'day{day}_dinner_main'),
            'dinner_side1': (dinner_side1_waste, f'day{day}_dinner_side1'),
            'dinner_side2': (dinner_side2_waste, f'day{day}_dinner_side2'),
            'dinner_kimchi': (dinner_kimchi_waste, f'day{day}_dinner_kimchi')
        }
        
        daily_waste_g = 0
        for item_name, (waste_level, portion_key) in waste_items.items():
            portion_amount = meal_portions_data.get(portion_key, 0)
            waste_ratio = visual_ratios[waste_level]
            waste_g = portion_amount * waste_ratio
            plate_waste_grams[f'day{day}_{item_name}_waste'] = waste_g
            daily_waste_g += waste_g
        
        # 일일 총 잔반량 표시
        st.metric(f"{day}일차 총 잔반량", f"{daily_waste_g:.0f}g")
        
        st.markdown("---")
    
    # 5일 총 잔반량 계산
    total_waste = sum(plate_waste_grams.values())
    st.subheader("📊 5일간 총 잔반량")
    st.metric("총계", f"{total_waste:.0f}g", 
             delta=f"1일 평균 {total_waste/5:.0f}g")
    
    # 섭취율 계산 (제공량 대비)
    if meal_portions_data:
        total_portions = sum(meal_portions_data.values())
        intake_rate = ((total_portions - total_waste) / total_portions * 100) if total_portions > 0 else 0
        st.metric("평균 섭취율", f"{intake_rate:.1f}%")
    
    # 데이터 저장 (목측 레벨과 그램 단위 모두 저장)
    st.session_state.nutrition_data['plate_waste_visual'] = json.dumps(plate_waste_visual, ensure_ascii=False)
    st.session_state.nutrition_data['plate_waste'] = json.dumps(plate_waste_grams, ensure_ascii=False)
    
    navigation_buttons()

def show_page4(supabase, elderly_id, surveyor_id, nursing_home_id):
    """4페이지: 영양 상태 평가 (MNA-SF) 및 제출"""
    st.subheader("영양 상태 평가 (MNA-SF)")
    
    st.info("📝 간이 영양 평가 (Mini Nutritional Assessment - Short Form)")
    
    data = st.session_state.nutrition_data
    
    # 기초 조사표에서 BMI 가져오기
    try:
        basic_response = supabase.table('basic_survey').select('height, weight').eq('elderly_id', elderly_id).execute()
        if basic_response.data:
            height = basic_response.data[0].get('height', 0)
            weight = basic_response.data[0].get('weight', 0)
            if height and weight and height > 0:
                bmi = weight / ((height / 100) ** 2)
                st.info(f"📊 기초 조사표 기준 BMI: {bmi:.2f} kg/m²")
            else:
                bmi = None
        else:
            bmi = None
    except:
        bmi = None
    
    st.markdown("### 1. 식욕 감퇴")
    appetite_change = st.radio(
        "지난 3개월 동안 식욕부진, 소화 문제, 씹기 또는 삼키기 어려움 등으로 음식 섭취량이 감소했습니까?",
        options=[
            "0 = 심하게 감소",
            "1 = 중등도로 감소",
            "2 = 감소하지 않음"
        ],
        index=int(data.get('appetite_change', 2)),
        key="appetite_change"
    )
    
    st.markdown("### 2. 체중 감소")
    weight_change = st.radio(
        "지난 3개월 동안 체중 감소가 있었습니까?",
        options=[
            "0 = 3kg 이상 감소",
            "1 = 모르겠다",
            "2 = 1-3kg 감소",
            "3 = 체중 감소 없음"
        ],
        index=int(data.get('weight_change', 3)),
        key="weight_change"
    )
    
    st.markdown("### 3. 거동")
    mobility = st.radio(
        "거동 능력은 어떻습니까?",
        options=[
            "0 = 침대나 의자에 묶여있음",
            "1 = 침대나 의자를 벗어날 수 있으나 외출하지 못함",
            "2 = 자유롭게 돌아다님"
        ],
        index=int(data.get('mobility', 2)),
        key="mobility"
    )
    
    st.markdown("### 4. 스트레스 또는 급성 질환")
    stress_illness = st.radio(
        "지난 3개월 동안 정신적 스트레스 또는 급성 질환을 겪었습니까?",
        options=[
            "0 = 예",
            "2 = 아니오"
        ],
        index=0 if data.get('stress_illness') == 0 else 1,
        key="stress_illness"
    )
    
    st.markdown("### 5. 신경정신학적 문제")
    neuropsychological = st.radio(
        "신경정신학적 문제가 있습니까?",
        options=[
            "0 = 심한 치매 또는 우울증",
            "1 = 경도 치매",
            "2 = 정신적 문제 없음"
        ],
        index=int(data.get('neuropsychological_problem', 2)),
        key="neuropsychological"
    )
    
    st.markdown("### 6. 체질량지수 (BMI)")
    
    if bmi:
        # BMI 자동 분류
        if bmi < 19:
            bmi_category_default = 0
            bmi_text = f"0 = BMI가 19 미만 (현재: {bmi:.2f})"
        elif bmi < 21:
            bmi_category_default = 1
            bmi_text = f"1 = BMI가 19 이상 21 미만 (현재: {bmi:.2f})"
        elif bmi < 23:
            bmi_category_default = 2
            bmi_text = f"2 = BMI가 21 이상 23 미만 (현재: {bmi:.2f})"
        else:
            bmi_category_default = 3
            bmi_text = f"3 = BMI가 23 이상 (현재: {bmi:.2f})"
        
        st.info(bmi_text)
        bmi_category = bmi_category_default
    else:
        bmi_category = st.radio(
            "BMI 분류",
            options=[
                "0 = BMI가 19 미만",
                "1 = BMI가 19 이상 21 미만",
                "2 = BMI가 21 이상 23 미만",
                "3 = BMI가 23 이상"
            ],
            index=int(data.get('bmi_category', 3)),
            key="bmi_category_manual"
        )
    
    # 점수 계산
    appetite_score = int(appetite_change.split('=')[0].strip())
    weight_score = int(weight_change.split('=')[0].strip())
    mobility_score = int(mobility.split('=')[0].strip())
    stress_score = int(stress_illness.split('=')[0].strip())
    neuro_score = int(neuropsychological.split('=')[0].strip())
    bmi_score = bmi_category if isinstance(bmi_category, int) else int(bmi_category.split('=')[0].strip())
    
    total_score = appetite_score + weight_score + mobility_score + stress_score + neuro_score + bmi_score
    
    # 데이터 저장
    st.session_state.nutrition_data.update({
        'appetite_change': appetite_score,
        'weight_change': weight_score,
        'mobility': mobility_score,
        'stress_illness': stress_score,
        'neuropsychological_problem': neuro_score,
        'bmi_category': bmi_score
    })
    
    st.markdown("---")
    st.subheader("📊 MNA-SF 결과")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("총점", f"{total_score}점 / 14점")
    
    with col2:
        if total_score >= 12:
            status = "정상 영양 상태"
            color = "green"
        elif total_score >= 8:
            status = "영양불량 위험"
            color = "orange"
        else:
            status = "영양불량"
            color = "red"
        
        st.markdown(f"### :{color}[{status}]")
    
    st.info("""
    **해석 기준:**
    - 12-14점: 정상 영양 상태
    - 8-11점: 영양불량 위험
    - 0-7점: 영양불량
    """)
    
    st.markdown("---")
    
    # 제출 버튼
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("⬅️ 이전", use_container_width=True):
            st.session_state.nutrition_page -= 1
            st.rerun()
    
    with col2:
        if st.button("🏠 대시보드", use_container_width=True):
            # 세션 초기화
            if 'nutrition_data' in st.session_state:
                del st.session_state.nutrition_data
            if 'nutrition_page' in st.session_state:
                del st.session_state.nutrition_page
            st.session_state.current_survey = None
            st.rerun()
    
    with col3:
        if st.button("✅ 제출", use_container_width=True, type="primary"):
            save_nutrition_survey(supabase, elderly_id, surveyor_id, nursing_home_id)

def save_nutrition_survey(supabase, elderly_id, surveyor_id, nursing_home_id):
    """설문 데이터 저장"""
    try:
        data = st.session_state.nutrition_data.copy()
        data.update({
            'elderly_id': elderly_id,
            'surveyor_id': surveyor_id,
            'nursing_home_id': nursing_home_id,
            'updated_at': datetime.now().isoformat()
        })
        
        # 기존 데이터 확인
        response = supabase.table('nutrition_survey').select('id').eq('elderly_id', elderly_id).execute()
        
        if response.data:
            # 업데이트
            supabase.table('nutrition_survey').update(data).eq('elderly_id', elderly_id).execute()
        else:
            # 새로 추가
            supabase.table('nutrition_survey').insert(data).execute()
        
        # 진행 상황 업데이트
        supabase.table('survey_progress').update({
            'nutrition_survey_completed': True,
            'last_updated': datetime.now().isoformat()
        }).eq('elderly_id', elderly_id).execute()
        
        st.success("✅ 영양 조사표가 저장되었습니다!")
        
        # 세션 초기화
        del st.session_state.nutrition_data
        del st.session_state.nutrition_page
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
        if st.session_state.nutrition_page > 1:
            if st.button("⬅️ 이전", use_container_width=True):
                st.session_state.nutrition_page -= 1
                st.rerun()
    
    with col2:
        if st.button("🏠 대시보드", use_container_width=True):
            # 세션 초기화
            if 'nutrition_data' in st.session_state:
                del st.session_state.nutrition_data
            if 'nutrition_page' in st.session_state:
                del st.session_state.nutrition_page
            st.session_state.current_survey = None
            st.rerun()
    
    with col3:
        if st.session_state.nutrition_page < 4:
            if st.button("다음 ➡️", use_container_width=True, type="primary"):
                st.session_state.nutrition_page += 1
                st.rerun()
