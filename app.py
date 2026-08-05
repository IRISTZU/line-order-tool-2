import streamlit as st
import pandas as pd
import requests
import io

# OCR.Space API Key
API_KEY = "YOUR_API_KEY"

st.set_page_config(page_title="LINE訂餐OCR")
st.title("LINE訂餐OCR")

uploaded_files = st.file_uploader(
    "上傳 LINE 截圖",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

if uploaded_files:

    st.success(f"已上傳 {len(uploaded_files)} 張圖片")

    all_text = []

    if st.button("開始辨識"):

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
                    "K87167491488957": API_KEY,
                    "language": "cht"
                }
            )

            result = response.json()

            try:

                text = result["ParsedResults"][0]["ParsedText"]

                st.text(text)

                lines = text.splitlines()

                for line in lines:

                    line = line.strip()

                    if line:
                        all_text.append({
                            "圖片": file.name,
                            "辨識文字": line
                        })

            except Exception:

                st.error(f"{file.name} 辨識失敗")

        if all_text:

            st.divider()

            st.subheader("全部辨識結果")

            df = pd.DataFrame(all_text)

            st.dataframe(
                df,
                use_container_width=True
            )

            excel_buffer = io.BytesIO()

            with pd.ExcelWriter(
                excel_buffer,
                engine="openpyxl"
            ) as writer:

                df.to_excel(
                    writer,
                    sheet_name="OCR結果",
                    index=False
                )

            excel_buffer.seek(0)

            st.download_button(
                label="下載Excel",
                data=excel_buffer,
                file_name="LINE_OCR_Result.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
