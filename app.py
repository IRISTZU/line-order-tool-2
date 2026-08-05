import streamlit as st
import pandas as pd
import requests
import io
import re

# OCR.Space API Key
API_KEY = "你的APIKEY"

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

            try:

                text = result["ParsedResults"][0]["ParsedText"]

                lines = text.splitlines()

                current_name = ""

                for i, line in enumerate(lines):

                    line = line.strip()

                    if not line:
                        continue

                    # 判斷姓名
                    if (
                        "x1" not in line
                        and "X1" not in line
                        and "$" not in line
                        and "總計" not in line
                        and len(line) < 30
                    ):

                        if not re.search(
                            r"^\d+$",
                            line
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

                        orders.append(
                            {
                                "姓名": current_name,
                                "數量": 1,
                                "餐點名稱": item,
                                "金額": price
                            }
                        )

            except Exception as e:

                st.error(
                    f"{file.name} 辨識失敗"
                )
                st.write(str(e))

        if len(orders) == 0:

            st.warning("沒有解析到訂單資料")

        else:

            detail_df = pd.DataFrame(orders)

            st.subheader("訂單明細")

            st.dataframe(
                detail_df,
                use_container_width=True
            )

            # 同一人合併
            person_df = (
                detail_df.groupby("姓名")
                .agg({
                    "數量": "sum",
                    "餐點名稱": lambda x: "、".join(x),
                    "金額": "sum"
                })
                .reset_index()
            )

            st.subheader("人員訂單彙總")

            st.dataframe(
                person_df,
                use_container_width=True
            )

            # 餐點統計
            item_df = (
                detail_df.groupby("餐點名稱")
                .agg({
                    "數量": "sum",
                    "金額": "sum"
                })
                .reset_index()
            )

            st.subheader("餐點統計")

            st.dataframe(
                item_df,
                use_container_width=True
            )

            total_amount = (
                person_df["金額"]
                .sum()
            )

            st.metric(
                "訂單總金額",
                f"${total_amount:,}"
            )

            # Excel
            output = io.BytesIO()

            with pd.ExcelWriter(
                output,
                engine="openpyxl"
            ) as writer:

                detail_df.to_excel(
                    writer,
                    sheet_name="訂單明細",
                    index=False
                )

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
