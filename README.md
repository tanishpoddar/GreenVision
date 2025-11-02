# GreenVision: NDVI Analysis & Visualization

<p align="left">
  <a href="https://streamlit.io/"><img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit"></a>
  <a href="https://numpy.org/"><img src="https://img.shields.io/badge/Numpy-013243?style=for-the-badge&logo=NumPy&logoColor=white" alt="NumPy"></a>
  <a href="https://pandas.pydata.org/"><img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=Pandas&logoColor=white" alt="Pandas"></a>
  <a href="https://matplotlib.org/"><img src="https://img.shields.io/badge/Matplotlib-11557C?style=for-the-badge&logo=matplotlib&logoColor=white" alt="Matplotlib"></a>
  <a href="https://gdown.readthedocs.io/en/latest/"><img src="https://img.shields.io/badge/gdown-28A745?style=for-the-badge&logo=python&logoColor=white" alt="gdown"></a>
</p>

## Overview

GreenVision is an interactive web app built on Streamlit to analyze and visualize NDVI (Normalized Difference Vegetation Index) from GeoTIFF images across different years or time points.

Main features include:

- Upload your own NDVI GeoTIFF files or load sample data.
- Visualize input images and NDVI maps side by side.
- Display NDVI statistics (min, max, mean) per image.
- Download compiled NDVI statistics in a downloadable Excel report.
- Loading animations for better user experience.


## How to Run

1. Clone or download the repository.
```
https://github.com/tanishpoddar/GreenVision.git
```
3. Install required dependencies using:
```
pip install -r requirements.txt
```


3. Launch the app:
```
streamlit run app.py
```

## Motivation

This app helps users check vegetation changes over time at the same location, useful for monitoring crop health, environmental changes, or ecological research.


## Tech Stack

- [Streamlit](https://streamlit.io) for easy and fast UI.
- [rasterio](https://rasterio.readthedocs.io) for geospatial raster data processing.
- [NumPy](https://numpy.org) for numerical operations.
- [Pandas](https://pandas.pydata.org) for data handling and Excel export.
- [Matplotlib](https://matplotlib.org) for plotting.
- [gdown](https://gdown.readthedocs.io) for efficient downloading from Google Drive.


## Contributors

- [Tanish Poddar](https://github.com/tanishpoddar)
- [Aabidha Zahra](https://github.com/Zahraaabidha)
- [Pranavi Reddy](https://github.com/MPranaviReddy)
