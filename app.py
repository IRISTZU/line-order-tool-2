import streamlit as st
import pandas as pd
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

    st.subheader("訂單資料")

    df = pd.DataFrame(
        columns=["姓名", "餐點", "數量", "金額"]
    )

    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True
    )

    if st.button("產生Excel"):

        output = io.BytesIO()

        with pd.ExcelWriter(
            output,
            engine="xlsxwriter"
        ) as writer:

            edited_df.to_excel(
                writer,
                sheet_name="訂單明細",
                index=False
            )

            summary = (
                edited_df.groupby("餐點")
                .agg({"數量": "sum"})
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
            output,
            file_name="LINE訂餐統計.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
