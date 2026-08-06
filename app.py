import streamlit as st
import pandas as pd
import requests
import io
import re

API_KEY = "K87167491488957"

NAME_MAPPING = {
    "聯亞-林倉志": "林倉志",
    "林哲民": "林哲民",
    "dowayhome": "杜韋弘",
    "Brian Hsiao 蕭有玉": "蕭有玉",
    "Brian Hsiao": "蕭有玉",
    "陳冠中": "陳冠中",
    "佑瑄": "陳佑瑄",
    "Cenwei": "嚴岑葳",
    "LLH廖仲志": "廖仲志",
    "廖仲志": "廖仲志",
    "LiuYuTsan": "柳育燦",
    "柳育燦": "柳育燦",
    "安迪 Cohen": "柯安迪",
    "柏宏_聯華": "陳柏宏",
    "ruihua(瑞鏵)_聯華": "黃瑞鏵",
    "ruihua（瑞鏵）_聯華": "黃瑞鏵",
    "姿": "林姿沂",
    "第三方工安_周冠旻": "周冠旻",
    "第三方工安_諾倢": "蕭諾倢",
    "第三方工安_盈君": "林盈君",
    "第三方工安_魏久棣": "魏久棣",
    "賴泱儒_聯華": "賴泱儒",
    "賴泱儒─聯華": "賴泱儒",
    "立哲": "林立哲",
    "林立哲": "林立哲"
}

st.title("LINE訂餐整理工具")

uploaded_files = st.file_uploader(
    "上傳 LINE 截圖",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

if uploaded_files:

    if st.button("開始辨識"):

        orders = []

        for file in uploaded_files:

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

                # 姓名
                if (
                    "$" not in line
                    and "x 1" not in line.lower()
                    and "x1" not in line.lower()
                    and "×1" not in line
                    and len(line) < 40
                    and "LINE揪團" not in line
                    and "名單統計" not in line
                ):
                    current_name = line

                # 品項
                if (
                    "x 1" in line.lower()
                    or "x1" in line.lower()
                    or "×1" in line
                ):

                    item = re.sub(
                        r"\s*[xX×]\s*1",
                        "",
                        line
                    ).strip()

                    price = 0

                    if i + 1 < len(lines):

                        next_line = re.sub(
                            r"[^\d]",
                            "",
                            lines[i + 1]
                        )

                        if next_line.isdigit():

                            price = int(next_line)

                    excel_name = NAME_MAPPING.get(
                        current_name.strip(),
                        current_name.strip()
                    )

                    orders.append({
                        "姓名": excel_name,
                        "餐點名稱": item,
                        "數量": 1,
                        "金額": price
                    })

        if len(orders) > 0:

            df = pd.DataFrame(orders)

            person_df = (
                df.groupby("姓名")
                .agg({
                    "餐點名稱": lambda x: "、".join(x),
                    "數量": "sum",
                    "金額": "sum"
                })
                .reset_index()
            )

            st.subheader("人員訂單彙總")
            st.dataframe(person_df)

            item_df = (
                df.groupby("餐點名稱")
                .agg({
                    "數量": "sum"
                })
                .reset_index()
            )

            st.subheader("餐點統計")
            st.dataframe(item_df)

            output = io.BytesIO()

            with pd.ExcelWriter(
                output,
                engine="openpyxl"
            ) as writer:

                person_df.to_excel(
                    writer,
                    sheet_name="人員訂單彙總",
                    index=False
                )

                item_df.to_excel(
                    writer,
                    sheet_name="餐點統計",
                    index=False
                )

            output.seek(0)

            st.download_button(
                "下載Excel",
                output,
                file_name="LINE訂餐統計.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
