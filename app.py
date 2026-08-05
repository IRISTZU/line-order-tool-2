import streamlit as st
import pandas as pd
from PIL import Image

st.title("LINE訂餐整理工具 V1.1")

uploaded_files = st.file_uploader(
    "上傳 LINE 截圖",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

if uploaded_files:

    st.success(
        f"已上傳 {len(uploaded_files)} 張圖片"
    )

    for file in uploaded_files:
        image = Image.open(file)

        st.image(
            image,
            caption=file.name,
            use_container_width=True
        )

    if st.button("開始辨識"):

        st.info("OCR功能準備中")

        data = [
            ["黃東源", "香酥排骨餐盒", 100],
            ["鄭庭宜", "滷雞腿餐盒", 115]
        ]

        df = pd.DataFrame(
            data,
            columns=["姓名", "餐點", "金額"]
        )

        st.dataframe(df)
