import streamlit as st
import pandas as pd
import requests
import io
import re

API_KEY = "K87167491488957"

# LINE名稱轉正式姓名
NAME_MAPPING = {
    "賴泱儒_聯華": "賴泱儒",
    "Brian Hsiao 蕭有玉": "蕭有玉",
    "Brian Hsiao": "蕭有玉",
    "蕭有玉": "蕭有玉",
    "LiuYuTsan": "柳育燦",
    "柳育燦": "柳育燦",
    "LLH廖仲志": "廖仲志",
    "廖仲志": "廖仲志",
    "ruihua(瑞鏵)_聯華": "黃瑞鏵",
    "黃瑞鏵": "黃瑞鏵",
    "Cenwei": "嚴岑葳",
    "嚴岑葳": "嚴岑葳",
    "dowayhome": "杜韋弘",
    "杜韋弘": "杜韋弘",
    "林哲民": "林哲民",
    "陳冠中": "陳冠中",
    "佑瑄": "陳佑瑄",
    "陳佑瑄": "陳佑瑄",
    "安迪 Cohen": "柯安迪",
    "柯安迪": "柯安迪",
    "柏宏_聯華": "陳柏宏",
    "陳柏宏": "陳柏宏",
    "立哲": "林立哲",
    "林立哲": "林立哲",
    "第三方工安_周冠旻": "周冠旻",
    "周冠旻": "周冠旻",
    "第三方工安_诺倢": "蕭渃倢",
    "蕭渃倢": "蕭渃倢",
    "第三方工安_盈君": "林盈君",
    "林盈君": "林盈君",
    "第三方工安_魏久棣": "魏久棣",
    "魏久棣": "魏久棣",
    "聯亞-林倉志": "林倉志",
    "林倉志": "林倉志"
}

# 最終要保留的人員
TARGET_NAMES = {
    "賴泱儒",
    "蕭有玉",
    "柳育燦",
    "廖仲志",
    "黃瑞鏵",
    "嚴岑葳",
    "杜韋弘",
    "林哲民",
    "陳冠中",
    "陳佑瑄",
    "柯安迪",
    "陳柏宏",
    "林立哲",
    "周冠旻",
    "蕭渃倢",
    "林盈君",
    "魏久棣",
    "林倉志"
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

                if "ParsedResults" not in result:
                    continue

                text = result["ParsedResults"][0]["ParsedText"]

                lines = text.splitlines()

                current_name = ""

                for i, line in enumerate(lines):

                    line = line.strip()

                    if not line:
                        continue

                    if "總計" in line:
                        continue

                    if (
                        "x1" not in line.lower()
                        and "$" not in line
                        and len(line) < 40
                        and not re.match(r"^\d+$", line)
                    ):
                        current_name = line

                    if "x1" in line.lower():

                        item = re.sub(
                            r"[xX]1",
                            "",
                            line
                        ).strip()

                        price = 0

                        if i + 1 < len(lines):

                            next_line = (
                                lines[i + 1]
                                .replace("$", "")
                                .replace(",", "")
                                .strip()
                            )

                            if next_line.isdigit():
                                price = int(next_line)

                        excel_name = NAME_MAPPING.get(
                            current_name,
                            current_name
                        )

                        if excel_name in TARGET_NAMES:

                            orders.append({
                                "姓名": excel_name,
                                "數量": 1,
                                "餐點名稱": item,
                                "金額": price
                            })

            except Exception as e:
                st.error(f"{file.name} 辨識失敗：{e}")

        if len(orders) == 0:

            st.warning("沒有找到符合條件的人員")

        else:

            detail_df = pd.DataFrame(orders)

            person_df = (
                detail_df.groupby("姓名")
                .agg({
                    "數量": "sum",
                    "餐點名稱": lambda x: "、".join(x),
                    "金額": "sum"
                })
                .reset_index()
            )

            item_
