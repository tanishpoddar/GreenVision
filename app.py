import streamlit as st
import rasterio
import numpy as np
import matplotlib.pyplot as plt
import io
import tempfile
import gdown
import pandas as pd
import os
from openai import OpenAI
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

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
    """Fallback explanation (kept for backward compatibility)"""
    if value < 0:
        return "Non-vegetation (water, barren land etc.)"
    elif value < 0.2:
        return "Very sparse or stressed vegetation"
    elif value < 0.4:
        return "Low to moderate vegetation"
    elif value < 0.6:
        return "Moderately healthy crops"
    else:
        return "Healthy and dense vegetation"

def call_minimax_ai(prompt_messages):
    """Call MiniMax M2 AI model for temporal NDVI analysis using OpenAI client"""
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key or api_key.strip() == "":
        st.warning("⚠️ OpenRouter API key not found. Set OPENROUTER_API_KEY in .env file for AI-powered insights.")
        return None
    
    try:
        # Initialize OpenAI client with OpenRouter base URL
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        
        # Make API call
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://github.com/tanishpoddar/GreenVision",
                "X-Title": "GreenVision NDVI Analysis",
            },
            model="minimax/minimax-m2:free",
            messages=prompt_messages,
            temperature=0.3,
            max_tokens=5000,
        )
        
        # Extract and return response content
        return completion.choices[0].message.content
    
    except Exception as e:
        st.error(f"Error calling AI model: {str(e)}")
        return None

def generate_ai_temporal_analysis(image_names, ndvi_stats_list):
    """Generate AI-powered temporal analysis of NDVI data"""
    
    # Prepare temporal data summary for AI (convert numpy types to Python native types)
    temporal_data = []
    for name, stats in zip(image_names, ndvi_stats_list):
        temporal_data.append({
            "time_period": name,
            "ndvi_min": float(stats["NDVI Min"]),
            "ndvi_max": float(stats["NDVI Max"]),
            "ndvi_mean": float(stats["NDVI Mean"])
        })
    
    # Create detailed prompt for AI analysis
    import json
    prompt = f"""You are an expert remote sensing analyst specializing in vegetation monitoring using NDVI (Normalized Difference Vegetation Index).

Analyze the following temporal NDVI data from the same location over multiple time periods:

{json.dumps(temporal_data, indent=2)}

Provide a comprehensive analysis including:

1. **Overall Trend**: Describe whether vegetation health is improving, declining, or stable over time
2. **Significant Changes**: Identify any notable changes between time periods with specific numbers
3. **NDVI Value Interpretation**: Explain what the actual NDVI values mean for each time period in context:
   - NDVI < 0: Water bodies, barren land, built-up areas
   - NDVI 0-0.2: Bare soil, rock, sand, or stressed vegetation
   - NDVI 0.2-0.4: Sparse vegetation, grassland, or crops in early growth
   - NDVI 0.4-0.6: Moderate vegetation, healthy grassland, or developing crops
   - NDVI 0.6-0.8: Dense vegetation, healthy crops, or forest
   - NDVI > 0.8: Very dense, peak health vegetation
4. **Possible Causes**: What environmental, agricultural, or climate factors might explain these changes?
5. **Recommendations**: Provide actionable insights for land management based on the trends

Be specific with numbers, percentages, and timeframes. Format your response in clear sections with markdown."""

    messages = [
        {"role": "system", "content": "You are an expert in remote sensing and vegetation analysis."},
        {"role": "user", "content": prompt}
    ]
    
    return call_minimax_ai(messages)

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
    col1.image(input_png, caption=input_caption, width='stretch')
    col2.image(ndvi_png, caption="NDVI Map", width='stretch')

    info_txt = (
        f"**NDVI Min:** {ndvi_stats['NDVI Min']} ({ndvi_stats['Min Desc']})  \n"
        f"**NDVI Max:** {ndvi_stats['NDVI Max']} ({ndvi_stats['Max Desc']})  \n"
        f"**NDVI Mean:** {ndvi_stats['NDVI Mean']} ({ndvi_stats['Mean Desc']})"
    )
    st.markdown(info_txt)

    return ndvi_stats

def plot_temporal_trend(image_names, ndvi_stats_list):
    """Create a line plot showing NDVI trends over time"""
    means = [stats["NDVI Mean"] for stats in ndvi_stats_list]
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(image_names, means, marker='o', linewidth=2, markersize=8, color='#138A18')
    ax.set_xlabel("Time Period", fontsize=12, fontweight='bold')
    ax.set_ylabel("Mean NDVI", fontsize=12, fontweight='bold')
    ax.set_title("Vegetation Health Trend Over Time", fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_ylim([0, 1])
    
    # Rotate x-axis labels if needed
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    plt.close(fig)
    buf.seek(0)
    return buf

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
        - **NEW**: AI-powered temporal analysis provides insights into vegetation changes over time!

        ### Project Motive
        This app helps you check **vegetation differences of the same place over different points in time**, enabling monitoring of vegetation health, crop growth, or environmental change.
        
        ### AI Integration
        Set `OPENROUTER_API_KEY` in your `.env` file to enable AI-powered temporal analysis and interpretation.
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
    st.markdown("---")
    
    # Build pandas DataFrame for comparison table
    rows = []
    for name, stats in zip(image_names, ndvi_stats_list):
        rows.append({
            "Image Name": name,
            "NDVI Min": stats["NDVI Min"],
            "NDVI Max": stats["NDVI Max"],
            "NDVI Mean": stats["NDVI Mean"],
        })
    df = pd.DataFrame(rows).set_index("Image Name")

    st.markdown("### 📊 NDVI Statistics Comparison")
    st.dataframe(df, width='stretch')

    # Excel Export
    towrite = io.BytesIO()
    with pd.ExcelWriter(towrite, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='NDVI Stats')
        workbook = writer.book
        worksheet = writer.sheets['NDVI Stats']
        format1 = workbook.add_format({'num_format': '0.000'})
        worksheet.set_column('B:D', 12, format1)
    towrite.seek(0)

    st.download_button(label="📥 Download NDVI Stats Excel",
                       data=towrite,
                       file_name="NDVI_Stats_Report.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # AI-Powered Temporal Analysis (only if 2+ images)
    if len(ndvi_stats_list) >= 2:
        st.markdown("---")
        st.markdown("### 🤖 AI-Powered Temporal Analysis")
        
        # Show trend visualization
        trend_plot = plot_temporal_trend(image_names, ndvi_stats_list)
        st.image(trend_plot, caption="NDVI Trend Over Time", width='stretch')
        
        # Generate AI insights
        with st.spinner("🔍 Analyzing vegetation changes with AI..."):
            ai_analysis = generate_ai_temporal_analysis(image_names, ndvi_stats_list)
        
        if ai_analysis:
            st.markdown(ai_analysis)
        else:
            st.info("💡 AI analysis unavailable. Set `OPENROUTER_API_KEY` in .env file to enable AI-powered insights.")

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
    <a href="https://github.com/MPranaviReddy" target="_blank">Pranavi Reddy</a>, and
    <a href="https://github.com/Zahraaabidha" target="_blank">Aabidha Zahra</a>
</div>
'''
st.markdown(footer_html, unsafe_allow_html=True)
