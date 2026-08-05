import streamlit as st
import easyocr
from PIL import Image
import numpy as np

st.title("LINE訂餐 OCR 測試")

uploaded_file = st.file_uploader(
    "上傳圖片",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file:

    image = Image.open(uploaded_file)

    st.image(image)

    if st.button("開始 OCR"):

        reader = easyocr.Reader(
            ['ch_tra', 'en']
        )

        results = reader.readtext(
            np.array(image),
            detail=0
        )

        st.write(results)
