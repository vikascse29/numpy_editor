import streamlit as st
import numpy as np
import pandas as pd
import io

st.set_page_config(page_title="NumPy Editor", layout="wide")
st.title("🧬 NumPy Array Editor")

uploaded_file = st.file_uploader("Upload a NumPy file (.npy or .npz)", type=["npy", "npz"])

if uploaded_file:
    file_name = uploaded_file.name
    ext = file_name.split(".")[-1]

    # Load arrays
    if ext == "npy":
        array = np.load(uploaded_file, allow_pickle=True)
        arrays = {"array": array}

    elif ext == "npz":
        npz = np.load(uploaded_file, allow_pickle=True)
        arrays = {k: npz[k] for k in npz.files}

    selected = st.selectbox("Choose an array to view/edit:", list(arrays.keys()))
    arr = arrays[selected]

    st.subheader(f"📌 Viewing: {selected}")

    # -----------------------------
    #  ARRAY METADATA
    # -----------------------------
    st.write("### 📐 Array Details")
    st.write(f"- **Shape**: `{arr.shape}`")
    st.write(f"- **Dtype**: `{arr.dtype}`")
    st.write(f"- **Size**: `{arr.size}`")
    st.write(f"- **Bytes**: `{arr.nbytes}`")

    # -----------------------------
    #  STRUCTURED ARRAY HANDLING
    # -----------------------------
    if arr.dtype.names:
        st.subheader("🗂 Structured Array Detected")

        df = pd.DataFrame(arr)

        st.write("### ✏️ Edit Structured Array")
        edited_df = st.data_editor(df, height=500)

        # Convert edited dataframe back to structured numpy array
        st.write("### 💾 Save Edited Structured Array")
        if st.button("Save .npy"):
            new_arr = np.zeros(len(edited_df), dtype=arr.dtype)
            for field in arr.dtype.names:
                new_arr[field] = edited_df[field].to_numpy()

            buffer = io.BytesIO()
            np.save(buffer, new_arr)
            st.download_button(
                label="Download Edited Array",
                data=buffer.getvalue(),
                file_name=f"{selected}_edited.npy",
                mime="application/octet-stream",
            )

    else:
        # -----------------------------
        #  UNSTRUCTURED ARRAY HANDLING
        # -----------------------------
        st.subheader("📄 Unstructured Array")

        # 1D array -> editable list
        if arr.ndim == 1:
            st.write("### ✏️ Edit 1D Array")
            edited_list = st.text_area("Comma-separated values:", ",".join(map(str, arr)))

            if edited_list.strip():
                try:
                    new_arr = np.array([float(x) for x in edited_list.split(",")])
                    st.write("Updated Array:", new_arr)
                except:
                    st.error("Invalid values. Make sure they are numbers separated by commas.")

        # 2D or higher arrays edited as DataFrame
        else:
            st.write("### ✏️ Edit 2D+ Array")

            if arr.ndim == 2:
                df = pd.DataFrame(arr)
                edited_df = st.data_editor(df, height=500)
                new_arr = edited_df.to_numpy()

            else:
                st.info("Showing first slice for editing (multidimensional array).")
                df = pd.DataFrame(arr[0])
                edited_df = st.data_editor(df, height=500)
                new_arr = arr.copy()
                new_arr[0] = edited_df.to_numpy()

        # Save button
        st.write("### 💾 Save Edited Array")
        if st.button("Save Edited .npy"):
            buffer = io.BytesIO()
            np.save(buffer, new_arr)
            st.download_button(
                label="Download File",
                data=buffer.getvalue(),
                file_name=f"{selected}_edited.npy",
                mime="application/octet-stream",
            )

else:
    st.info("Upload a .npy or .npz file to view & edit arrays.")
