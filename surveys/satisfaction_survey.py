import streamlit as st
import json
from datetime import datetime

def show_satisfaction_survey(supabase, elderly_id, surveyor_id, nursing_home_id):
    st.title("😊 3. 만족도 및 선호도 조사표")
    
    # 진행 상태 초기화
    if 'satisfaction_page' not in st.session_state:
        st.session_state.satisfaction_page = 1
    
    # 기존 데이터 불러오기
    if 'satisfaction_data' not in st.session_state:
        try:
            response = supabase.table('satisfaction_survey').select('*').eq('elderly_id', elderly_id).execute()
            if response.data:
                st.session_state.satisfaction_data = response.data[0]
            else:
                st.session_state.satisfaction_data = {}
        except:
            st.session_state.satisfaction_data = {}
    
    # 페이지 진행 표시
    total_pages = 4
    st.progress(st.session_state.satisfaction_page / total_pages)
    st.caption(f"페이지 {st.session_state.satisfaction_page} / {total_pages}")
    
    # 페이지별 내용
    if st.session_state.satisfaction_page == 1:
        show_page1()
    elif st.session_state.satisfaction_page == 2:
        show_page2()
    elif st.session_state.satisfaction_page == 3:
        show_page3()
    elif st.session_state.satisfaction_page == 4:
        show_page4(supabase, elderly_id, surveyor_id, nursing_home_id)

def show_page1():
    """1페이지: 급식 만족도"""
    st.subheader("급식 만족도")
    
    data = st.session_state.satisfaction_data
    
    st.info("📝 현재 제공받는 급식에 대한 만족도를 평가해주세요.")
    
    st.markdown("### 1. 전반적인 급식 만족도")
    overall_satisfaction = st.radio(
        "급식에 대해 전반적으로 얼마나 만족하십니까?",
        options=[
            "1 = 매우 불만족",
            "2 = 불만족",
            "3 = 보통",
            "4 = 만족",
            "5 = 매우 만족"
        ],
        index=int(data.get('overall_satisfaction', 3)) - 1 if data.get('overall_satisfaction') else 2,
        key="overall_satisfaction",
        horizontal=True
    )
    
    st.markdown("### 2. 급식 양의 적절성")
    portion_adequacy = st.radio(
        "제공되는 급식의 양은 적절합니까?",
        options=[
            "1 = 매우 부족",
            "2 = 부족",
            "3 = 적당",
            "4 = 많음",
            "5 = 매우 많음"
        ],
        index=int(data.get('portion_adequacy', 3)) - 1 if data.get('portion_adequacy') else 2,
        key="portion_adequacy",
        horizontal=True
    )
    
    st.markdown("### 3. 급식 품질 만족도")
    food_quality = st.radio(
        "급식의 맛과 품질에 만족하십니까?",
        options=[
            "1 = 매우 불만족",
            "2 = 불만족",
            "3 = 보통",
            "4 = 만족",
            "5 = 매우 만족"
        ],
        index=int(data.get('food_quality', 3)) - 1 if data.get('food_quality') else 2,
        key="food_quality",
        horizontal=True
    )
    
    # 데이터 저장
    st.session_state.satisfaction_data.update({
        'overall_satisfaction': int(overall_satisfaction.split('=')[0].strip()),
        'portion_adequacy': int(portion_adequacy.split('=')[0].strip()),
        'food_quality': int(food_quality.split('=')[0].strip())
    })
    
    navigation_buttons()

def show_page2():
    """2페이지: 식품 선호도"""
    st.subheader("식품 선호도")
    
    data = st.session_state.satisfaction_data
    
    st.markdown("### 1. 선호하는 식품군 (복수 선택 가능)")
    
    food_groups = [
        "곡류 (밥, 빵, 국수 등)",
        "육류 (소고기, 돼지고기, 닭고기 등)",
        "생선류 (고등어, 갈치, 연어 등)",
        "해산물 (오징어, 새우, 조개 등)",
        "계란 및 유제품",
        "두부 및 콩류",
        "채소류",
        "과일류",
        "견과류",
        "유제품 (우유, 요거트, 치즈 등)"
    ]
    
    existing_food_groups = data.get('preferred_food_groups', [])
    if isinstance(existing_food_groups, str):
        existing_food_groups = json.loads(existing_food_groups) if existing_food_groups else []
    
    selected_food_groups = []
    col1, col2 = st.columns(2)
    
    for i, food_group in enumerate(food_groups):
        with [col1, col2][i % 2]:
            if st.checkbox(food_group, value=food_group in existing_food_groups, key=f"food_group_{i}"):
                selected_food_groups.append(food_group)
    
    st.markdown("---")
    st.markdown("### 2. 선호하는 조리 방법 (복수 선택 가능)")
    
    cooking_methods = [
        "찌기",
        "삶기",
        "굽기",
        "볶기",
        "튀기기",
        "조림",
        "무침",
        "국/탕/찌개",
        "생식 (회, 샐러드 등)"
    ]
    
    existing_cooking = data.get('preferred_cooking_methods', [])
    if isinstance(existing_cooking, str):
        existing_cooking = json.loads(existing_cooking) if existing_cooking else []
    
    selected_cooking = []
    col1, col2 = st.columns(2)
    
    for i, method in enumerate(cooking_methods):
        with [col1, col2][i % 2]:
            if st.checkbox(method, value=method in existing_cooking, key=f"cooking_{i}"):
                selected_cooking.append(method)
    
    st.markdown("---")
    st.markdown("### 3. 급식 개선 사항")
    
    improvement_suggestions = st.text_area(
        "급식에서 개선되었으면 하는 점이 있다면 자유롭게 작성해주세요.",
        value=data.get('improvement_suggestions', ''),
        height=150,
        key="improvement_suggestions"
    )
    
    # 데이터 저장
    st.session_state.satisfaction_data.update({
        'preferred_food_groups': json.dumps(selected_food_groups, ensure_ascii=False),
        'preferred_cooking_methods': json.dumps(selected_cooking, ensure_ascii=False),
        'improvement_suggestions': improvement_suggestions
    })
    
    navigation_buttons()

def show_page3():
    """3페이지: 고령친화우수식품 평가"""
    st.subheader("고령친화우수식품 평가")
    
    st.info("📝 다음 4가지 제품을 시식하고 평가해주세요. (1점: 매우 불만족 ~ 5점: 매우 만족)")
    
    data = st.session_state.satisfaction_data
    
    products = [
        {
            'name': '고운오징어젓',
            'prefix': 'product_1'
        },
        {
            'name': '화덕에 미치다 500도 고등어구이',
            'prefix': 'product_2'
        },
        {
            'name': '오쉐프 간편 고등어구이',
            'prefix': 'product_3'
        },
        {
            'name': '해물동그랑땡 행복한맛남',
            'prefix': 'product_4'
        }
    ]
    
    for i, product in enumerate(products):
        with st.expander(f"**제품 {i+1}: {product['name']}**", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                taste = st.slider(
                    "맛",
                    min_value=1,
                    max_value=5,
                    value=int(data.get(f"{product['prefix']}_taste", 3)) if data.get(f"{product['prefix']}_taste") else 3,
                    key=f"{product['prefix']}_taste"
                )
                
                chewing = st.slider(
                    "씹기 편함",
                    min_value=1,
                    max_value=5,
                    value=int(data.get(f"{product['prefix']}_chewing", 3)) if data.get(f"{product['prefix']}_chewing") else 3,
                    key=f"{product['prefix']}_chewing"
                )
                
                swallowing = st.slider(
                    "삼키기 편함",
                    min_value=1,
                    max_value=5,
                    value=int(data.get(f"{product['prefix']}_swallowing", 3)) if data.get(f"{product['prefix']}_swallowing") else 3,
                    key=f"{product['prefix']}_swallowing"
                )
            
            with col2:
                satisfaction = st.slider(
                    "전반적 만족도",
                    min_value=1,
                    max_value=5,
                    value=int(data.get(f"{product['prefix']}_satisfaction", 3)) if data.get(f"{product['prefix']}_satisfaction") else 3,
                    key=f"{product['prefix']}_satisfaction"
                )
                
                repurchase = st.slider(
                    "재구매 의향",
                    min_value=1,
                    max_value=5,
                    value=int(data.get(f"{product['prefix']}_repurchase", 3)) if data.get(f"{product['prefix']}_repurchase") else 3,
                    key=f"{product['prefix']}_repurchase"
                )
            
            # 평균 점수 표시
            avg_score = (taste + chewing + swallowing + satisfaction + repurchase) / 5
            st.metric("평균 평점", f"{avg_score:.1f}점")
            
            # 데이터 저장
            st.session_state.satisfaction_data.update({
                f"{product['prefix']}_taste": taste,
                f"{product['prefix']}_chewing": chewing,
                f"{product['prefix']}_swallowing": swallowing,
                f"{product['prefix']}_satisfaction": satisfaction,
                f"{product['prefix']}_repurchase": repurchase
            })
    
    navigation_buttons()

def show_page4(supabase, elderly_id, surveyor_id, nursing_home_id):
    """4페이지: 종합 평가 및 제출"""
    st.subheader("종합 평가")
    
    data = st.session_state.satisfaction_data
    
    st.markdown("### 1. 고령친화우수식품 전반적 만족도")
    overall_product_satisfaction = st.radio(
        "시식한 고령친화우수식품에 대해 전반적으로 얼마나 만족하십니까?",
        options=[
            "1 = 매우 불만족",
            "2 = 불만족",
            "3 = 보통",
            "4 = 만족",
            "5 = 매우 만족"
        ],
        index=int(data.get('overall_product_satisfaction', 3)) - 1 if data.get('overall_product_satisfaction') else 2,
        key="overall_product_satisfaction",
        horizontal=True
    )
    
    st.markdown("---")
    st.markdown("### 2. 선호하는 수산물 조리 형태 (복수 선택 가능)")
    
    cooking_types = [
        "구이",
        "조림",
        "찜",
        "튀김",
        "무침",
        "회",
        "국/탕/찌개",
        "볶음",
        "젓갈",
        "기타"
    ]
    
    existing_cooking_types = data.get('desired_cooking_types', [])
    if isinstance(existing_cooking_types, str):
        existing_cooking_types = json.loads(existing_cooking_types) if existing_cooking_types else []
    
    selected_cooking_types = []
    col1, col2, col3 = st.columns(3)
    
    for i, cooking_type in enumerate(cooking_types):
        with [col1, col2, col3][i % 3]:
            if st.checkbox(cooking_type, value=cooking_type in existing_cooking_types, key=f"cooking_type_{i}"):
                selected_cooking_types.append(cooking_type)
    
    st.markdown("---")
    st.markdown("### 3. 선호하는 수산물 종류 (복수 선택 가능)")
    
    seafood_types = [
        "고등어",
        "갈치",
        "삼치",
        "연어",
        "광어",
        "오징어",
        "낙지",
        "문어",
        "새우",
        "조개류",
        "멸치",
        "명란",
        "기타"
    ]
    
    existing_seafood = data.get('desired_seafood_types', [])
    if isinstance(existing_seafood, str):
        existing_seafood = json.loads(existing_seafood) if existing_seafood else []
    
    selected_seafood = []
    col1, col2, col3 = st.columns(3)
    
    for i, seafood in enumerate(seafood_types):
        with [col1, col2, col3][i % 3]:
            if st.checkbox(seafood, value=seafood in existing_seafood, key=f"seafood_{i}"):
                selected_seafood.append(seafood)
    
    # 데이터 저장
    st.session_state.satisfaction_data.update({
        'overall_product_satisfaction': int(overall_product_satisfaction.split('=')[0].strip()),
        'desired_cooking_types': json.dumps(selected_cooking_types, ensure_ascii=False),
        'desired_seafood_types': json.dumps(selected_seafood, ensure_ascii=False)
    })
    
    st.markdown("---")
    
    # 응답 요약
    st.subheader("📊 응답 요약")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**급식 만족도**")
        st.metric("전반적 만족도", f"{data.get('overall_satisfaction', 0)}점")
        st.metric("양 적절성", f"{data.get('portion_adequacy', 0)}점")
        st.metric("품질 만족도", f"{data.get('food_quality', 0)}점")
    
    with col2:
        st.write("**제품 평가**")
        
        # 각 제품의 평균 점수 계산
        for i in range(1, 5):
            prefix = f"product_{i}"
            scores = [
                data.get(f"{prefix}_taste", 0),
                data.get(f"{prefix}_chewing", 0),
                data.get(f"{prefix}_swallowing", 0),
                data.get(f"{prefix}_satisfaction", 0),
                data.get(f"{prefix}_repurchase", 0)
            ]
            avg = sum(scores) / len(scores) if scores else 0
            st.metric(f"제품 {i}", f"{avg:.1f}점")
    
    st.markdown("---")
    
    # 제출 버튼
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("⬅️ 이전", use_container_width=True):
            st.session_state.satisfaction_page -= 1
            st.rerun()
    
    with col2:
        if st.button("🏠 대시보드", use_container_width=True):
            # 세션 초기화
            if 'satisfaction_data' in st.session_state:
                del st.session_state.satisfaction_data
            if 'satisfaction_page' in st.session_state:
                del st.session_state.satisfaction_page
            st.session_state.current_survey = None
            st.rerun()
    
    with col3:
        if st.button("✅ 제출", use_container_width=True, type="primary"):
            save_satisfaction_survey(supabase, elderly_id, surveyor_id, nursing_home_id)

def save_satisfaction_survey(supabase, elderly_id, surveyor_id, nursing_home_id):
    """설문 데이터 저장"""
    try:
        data = st.session_state.satisfaction_data.copy()
        data.update({
            'elderly_id': elderly_id,
            'surveyor_id': surveyor_id,
            'nursing_home_id': nursing_home_id,
            'updated_at': datetime.now().isoformat()
        })
        
        # 기존 데이터 확인
        response = supabase.table('satisfaction_survey').select('id').eq('elderly_id', elderly_id).execute()
        
        if response.data:
            # 업데이트
            supabase.table('satisfaction_survey').update(data).eq('elderly_id', elderly_id).execute()
        else:
            # 새로 추가
            supabase.table('satisfaction_survey').insert(data).execute()
        
        # 진행 상황 업데이트
        progress_update = {
            'satisfaction_survey_completed': True,
            'last_updated': datetime.now().isoformat()
        }
        
        # 모든 설문 완료 여부 확인
        progress_response = supabase.table('survey_progress').select('*').eq('elderly_id', elderly_id).execute()
        if progress_response.data:
            progress = progress_response.data[0]
            if progress.get('basic_survey_completed') and progress.get('nutrition_survey_completed'):
                progress_update['all_surveys_completed'] = True
        
        supabase.table('survey_progress').update(progress_update).eq('elderly_id', elderly_id).execute()
        
        st.success("✅ 만족도 및 선호도 조사표가 저장되었습니다!")
        
        if progress_update.get('all_surveys_completed'):
            st.success("🎉 모든 설문이 완료되었습니다! 수고하셨습니다!")
        
        # 세션 초기화
        del st.session_state.satisfaction_data
        del st.session_state.satisfaction_page
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
        if st.session_state.satisfaction_page > 1:
            if st.button("⬅️ 이전", use_container_width=True):
                st.session_state.satisfaction_page -= 1
                st.rerun()
    
    with col2:
        if st.button("🏠 대시보드", use_container_width=True):
            # 세션 초기화
            if 'satisfaction_data' in st.session_state:
                del st.session_state.satisfaction_data
            if 'satisfaction_page' in st.session_state:
                del st.session_state.satisfaction_page
            st.session_state.current_survey = None
            st.rerun()
    
    with col3:
        if st.session_state.satisfaction_page < 4:
            if st.button("다음 ➡️", use_container_width=True, type="primary"):
                st.session_state.satisfaction_page += 1
                st.rerun()
