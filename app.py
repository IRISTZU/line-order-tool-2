import streamlit as st

st.title("LINE訂餐整理工具")

uploaded_files = st.file_uploader(
    "上傳 LINE 截圖",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

if uploaded_files:

    st.success(
        f"已上傳 {len(uploaded_files)} 張圖片"
    )

    st.subheader("檔案列表")

    for file in uploaded_files:
        st.write(file.name)
