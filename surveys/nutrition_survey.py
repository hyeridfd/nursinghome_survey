import streamlit as st
import json
from datetime import datetime, timedelta

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
    
    # 페이지 진행 표시
    total_pages = 4  # 2페이지에서 4페이지로 증가
    st.progress(st.session_state.nutrition_page / total_pages)
    st.caption(f"페이지 {st.session_state.nutrition_page} / {total_pages}")
    
    # 페이지별 내용
    if st.session_state.nutrition_page == 1:
        show_page1()
    elif st.session_state.nutrition_page == 2:
        show_page2()
    elif st.session_state.nutrition_page == 3:
        show_page3()
    elif st.session_state.nutrition_page == 4:
        show_page4(supabase, elderly_id, surveyor_id, nursing_home_id)

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

def show_page2():
    """2페이지: 1인 분량 음식 질량 조사(5일)"""
    st.subheader("📏 1인 분량 음식 질량 조사 (5일)")
    
    st.info("📝 5일간의 식사별 음식 중량을 그램(g) 단위로 기록해주세요.")
    
    data = st.session_state.nutrition_data
    
    # 5일간의 날짜 생성
    if 'food_intake_start_date' not in data:
        start_date = datetime.now()
    else:
        start_date = datetime.fromisoformat(data['food_intake_start_date'])
    
    # 시작 날짜 선택
    selected_start_date = st.date_input(
        "조사 시작 날짜",
        value=start_date.date(),
        key="food_intake_start_date"
    )
    
    # 식사 유형 정의
    meal_types = {
        "조식": {
            "일반식": ["밥", "국/탕", "주찬", "부찬1", "부찬2", "김치"],
            "죽식": ["죽"],
            "간식": ["간식1", "간식2"]
        },
        "중식": {
            "일반식": ["밥", "국/탕", "주찬", "부찬1", "부찬2", "김치"],
            "죽식": ["죽"],
            "간식": ["간식1", "간식2"]
        },
        "석식": {
            "일반식": ["밥", "국/탕", "주찬", "부찬1", "부찬2", "김치"],
            "죽식": ["죽"],
            "간식": ["간식1", "간식2"]
        }
    }
    
    # 식품 섭취 데이터 초기화
    if 'food_intake_data' not in data:
        data['food_intake_data'] = {}
    
    # 5일간 데이터 입력
    for day in range(5):
        current_date = selected_start_date + timedelta(days=day)
        date_str = current_date.strftime("%Y-%m-%d")
        day_name = ["월", "화", "수", "목", "금", "토", "일"][current_date.weekday()]
        
        st.markdown(f"---")
        st.markdown(f"### 📅 {current_date.strftime('%m/%d')}({day_name})")
        
        if date_str not in data['food_intake_data']:
            data['food_intake_data'][date_str] = {}
        
        # 각 식사 시간대별 입력
        tabs = st.tabs(["🌅 조식", "☀️ 중식", "🌙 석식"])
        
        for tab_idx, (meal_name, tab) in enumerate(zip(["조식", "중식", "석식"], tabs)):
            with tab:
                if meal_name not in data['food_intake_data'][date_str]:
                    data['food_intake_data'][date_str][meal_name] = {}
                
                meal_data = data['food_intake_data'][date_str][meal_name]
                
                # 식사 유형 선택
                meal_type = st.radio(
                    "식사 유형",
                    options=["일반식", "죽식"],
                    key=f"meal_type_{date_str}_{meal_name}",
                    horizontal=True,
                    index=0 if meal_data.get('meal_type', '일반식') == '일반식' else 1
                )
                
                meal_data['meal_type'] = meal_type
                
                # 일반식 입력
                if meal_type == "일반식":
                    st.markdown("**일반식**")
                    cols = st.columns(3)
                    for idx, item in enumerate(meal_types[meal_name]["일반식"]):
                        with cols[idx % 3]:
                            value = st.number_input(
                                f"{item} (g)",
                                min_value=0,
                                max_value=2000,
                                value=int(meal_data.get(item, 0)) if meal_data.get(item) else 0,
                                step=10,
                                key=f"intake_{date_str}_{meal_name}_{item}"
                            )
                            meal_data[item] = value
                
                # 죽식 입력
                else:
                    st.markdown("**죽식**")
                    value = st.number_input(
                        "죽 (g)",
                        min_value=0,
                        max_value=2000,
                        value=int(meal_data.get('죽', 0)) if meal_data.get('죽') else 0,
                        step=10,
                        key=f"intake_{date_str}_{meal_name}_죽"
                    )
                    meal_data['죽'] = value
                
                # 간식 입력
                st.markdown("**간식**")
                cols = st.columns(2)
                for idx, item in enumerate(meal_types[meal_name]["간식"]):
                    with cols[idx]:
                        value = st.number_input(
                            f"{item} (g)",
                            min_value=0,
                            max_value=1000,
                            value=int(meal_data.get(item, 0)) if meal_data.get(item) else 0,
                            step=10,
                            key=f"intake_{date_str}_{meal_name}_{item}"
                        )
                        meal_data[item] = value
    
    # 데이터 저장
    st.session_state.nutrition_data['food_intake_start_date'] = selected_start_date.isoformat()
    st.session_state.nutrition_data['food_intake_data'] = data['food_intake_data']
    
    # 일일 총 섭취량 요약
    st.markdown("---")
    st.subheader("📊 5일간 총 섭취량 요약")
    
    summary_data = []
    for day in range(5):
        current_date = selected_start_date + timedelta(days=day)
        date_str = current_date.strftime("%Y-%m-%d")
        day_name = ["월", "화", "수", "목", "금", "토", "일"][current_date.weekday()]
        
        daily_total = 0
        if date_str in data['food_intake_data']:
            for meal_name in ["조식", "중식", "석식"]:
                if meal_name in data['food_intake_data'][date_str]:
                    meal_data = data['food_intake_data'][date_str][meal_name]
                    for key, value in meal_data.items():
                        if key != 'meal_type' and isinstance(value, (int, float)):
                            daily_total += value
        
        summary_data.append({
            "날짜": f"{current_date.strftime('%m/%d')}({day_name})",
            "총 섭취량": f"{daily_total}g"
        })
    
    cols = st.columns(5)
    for idx, day_data in enumerate(summary_data):
        with cols[idx]:
            st.metric(day_data["날짜"], day_data["총 섭취량"])
    
    navigation_buttons()

def show_page3():
    """3페이지: 잔반량 조사(5일)"""
    st.subheader("🗑️ 잔반량 조사 (5일)")
    
    st.info("📝 5일간의 식사별 잔반량을 선택해주세요.")
    
    data = st.session_state.nutrition_data
    
    # 식품 섭취 조사에서 설정한 날짜 사용
    if 'food_intake_start_date' not in data:
        start_date = datetime.now()
        st.warning("⚠️ 먼저 '1인 분량 음식 질량 조사' 페이지에서 조사 날짜를 설정해주세요.")
    else:
        start_date = datetime.fromisoformat(data['food_intake_start_date'])
    
    selected_start_date = start_date.date() if isinstance(start_date, datetime) else start_date
    
    st.info(f"📅 조사 기간: {selected_start_date.strftime('%Y년 %m월 %d일')}부터 5일간")
    
    # 잔반량 데이터 초기화
    if 'leftover_data' not in data:
        data['leftover_data'] = {}
    
    # 잔반량 옵션 정의
    leftover_options = {
        "다 먹음": {"ratio": 0.0, "color": "#2E5266"},
        "조금 남김": {"ratio": 0.25, "color": "#6E8898"},
        "반 정도 남김": {"ratio": 0.5, "color": "#9FB1BC"},
        "대부분 남김": {"ratio": 0.75, "color": "#D3D0CB"},
        "모두 남김": {"ratio": 1.0, "color": "#E2E2E2"}
    }
    
    # CSS 스타일 추가
    st.markdown("""
    <style>
    .leftover-option {
        text-align: center;
        padding: 10px;
        cursor: pointer;
        border-radius: 10px;
        transition: all 0.3s;
    }
    .leftover-option:hover {
        background-color: #f0f2f6;
        transform: scale(1.05);
    }
    .leftover-circle {
        width: 80px;
        height: 80px;
        margin: 0 auto 10px;
        position: relative;
        border-radius: 50%;
        border: 2px dashed #ccc;
    }
    .leftover-label {
        font-size: 14px;
        font-weight: bold;
        color: #333;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 5일간 데이터 입력
    for day in range(5):
        current_date = selected_start_date + timedelta(days=day)
        date_str = current_date.strftime("%Y-%m-%d")
        day_name = ["월", "화", "수", "목", "금", "토", "일"][current_date.weekday()]
        
        st.markdown(f"---")
        st.markdown(f"### 📅 {current_date.strftime('%m/%d')}({day_name})")
        
        if date_str not in data['leftover_data']:
            data['leftover_data'][date_str] = {}
        
        # 섭취량 데이터 참조
        intake_data_for_date = data.get('food_intake_data', {}).get(date_str, {})
        
        # 각 식사 시간대별 입력
        for meal_name in ["조식", "중식", "석식"]:
            if meal_name not in data['leftover_data'][date_str]:
                data['leftover_data'][date_str][meal_name] = {}
            
            leftover_meal_data = data['leftover_data'][date_str][meal_name]
            intake_meal_data = intake_data_for_date.get(meal_name, {})
            
            # 식사 아이콘
            meal_icons = {"조식": "🌅", "중식": "☀️", "석식": "🌙"}
            
            st.markdown(f"#### {meal_icons[meal_name]} {meal_name}")
            
            # 잔반량 선택 (원형 도식)
            col1, col2, col3, col4, col5 = st.columns(5)
            cols = [col1, col2, col3, col4, col5]
            
            current_selection = leftover_meal_data.get('leftover_option', '다 먹음')
            
            for idx, (option, details) in enumerate(leftover_options.items()):
                with cols[idx]:
                    # SVG로 원형 차트 생성
                    ratio = details['ratio']
                    color = details['color']
                    
                    # 원형 차트 SVG
                    if ratio == 0:
                        # 다 먹음 - 빈 원
                        svg_chart = f"""
                        <svg width="80" height="80" style="margin: 0 auto; display: block;">
                            <circle cx="40" cy="40" r="38" fill="none" stroke="#ccc" stroke-width="2" stroke-dasharray="5,5"/>
                        </svg>
                        """
                    elif ratio == 1:
                        # 모두 남김 - 꽉 찬 원
                        svg_chart = f"""
                        <svg width="80" height="80" style="margin: 0 auto; display: block;">
                            <circle cx="40" cy="40" r="38" fill="{color}" stroke="#2E5266" stroke-width="2"/>
                        </svg>
                        """
                    else:
                        # 부분적으로 채워진 원 (파이 차트)
                        angle = ratio * 360
                        large_arc = 1 if angle > 180 else 0
                        
                        # 각도를 라디안으로 변환
                        import math
                        end_angle = math.radians(angle - 90)  # -90도에서 시작 (12시 방향)
                        end_x = 40 + 38 * math.cos(end_angle)
                        end_y = 40 + 38 * math.sin(end_angle)
                        
                        svg_chart = f"""
                        <svg width="80" height="80" style="margin: 0 auto; display: block;">
                            <circle cx="40" cy="40" r="38" fill="white" stroke="#ccc" stroke-width="2" stroke-dasharray="5,5"/>
                            <path d="M 40 40 L 40 2 A 38 38 0 {large_arc} 1 {end_x} {end_y} Z" 
                                  fill="{color}" stroke="#2E5266" stroke-width="2"/>
                        </svg>
                        """
                    
                    st.markdown(svg_chart, unsafe_allow_html=True)
                    
                    # 라디오 버튼처럼 동작
                    is_selected = (current_selection == option)
                    
                    if st.button(
                        option,
                        key=f"leftover_{date_str}_{meal_name}_{option}",
                        use_container_width=True,
                        type="primary" if is_selected else "secondary"
                    ):
                        leftover_meal_data['leftover_option'] = option
                        leftover_meal_data['leftover_ratio'] = ratio
                        st.rerun()
            
            # 현재 선택 표시
            st.info(f"선택: **{current_selection}** (잔반 비율: {leftover_meal_data.get('leftover_ratio', 0)*100:.0f}%)")
            
            # 제공량 기반 실제 섭취량 계산
            total_provided = 0
            for key, value in intake_meal_data.items():
                if key != 'meal_type' and isinstance(value, (int, float)):
                    total_provided += value
            
            if total_provided > 0:
                leftover_ratio = leftover_meal_data.get('leftover_ratio', 0)
                actual_intake = total_provided * (1 - leftover_ratio)
                leftover_amount = total_provided * leftover_ratio
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("제공량", f"{total_provided:.0f}g")
                with col2:
                    st.metric("실제 섭취", f"{actual_intake:.0f}g")
                with col3:
                    st.metric("잔반량", f"{leftover_amount:.0f}g")
    
    # 데이터 저장
    st.session_state.nutrition_data['leftover_data'] = data['leftover_data']
    
    # 5일간 섭취율 요약
    st.markdown("---")
    st.subheader("📊 5일간 섭취율 요약")
    
    summary_data = []
    for day in range(5):
        current_date = selected_start_date + timedelta(days=day)
        date_str = current_date.strftime("%Y-%m-%d")
        day_name = ["월", "화", "수", "목", "금", "토", "일"][current_date.weekday()]
        
        daily_provided = 0
        daily_actual_intake = 0
        
        # 제공량 계산
        if date_str in data.get('food_intake_data', {}):
            for meal_name in ["조식", "중식", "석식"]:
                if meal_name in data['food_intake_data'][date_str]:
                    meal_data = data['food_intake_data'][date_str][meal_name]
                    for key, value in meal_data.items():
                        if key != 'meal_type' and isinstance(value, (int, float)):
                            daily_provided += value
        
        # 실제 섭취량 계산
        if date_str in data.get('leftover_data', {}):
            for meal_name in ["조식", "중식", "석식"]:
                if meal_name in data['leftover_data'][date_str]:
                    meal_data = data['leftover_data'][date_str][meal_name]
                    leftover_ratio = meal_data.get('leftover_ratio', 0)
                    
                    # 해당 식사의 제공량
                    meal_provided = 0
                    if date_str in data.get('food_intake_data', {}):
                        if meal_name in data['food_intake_data'][date_str]:
                            intake_meal = data['food_intake_data'][date_str][meal_name]
                            for key, value in intake_meal.items():
                                if key != 'meal_type' and isinstance(value, (int, float)):
                                    meal_provided += value
                    
                    daily_actual_intake += meal_provided * (1 - leftover_ratio)
        
        intake_rate = (daily_actual_intake / daily_provided * 100) if daily_provided > 0 else 0
        
        summary_data.append({
            "날짜": f"{current_date.strftime('%m/%d')}({day_name})",
            "제공량": daily_provided,
            "실제섭취": daily_actual_intake,
            "섭취율": intake_rate
        })
    
    cols = st.columns(5)
    for idx, day_data in enumerate(summary_data):
        with cols[idx]:
            # 섭취율에 따른 색상
            if day_data['섭취율'] >= 80:
                delta_color = "normal"
            elif day_data['섭취율'] >= 60:
                delta_color = "off"
            else:
                delta_color = "inverse"
            
            st.metric(
                day_data["날짜"],
                f"{day_data['섭취율']:.1f}%",
                f"{day_data['실제섭취']:.0f}g"
            )
            st.caption(f"제공: {day_data['제공량']:.0f}g")
    
    # 5일 평균 섭취율
    avg_intake_rate = sum(d['섭취율'] for d in summary_data) / len(summary_data) if summary_data else 0
    
    st.markdown("---")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("5일 평균 섭취율", f"{avg_intake_rate:.1f}%")
    
    with col2:
        if avg_intake_rate >= 80:
            st.success("✅ 양호한 섭취율입니다.")
        elif avg_intake_rate >= 60:
            st.warning("⚠️ 섭취율이 다소 낮습니다. 식사 관리가 필요합니다.")
        else:
            st.error("🚨 섭취율이 매우 낮습니다. 영양 상담이 필요합니다.")
    
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
        
        # JSON 직렬화 가능하도록 변환
        if 'food_intake_data' in data:
            data['food_intake_data'] = json.dumps(data['food_intake_data'])
        if 'leftover_data' in data:
            data['leftover_data'] = json.dumps(data['leftover_data'])
        
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
        if st.session_state.nutrition_page < 4:  # 총 4페이지
            if st.button("다음 ➡️", use_container_width=True, type="primary"):
                st.session_state.nutrition_page += 1
                st.rerun()
