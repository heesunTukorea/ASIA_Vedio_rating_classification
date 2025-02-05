import streamlit as st
import base64
from PIL import Image
from classification_runner_def import total_classification_run


# base64 인코딩 함수
def image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        return f"data:image/png;base64,{encoded_string}"
    except FileNotFoundError:
        st.write(f"파일을 찾을 수 없습니다: {image_path}")
        return None

# 기본 정보 표시 함수
def display_basic_info(analysis_results, cols):
    for i, col in enumerate(cols):
        with col:
            keys = ["구분", "한글제명/원재명", "신청사", "대표", "등급분류일자", "관람등급"] if i == 0 else ["등급분류번호/유해확인번호", "상영시간(분)", "감독", "감독국적", "주연", "주연국적", "계약연도", "정당한권리자", "제작년도"]
            for key in keys:
                st.write(f"**{key}:** {analysis_results.get(key, '데이터 없음')}")

# 🔹 등급 분석 실행 함수
def process_video_classification():
    input_data = st.session_state["input_data"]
    uploaded_file = st.session_state["uploaded_file"]

    if uploaded_file:
        video_path = f"./{uploaded_file.name}"  # 🔹 업로드된 파일을 저장할 경로
        with open(video_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # 🔹 `total_classification_run()`에 전달할 입력값 구성
        video_data_lists = [
            video_path,
            input_data["제목"],
            input_data["시놉시스"],  
            input_data["구분"],
            None,
            None,
            input_data["영상 언어"][:2]
        ]
        
        # 🔹 `total_classification_run()` 실행하여 분석 결과 얻기
        try:
            rating_value, final_result_rating, reason_list = total_classification_run(video_data_lists)
        except Exception as e:
            st.error(f"등급 분류 실행 중 오류 발생: {e}")
            return

        # 🔹 분석 결과 저장
        st.session_state["analysis_results"] = {
            "구분": input_data["구분"],
            "한글제명/원재명": input_data["제목"],
            "신청사": input_data["신청사"],
            "시놉시스": input_data["시놉시스"],
            "등급분류일자": "2024-02-21",
            "관람등급": rating_value,
            "내용정보": {criterion: rating_value for criterion in final_result_rating},
            "서술적 내용기술": "\n".join(reason_list)
        }

        # 🔹 결과 페이지로 이동
        st.write("등급 분류 요청이 제출되었습니다!")
        st.query_params["page"] = "result"
        st.rerun()

# 페이지 상태 관리 및 세션 상태 초기화
page = st.query_params.get("page", "")
if "input_data" not in st.session_state:
    st.session_state["input_data"] = {}
if "analysis_results" not in st.session_state:
    st.session_state["analysis_results"] = {}
if "uploaded_file" not in st.session_state:  # 🔥 오류 방지를 위해 초기화
    st.session_state["uploaded_file"] = None

# 메인 페이지
if page == "":
    st.title("비디오 등급 분류 시스템")
    try:
        image = Image.open("C:/Users/chloeseo/Downloads/서비스이미지.png")  # 실제 이미지 파일 경로로 변경
        st.image(image, use_container_width=True)
    except FileNotFoundError:
        st.write(" ")
    st.write("비디오 콘텐츠에 적절한 등급을 지정하는 시스템입니다. 아래 버튼을 클릭하여 시작하세요.")

    if st.button("등급 분류 시작"):
        st.query_params["page"] = "upload"
        st.rerun()


# 업로드 및 메타데이터 입력 페이지
elif page == "upload":
    st.title("비디오 정보 입력")
    st.write("비디오 등급 분류에 필요한 정보를 입력해주세요.")

    category = st.selectbox("구분 *", ["선택하세요", "영화", "드라마", "애니메이션", "기타"])
    title = st.text_input("제목 *")
    genre = st.selectbox("장르 *", ["선택하세요", "범죄", "액션", "드라마", "코미디", "공포", "로맨스", "SF", "판타지", "기타"])
    synopsis = st.text_input("시놉시스 *")
    applicant = st.text_input("신청사 *")
    representative = st.text_input("대표 *")
    director = st.text_input("감독 *")
    director_nationality = st.selectbox("감독 국적 *", ["선택하세요", "한국", "미국", "일본", "중국", "기타"])
    lead_actor = st.text_input("주연 배우 *")
    lead_actor_nationality = st.selectbox("주연 배우 국적 *", ["선택하세요", "한국", "미국", "일본", "중국", "기타"])
    video_language = st.selectbox("영상 언어 *", ["선택하세요", "ko", "en", "ja", "cn", "es", "fr", "it"])
    uploaded_file = st.file_uploader("비디오 업로드 *", type=["mp4", "mov", "avi"], help="MP4, MOV 또는 AVI 형식, 최대 2GB")

    if uploaded_file is not None:
        st.session_state["uploaded_file"] = uploaded_file
        st.write("파일 업로드 완료!")

    if st.button("등급 분류 요청"):
        if not all([genre, category, applicant, director_nationality, title, lead_actor_nationality, representative, video_language, director, lead_actor, uploaded_file]):
            st.error("모든 필수 항목을 입력해주세요.")
        else:
            # 입력 데이터 저장
            st.session_state["input_data"] = {
                "구분": category,
                "장르" : genre,
                "제목": title,
                "시놉시스" : synopsis,
                "신청사": applicant,
                "감독": director,
                "감독 국적": director_nationality,
                "주연 배우": lead_actor,
                "주연 배우 국적": lead_actor_nationality,
                "대표": representative,
                "영상 언어": video_language[:2],
                "업로드 파일": uploaded_file.name if uploaded_file else None
            }
            # 🔹 등급 분석 실행
            process_video_classification()

# 결과 페이지
elif page == "result":
    st.title("비디오 등급 분류 결과")

    analysis_results = st.session_state.get("analysis_results", {})

    if not analysis_results:
        st.error("분석 결과가 없습니다. 먼저 비디오 등급 분류를 수행해주세요.")
        st.stop()

    st.write(f"### 최종 등급: {analysis_results['관람등급']}")
    st.write(f"**신청사:** {analysis_results['신청사']}")
    st.write(f"**한글제명:** {analysis_results['한글제명/원재명']}")

    # 🔹 등급 기준별 결과 출력
    st.write("### 등급 기준")
    for key, value in analysis_results["내용정보"].items():
        st.write(f"**{key}:** {value}")

    # 🔹 분석 사유 출력
    st.write("### 서술적 내용 기술")
    st.write(analysis_results["서술적 내용기술"])

    # 🔹 메인 페이지로 돌아가는 버튼
    if st.button("시작 화면으로 돌아가기"):
        st.query_params["page"] = ""
        st.rerun()

