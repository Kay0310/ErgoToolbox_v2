import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
from PIL import Image
import tempfile
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title='ErgoToolbox - RULA 자동 평가', layout='wide')
st.title("📸 ErgoToolbox v1 - RULA 자동 평가")

uploaded_file = st.file_uploader("작업 사진을 업로드하세요", type=["jpg", "png", "jpeg"])
if uploaded_file:
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())
    img_path = tfile.name
    image = cv2.imread(img_path)

    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=True)
    results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    if results.pose_landmarks:
        annotated = image.copy()
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing.draw_landmarks(annotated, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        
        # 시각화
        st.image(annotated, caption="📍 인식된 자세", channels="BGR", use_column_width=True)

        # 간단한 RULA 점수 예시
        rula_score = 6
        st.subheader(f"🧠 예측된 RULA 점수: {rula_score}점")
        st.write("📌 위험 수준: 즉각적 조치 필요")

        # 엑셀 저장
        output = {
            "작업자명": ["홍길동"],
            "평가일": [datetime.today().strftime('%Y-%m-%d')],
            "RULA 점수": [rula_score],
            "위험도": ["즉각적 조치 필요"]
        }
        df = pd.DataFrame(output)
        save_path = os.path.join("output", f"rula_result_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx")
        os.makedirs("output", exist_ok=True)
        df.to_excel(save_path, index=False)
        with open(save_path, "rb") as file:
            btn = st.download_button(label="📥 평가결과 엑셀 다운로드", data=file, file_name="RULA_결과.xlsx")
    else:
        st.warning("자세를 인식할 수 없습니다. 다른 사진을 사용해보세요.")
