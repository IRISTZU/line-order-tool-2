import streamlit as st
import easyocr
import pandas as pd
import numpy as np
from PIL import Image

st.set_page_config(page_title="LINE訂餐整理工具")

st.title("LINE訂餐整理工具 OCR版")

uploaded_files = st.file_uploader(
    "上傳 LINE 截圖",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

if uploaded_files:

    st.success(f"已上傳 {len(uploaded_files)} 張圖片")

    if st.button("開始辨識"):

        with st.spinner("OCR辨識中，請稍候..."):

            reader = easyocr.Reader(
                ['ch_tra', 'en'],
                gpu=False
            )

            all_results = []

            for file in uploaded_files:

                image = Image.open(file)

                results = reader.readtext(
                    np.array(image),
                    detail=0
                )

                st.subheader(file.name)

                for text in results:
                    st.write(text)

                all_results.extend(results)

            st.divider()

            st.subheader("全部辨識結果")

            df = pd.DataFrame(
                all_results,
                columns=["辨識文字"]
            )

            st.dataframe(df)

            csv = df.to_csv(
                index=False,
                encoding="utf-8-sig"
            )

            st.download_button(
                "下載辨識結果 CSV",
                csv,
                file_name="ocr_result.csv",
                mime="text/csv"
            )
