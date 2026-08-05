import streamlit as st
import pandas as pd
import requests
import io
import re

API_KEY = "K87167491488957"

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

            st.subheader(file.name)

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

                for line in lines:

                    line = line.strip()

                    if not line:
                        continue

                    # 姓名判斷
                    if (
                        "x1" not in line
                        and "$" not in line
                        and not re.match(r"^\\d+$", line)
                        and "總計" not in line
                    ):

                        if len(line) < 30:
                            current_name = line

                    # 餐點判斷
                    if "x1" in line:

                        item = (
                            line.replace("x1", "")
                            .replace("X1", "")
                            .strip()
                        )

                        orders.append(
                            {
                                "姓名": current_name,
                                "數量": 1,
                                "餐點名稱": item
                            }
                        )

            except Exception as e:

                st.error(f"{file.name} 辨識失敗")
                st.write(result)
                st.write(str(e))

        if len(orders) > 0:

            df = pd.DataFrame(orders)

            st.subheader("訂單明細")

            st.dataframe(
                df,
                use_container_width=True
            )

            summary = (
                df.groupby("餐點名稱")["數量"]
                .sum()
                .reset_index()
            )

            st.subheader("餐點統計")

            st.dataframe(
                summary,
                use_container_width=True
            )

            output = io.BytesIO()

            with pd.ExcelWriter(
                output,
                engine="openpyxl"
            ) as writer:

                df.to_excel(
                    writer,
                    sheet_name="訂單明細",
                    index=False
                )

                summary.to_excel(
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

        else:

            st.warning("沒有解析到訂單資料")
