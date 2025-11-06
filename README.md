# GreenVision: NDVI Analysis & Visualization 🌱

<p align="left">
  <a href="https://streamlit.io/"><img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit"></a>
  <a href="https://numpy.org/"><img src="https://img.shields.io/badge/Numpy-013243?style=for-the-badge&logo=NumPy&logoColor=white" alt="NumPy"></a>
  <a href="https://pandas.pydata.org/"><img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=Pandas&logoColor=white" alt="Pandas"></a>
  <a href="https://matplotlib.org/"><img src="https://img.shields.io/badge/Matplotlib-11557C?style=for-the-badge&logo=matplotlib&logoColor=white" alt="Matplotlib"></a>
  <a href="https://rasterio.readthedocs.io/"><img src="https://img.shields.io/badge/Rasterio-4479A1?style=for-the-badge&logo=python&logoColor=white" alt="Rasterio"></a>
  <a href="https://openrouter.ai/"><img src="https://img.shields.io/badge/OpenRouter_AI-00D4AA?style=for-the-badge&logo=openai&logoColor=white" alt="OpenRouter AI"></a>
</p>

## 📖 Overview

**GreenVision** is an interactive web application built with Streamlit to analyze and visualize **NDVI (Normalized Difference Vegetation Index)** from GeoTIFF images across different time periods. It helps monitor vegetation health, track environmental changes, and support agricultural decision-making.

### 🚀 Key Features

- ✅ **Upload Custom Data**: Upload your own NDVI GeoTIFF files or load sample data
- ✅ **Visualize NDVI Maps**: View input images and NDVI maps side-by-side
- ✅ **Statistical Analysis**: Display NDVI statistics (min, max, mean) for each image
- ✅ **Temporal Trend Visualization**: Line chart showing vegetation health over time
- ✅ **🤖 AI-Powered Analysis**: Get comprehensive temporal insights using AI (MiniMax M2 via OpenRouter)
- ✅ **Excel Export**: Download compiled NDVI statistics in Excel format
- ✅ **User-Friendly UI**: Loading animations and clean interface for better UX

## 📦 Installation

### 1. Clone the Repository
```
git clone https://github.com/tanishpoddar/GreenVision.git
```
```
cd GreenVision
```

### 2. Install Dependencies
```
pip install -r requirements.txt
```

### 3. Set Up AI Integration (Optional but Recommended)

To enable **AI-powered temporal analysis**, you need an OpenRouter API key:

#### Step 1: Get Your OpenRouter API Key
1. Visit [OpenRouter](https://openrouter.ai/)
2. Sign up or log in to your account
3. Navigate to **Keys** section
4. Create a new API key
5. Copy your API key (format: `sk-or-v1-xxxxx...`)

#### Step 2: Create `.env` File
Create a file named `.env` in the project root directory:
```
OPENROUTER_API_KEY=sk-or-v1-your-actual-api-key-here
```

**Important Notes:**
- Replace `sk-or-v1-your-actual-api-key-here` with your actual API key
- No spaces around the `=` sign
- No quotes needed
- Keep this file private (it's already in `.gitignore`)

**Model Used:** [MiniMax M2 (Free)](https://openrouter.ai/minimax/minimax-m2:free) - A high-efficiency AI model optimized for analytical workflows

> **Note:** The app works without an API key, but AI-powered temporal analysis will be unavailable. You'll see a message prompting you to add the key.

## 🚀 Running the App

Launch the Streamlit app:
```
streamlit run app.py --server.fileWatcherType none
```

The app will open in your browser at `http://localhost:8501`

## 📝 How to Use

### Option 1: Load Sample Data
1. Click **"Load Sample Data"** button
2. Sample NDVI images from 2020-2023 will be downloaded and analyzed automatically

### Option 2: Upload Your Own Data
1. Click **"Upload GeoTIFF files"**
2. Select one or more `.tif` or `.tiff` files
3. The app will process and display results

### Viewing Results
- **Individual Analysis**: Each image shows:
  - Input image (False Color Composite if available)
  - NDVI map with color gradient
  - Statistical summary (min, max, mean values)
  
- **Comparison Table**: View NDVI statistics for all images in a table format

- **Temporal Trend**: Line chart showing mean NDVI over time

- **🤖 AI Analysis** (if API key is set):
  - Overall vegetation trend assessment
  - Significant changes between periods
  - Context-aware NDVI interpretation
  - Possible environmental causes
  - Actionable land management recommendations

- **Excel Export**: Download complete statistics as `.xlsx` file

## 📄 License

This project is open source and available under the [GNU General Public License v3.0](LICENSE)
