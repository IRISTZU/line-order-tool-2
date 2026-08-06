import streamlit as st
import pandas as pd
import requests
import io
import re

# OCR.Space API Key
API_KEY = "K87167491488957"

# 只保留以下人員
TARGET_USERS = {
    "賴泱儒_聯華",
    "Brian Hsiao 蕭有玉",
    "LiuYuTsan",
    "LLH廖仲志",
    "ruihua(瑞鏵)_聯華",
    "Cenwei",
    "dowayhome",
    "林哲民",
    "陳冠中",
    "佑瑄",
    "安迪 Cohen",
    "柏宏_聯華",
    "立哲",
    "第三方工安_周冠旻",
    "第三方工安_诺倢",
    "第三方工安_盈君",
    "第三方工安_魏久棣",
    "聯亞-林倉志"
}

# LINE名稱 -> 正式姓名
NAME_MAPPING = {
    "賴泱儒_聯華": "賴泱儒",
    "Brian Hsiao 蕭有玉": "蕭有玉",
    "LiuYuTsan": "柳育燦",
    "LLH廖仲志": "廖仲志",
    "ruihua(瑞鏵)_聯華": "黃瑞鏵",
    "Cenwei": "嚴岑葳",
    "dowayhome": "杜韋弘",
    "林哲民": "林哲民",
    "陳冠中": "陳冠中",
    "佑瑄": "陳佑瑄",
    "安迪 Cohen": "柯安迪",
    "柏宏_聯華": "陳柏宏",
    "立哲": "林立哲",
    "第三方工安_周冠旻": "周冠旻",
    "第三方工安_诺倢": "蕭渃倢",
    "第三方工安_盈君": "林盈君",
    "第三方工安_魏久棣": "魏久棣",
    "聯亞-林倉志": "林倉志"
}

st.set_page_config(page_title="LINE訂餐整理工具")

st.title("LINE訂餐整理工具")

uploaded_files = st.file_uploader(
    "上傳 LINE 截圖",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

if uploaded_files:

    st.success(f"已上傳 {len(uploaded_files)} 張圖片")

    if st.button("開始辨識"):

        orders = []

        for file in uploaded_files:

            try:

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

                lines = text.splitlines()

                current_name = ""

                for i, line in enumerate(lines):

                    line = line.strip()

          
