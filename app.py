import streamlit as st
import pandas as pd
import requests
import io
import re

# OCR.Space API Key
API_KEY = "K87167491488957"

# 指定抓取的人員
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

# LINE名稱轉正式姓名
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

                if "ParsedResults" not in result:
                    st.error(f"{file.name} OCR失敗")
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

                    # 判斷姓名
                    if (
                        "x1" not in line.lower()
                        and "$" not in line
                        and len(line) < 40
                        and not re.match(r"^\d+$", line)
                    ):
                        current_name = line

                    # 判斷餐點
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

                        if current_name.strip() in TARGET_USERS:

                            excel_name = NAME_MAPPING.get(
                                current_name.strip(),
                                current_name.strip()
                            )

                            orders.append({
                                "姓名": excel_name,
                                "數量": 1,
                                "餐點名稱": item,
                                "金額": price
                            })

            except Exception as e:

                st.error(f"{file.name} 辨識失敗")
                st.write(str(e))

        if len(orders) == 0:

            st.warning("沒有找到符合條件的人員")

        else:

            detail_df = pd.DataFrame(orders)

            # 人員訂單彙總
            person_df = (
                detail_df
                .groupby("姓名")
                .agg({
                    "數量": "sum",
                    "餐點名稱": lambda x: "、".join(x),
                    "金額": "sum"
                })
                .reset_index()
            )

            # 餐點統計
            item_df = (
                detail_df
                .groupby("餐點名稱")
                .agg({
                    "數量": "sum",
                    "金額": "sum"
                })
                .reset_index()
            )

            st.subheader("人員訂單彙總")
            st.dataframe(person_df, use_container_width=True)

            st.subheader("餐點統計")
            st.dataframe(item_df, use_container_width=True)

            total_amount = detail_df["金額"].sum()

            st.metric(
                "訂單總金額",
                f"${total_amount:,}"
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
