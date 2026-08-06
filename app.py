import streamlit as st
import pandas as pd
import requests
import io
import re

# OCR.Space API
API_KEY = "K87167491488957"

# LINE名稱 → 正式姓名
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
    "柏宏-聯華": "陳柏宏",
    "ruihua(瑞鏵)_聯華": "黃瑞鏵",
    "ruihua（瑞鏵）_聯華": "黃瑞鏵",
    "黃瑞鏵": "黃瑞鏵",
    "姿": "林姿沂",
    "林姿沂": "林姿沂",
    "第三方工安_周冠旻": "周冠旻",
    "周冠旻": "周冠旻",
    "第三方工安_諾倢": "蕭諾倢",
    "蕭諾倢": "蕭諾倢",
    "第三方工安_盈君": "林盈君",
    "林盈君": "林盈君",
    "第三方工安_魏久棣": "魏久棣",
    "魏久棣": "魏久棣",
    "賴泱儒_聯華": "賴泱儒",
    "賴泱儒─聯華": "賴泱儒",
    "賴泱儒-聯華": "賴泱儒",
    "立哲": "林立哲",
    "林立哲": "林立哲"
}

# 允許的人員
ALLOWED_NAMES = {
    "林倉志",
    "林哲民",
    "杜韋弘",
    "蕭有玉",
    "陳冠中",
    "陳佑瑄",
    "嚴岑葳",
    "廖仲志",
    "柳育燦",
    "柯安迪",
    "陳柏宏",
    "黃瑞鏵",
    "林姿沂",
    "周冠旻",
    "蕭諾倢",
    "林盈君",
    "魏久棣",
    "賴泱儒",
    "林立哲"
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

                    if (
                        "LINE揪團" in line
                        or "名單統計" in line
                        or "選項統計" in line
                        or "總計" in line
                    ):
                        continue

                    # 判斷姓名
                    if (
                        "$" not in line
                        and "x1" not in line.lower()
                        and "x 1" not in line.lower()
                        and "×1" not in line
                        and len(line) < 40
                    ):
                        current_name = line

                    # 判斷品項
                    if (
                        "x1" in line.lower()
                        or "x 1" in line.lower()
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

                        matched_name = None

                        for key, value in NAME_MAPPING.items():

                            key_clean = key.strip()

                            if (
                                current_name == key_clean
                                or key_clean in current_name
                                or current_name in key_clean
                            ):
                                matched_name = value
                                break

                        if (
                            matched_name
                            and matched_name in ALLOWED_NAMES
                        ):

                            orders.append({
                                "姓名": matched_name,
                                "餐點名稱": item,
                                "數量": 1,
                                "金額": price
                            })

            except Exception as e:
                st.error(f"{file.name} 辨識失敗：{e}")

        if not orders:

            st.warning("沒有找到符合條件的人員")

        else:

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

            item_df = (
                df.groupby("餐點名稱")
                .agg({
                    "數量": "sum"
                })
                .reset_index()
            )

            st.subheader("人員訂單彙總")
            st.dataframe(
                person_df,
                use_container_width=True
            )

            st.subheader("餐點統計")
            st.dataframe(
                item_df,
                use_container_width=True
            )

            st.metric(
                "訂單總金額",
                f"${df['金額'].sum():,}"
            )

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
                data=output,
                file_name="LINE訂餐統計.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
