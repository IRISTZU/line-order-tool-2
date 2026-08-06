import streamlit as st
import pandas as pd
import requests
import io
import re

API_KEY = "K87167491488957"

NAME_MAPPING = {
    "賴泱儒─聯華": "賴泱儒",
    "賴泱儒_聯華": "賴泱儒",
    "LiuYuTsan": "柳育燦",
    "LLH廖仲志": "廖仲志",
    "廖仲志": "廖仲志",
    "ruihua(瑞鏵)_聯華": "黃瑞鏵",
    "Cenwei": "嚴岑葳",
    "dowayhome": "杜韋弘",
    "林哲民": "林哲民",
    "陳冠中": "陳冠中",
    "佑瑄": "陳佑瑄",
    "安迪 Cohen": "柯安迪",
    "柏宏_聯華": "陳柏宏",
    "立哲": "林立哲",
    "林立哲": "林立哲",
    "第三方工安_周冠旻": "周冠旻",
    "第三方工安_诺倢": "蕭渃倢",
    "第三方工安_盈君": "林盈君",
    "第三方工安_魏久棣": "魏久棣",
    "聯亞-林倉志": "林倉志",
    "JH.ChenTM(建宏經理PM)": "陳建宏"
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

                st.subheader(file.name)
                st.text(text)

                lines = text.splitlines()

                current_name = ""

                for line in lines:

                    line = line.strip()

                    if not line:
                        continue

                    if (
                        "LINE揪團" in line
                        or "名單統計" in line
                        or "總計" in line
                    ):
                        continue

                    # 判斷姓名
                    if (
                        "x1" not in line.lower()
                        and "(1" not in line
                        and "（1" not in line
                        and "$" not in line
                        and len(line) < 40
                    ):

                        if (
                            "丼" not in line
                            and "餐盒" not in line
                            and "便當" not in line
                            and "飲料" not in line
                            and "檸檬" not in line
                            and "紅茶" not in line
                        ):
                            current_name = line

                    # 判斷餐點
                    is_food = (
                        "x1" in line.lower()
                        or "(1" in line
                        or "（1" in line
                        or "丼" in line
                        or "餐盒" in line
                        or "便當" in line
                    )

                    if is_food:

                        item = re.sub(
                            r"[xX×]1|\(1|\（1",
                            "",
                            line
                        ).strip()

                        excel_name = NAME_MAPPING.get(
                            current_name,
                            current_name
                        )

                        orders.append(
                            {
                                "姓名": excel_name,
                                "數量": 1,
                                "餐點名稱": item,
                                "金額": 0
                            }
                        )

            except Exception as e:

                st.error(f"{file.name} 辨識失敗")
                st.write(str(e))

        if len(orders) == 0:

            st.warning("沒有解析到資料")

        else:

            detail_df = pd.DataFrame(orders)

            person_df = (
                detail_df.groupby("姓名")
                .agg({
                    "數量": "sum",
                    "餐點名稱": lambda x: "、".join(x)
                })
                .reset_index()
            )

            item_df = (
                detail_df.groupby("餐點名稱")
                .agg({
                    "數量": "sum"
                })
                .reset_index()
            )

            st.subheader("人員訂單彙總")
            st.dataframe(person_df)

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
                data=output,
                file_name="LINE訂餐統計.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
