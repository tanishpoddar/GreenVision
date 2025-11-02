import streamlit as st
import rasterio
import numpy as np
import matplotlib.pyplot as plt
import io
import tempfile
import gdown
import pandas as pd
import os

# Sample Google Drive file IDs and names for years 2020-2023
sample_files = [
    {"id": "164vS6ClPCFVJ55pLy12JXLvQqfW-9agC", "name": "NDVI 2020.tif"},
    {"id": "1ILymexmwaWvi0c0ebLtak02lO9XDRcY2", "name": "NDVI 2021.tif"},
    {"id": "1487Cl3DUCve7-ftNX_ZWh4U_IGDuCqX9", "name": "NDVI 2022.tif"},
    {"id": "1mrKn8fFm20fO62pluDS_t19qQ3WtdMg1", "name": "NDVI 2023.tif"}
]

def download_file_from_gdrive(file_id):
    url = f"https://drive.google.com/uc?id={file_id}"
    try:
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".tif")
        gdown.download(url, tmp_file.name, quiet=True)
        return tmp_file.name
    except Exception as e:
        st.error(f"Failed to download sample file with ID {file_id}: {e}")
        return None

def explain_ndvi(value):
    if value < 0:
        return "Non-vegetation (water, clouds, barren land)"
    elif value < 0.2:
        return "Very sparse or stressed vegetation"
    elif value < 0.4:
        return "Low to moderate vegetation"
    elif value < 0.6:
        return "Moderately healthy crops"
    else:
        return "Healthy and dense vegetation"

def analyze_ndvi(ndvi):
    ndvi = np.where(np.isfinite(ndvi), ndvi, np.nan)
    ndvi_min = np.nanmin(ndvi)
    ndvi_max = np.nanmax(ndvi)
    ndvi_mean = np.nanmean(ndvi)
    return {
        "NDVI Min": round(ndvi_min, 3),
        "NDVI Max": round(ndvi_max, 3),
        "NDVI Mean": round(ndvi_mean, 3),
        "Min Desc": explain_ndvi(ndvi_min),
        "Max Desc": explain_ndvi(ndvi_max),
        "Mean Desc": explain_ndvi(ndvi_mean)
    }

def plot_array_to_png(arr, title, cmap=None, vmin=None, vmax=None):
    fig, ax = plt.subplots(figsize=(6,4))
    im = ax.imshow(arr, cmap=cmap, vmin=vmin, vmax=vmax)
    ax.set_title(title)
    ax.set_xlabel("Pixel X")
    ax.set_ylabel("Pixel Y")
    plt.colorbar(im, ax=ax)
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf

def create_fcc_image(src):
    try:
        band4 = src.read(4).astype(float)
        band3 = src.read(3).astype(float)
        band2 = src.read(2).astype(float)
    except Exception:
        return None

    def normalize(arr):
        arr_min, arr_max = np.nanmin(arr), np.nanmax(arr)
        return (arr - arr_min) / (arr_max - arr_min) if arr_max > arr_min else arr*0

    r = normalize(band4)
    g = normalize(band3)
    b = normalize(band2)

    fcc_img = np.dstack((r, g, b))
    fcc_img = np.clip(fcc_img, 0, 1)
    return fcc_img

def process_and_display(path, filename):
    st.markdown(f"### {filename}")
    with rasterio.open(path) as src:
        fcc_img = create_fcc_image(src)
        ndvi = src.read(1)

    if fcc_img is not None:
        input_image = fcc_img
        input_caption = "Input Image - False Color Composite (Bands 4,3,2)"
    else:
        input_image = ndvi
        input_caption = "Input Image - Band 1 Grayscale (FCC not available)"

    ndvi_stats = analyze_ndvi(ndvi)
    ndvi_png = plot_array_to_png(ndvi, "NDVI Map", cmap='RdYlGn', vmin=0, vmax=1)
    input_png = plot_array_to_png(input_image, input_caption, cmap=None if fcc_img is not None else 'gray')

    col1, col2 = st.columns(2)
    col1.image(input_png, caption=input_caption, use_container_width=True)
    col2.image(ndvi_png, caption="NDVI Map", use_container_width=True)

    info_txt = (
        f"**NDVI Min:** {ndvi_stats['NDVI Min']} ({ndvi_stats['Min Desc']})  \n"
        f"**NDVI Max:** {ndvi_stats['NDVI Max']} ({ndvi_stats['Max Desc']})  \n"
        f"**NDVI Mean:** {ndvi_stats['NDVI Mean']} ({ndvi_stats['Mean Desc']})"
    )
    st.markdown(info_txt)

    return ndvi_stats

# Title and layout
st.markdown("""
<div style="
    display: flex; 
    justify-content: center; 
    align-items: baseline; 
    font-size: 2.3em; 
    font-weight: 700;
    margin-top: 2em;
    margin-bottom: 0.5em;
">
  <span style="color: #138A18;">GreenVision</span>
  <span style="color: #fff; margin-left: 0.5em;">: NDVI Analysis & Visualization</span>
</div>
""", unsafe_allow_html=True)

import time

button_col1, button_col2 = st.columns([1, 1], gap="small")
with button_col1:
    load_samples_clicked = st.button("Load Sample Data")
with button_col2:
    info_clicked = st.button("Info")

if info_clicked:
    @st.dialog("Information on GreenVision")
    def info_dialog():
        st.write("""
        ### How to Use GreenVision
        - Click **Load Sample Data** to quickly load sample NDVI images from different years for the same location.
        - Alternatively, upload your own GeoTIFF NDVI images to analyze.
        - The app visualizes the input images (as False Color Composite if available) alongside NDVI maps.
        - NDVI statistics (Min, Max, Mean) are shown to help you interpret vegetation health.

        ### Project Motive
        This app helps you check **vegetation differences of the same place over different points in time**, enabling monitoring of vegetation health, crop growth, or environmental change.
        """)
    info_dialog()

image_names = []
ndvi_stats_list = []

def loading_spinner(text):
    with st.spinner(text):
        time.sleep(0.1)  # For UI update

if load_samples_clicked:
    loading_spinner("Downloading and processing sample files...")
    sample_paths = []
    for file in sample_files:
        path = download_file_from_gdrive(file["id"])
        if path:
            sample_paths.append((path, file["name"]))
    if sample_paths:
        for path, name in sample_paths:
            stats = process_and_display(path, name)
            image_names.append(name)
            ndvi_stats_list.append(stats)

uploaded_files = st.file_uploader("Upload GeoTIFF files", type=['tif','tiff'], accept_multiple_files=True)

if uploaded_files:
    loading_spinner("Processing uploaded files...")
    temp_dir = tempfile.gettempdir()
    for uploaded_file in uploaded_files:
        temp_path = os.path.join(temp_dir, uploaded_file.name.replace(" ", "_"))
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        stats = process_and_display(temp_path, uploaded_file.name)
        image_names.append(uploaded_file.name)
        ndvi_stats_list.append(stats)

if image_names and ndvi_stats_list:
    # Build pandas DataFrame for Excel (rows = image names, columns = NDVI features)
    rows = []
    for name, stats in zip(image_names, ndvi_stats_list):
        rows.append({
            "Image Name": name,
            "NDVI Min": stats["NDVI Min"],
            "NDVI Max": stats["NDVI Max"],
            "NDVI Mean": stats["NDVI Mean"],
        })
    df = pd.DataFrame(rows).set_index("Image Name")

    st.dataframe(df)

    # Excel Export
    towrite = io.BytesIO()
    with pd.ExcelWriter(towrite, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='NDVI Stats')
        workbook = writer.book
        worksheet = writer.sheets['NDVI Stats']
        format1 = workbook.add_format({'num_format': '0.000'})
        worksheet.set_column('B:D', 12, format1)
    towrite.seek(0)

    st.download_button(label="Download NDVI Stats Excel",
                       data=towrite,
                       file_name="NDVI_Stats_Report.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Footer
footer_html = '''
<style>
.footer {
    text-align: center;
    font-size: 0.9em;
    margin-top: 3rem;
}
.footer a {
    color: inherit;
    text-decoration: none;
    transition: color 0.3s ease;
}
.footer a:hover {
    color: #1e90ff;
}
</style>
<div class="footer">
    Made with ❤️ by
    <a href="https://github.com/tanishpoddar" target="_blank">Tanish Poddar</a>,
    <a href="https://github.com/Zahraaabidha" target="_blank">Aabidha Zahra</a>, and
    <a href="https://github.com/MPranaviReddy" target="_blank">Pranavi Reddy</a>.
</div>
'''
st.markdown(footer_html, unsafe_allow_html=True)
