import streamlit as st
import pandas as pd
import requests
import io
import re

API_KEY = "K87167491488957"

NAME_MAPPING = {
    "LLH廖仲志": "廖仲志",
    "Maggie_Chen": "陳美琪",
    "Travis柏傑": "陳柏宏",
    "LiuYuTsan": "柳育燦",
    "賴泱儒_聯華": "賴泱儒",
    "賴泱儒─聯華": "賴泱儒",
    "林哲民": "林哲民",
    "陳冠中": "陳冠中",
    "佑瑄": "陳佑瑄",
    "安迪 Cohen": "柯安迪",
    "立哲": "林立哲"
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

                    # 排除標題
                    if (
                        "LINE揪團" in line
                        or "名單統計" in line
                        or "選項統計" in line
                        or "總計" in line
                    ):
                        continue

                    # 判斷人名
                    if (
                        "$" not in line
                        and "x 1" not in line.lower()
                        and "x1" not in line.lower()
                        and len(line) < 40
                    ):
                        current_name = line

                    # 判斷餐點/飲料
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

                        excel_name = NAME_MAPPING.get(
                            current_name,
                            current_name
                        )

                        price = 0

                        if i + 1 < len(lines):

                            price_text = re.sub(
                                r"[^\d]",
                                "",
                                lines[i + 1]
                            )

                            if price_text.isdigit():
                                price = int(price_text)

                        orders.append({
                            "姓名": excel_name,
                            "餐點名稱": item,
                            "數量": 1,
                            "金額": price
                        })

            except Exception as e:

                st.error(f"{file.name} 辨識失敗")
                st.write(str(e))

        if len(orders) == 0:

            st.warning("沒有解析到資料")

        else:

            df = pd.DataFrame(orders)

            person_df = (
                df.groupby("姓名")
                .agg({
                    "數量": "sum",
                    "餐點名稱": lambda x: "、".join(x),
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
            st.dataframe(person_df, use_container_width=True)

            st.subheader("餐點統計")
            st.dataframe(item_df, use_container_width=True)

            total_amount = df["金額"].sum()

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
