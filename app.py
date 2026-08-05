import streamlit as st
import requests

API_KEY = "K87167491488957"

st.title("LINE訂餐OCR")

files = st.file_uploader(
    "上傳圖片",
    accept_multiple_files=True
)

if files:

    if st.button("開始辨識"):

        for file in files:

            response = requests.post(
                "https://api.ocr.space/parse/image",
                files={
                    "filename": (
                        file.name,
                        file.getvalue()
                    )
                },
                data={
                    "apikey": API_KEY,
                    "language": "cht"
                }
            )

            result = response.json()

            text = result["ParsedResults"][0]["ParsedText"]

            st.subheader(file.name)

            st.text(text)
            ``

            try:
                text = result["ParsedResults"][0]["ParsedText"]

                st.subheader(file.name)
                st.text(text)

            except Exception:
                st.error(f"{file.name} 辨識失敗")
