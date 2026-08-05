import streamlit as st
import pandas as pd
from PIL import Image
import io

st.set_page_config(page_title="LINE訂餐整理工具")

st.title("LINE訂餐整理工具")

uploaded_files = st.file_uploader(
    "上傳 LINE 截圖",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

if uploaded_files:

    st.success(f"已上傳 {len(uploaded_files)} 張圖片")

    st.subheader("圖片預覽")

    for file in uploaded_files:
        image = Image.open(file)
        st.image(image, caption=file.name)

    st.subheader("訂單資料")

    sample_data = [
        ["黃東源", "香酥排骨餐盒", 1, 100],
        ["鄭庭宜", "滷雞腿餐盒", 1, 115]
    ]

    df = pd.DataFrame(
        sample_data,
        columns=["姓名", "餐點", "數量", "金額"]
    )

    edited_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic"
    )

    if st.button("產生Excel"):

        output = io.BytesIO()

        with pd.ExcelWriter(
            output,
            engine="openpyxl"
        ) as writer:

            edited_df.to_excel(
                writer,
                sheet_name="訂單明細",
                index=False
            )

            summary = (
                edited_df.groupby("餐點")["數量"]
                .sum()
                .reset_index()
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
            mime="
