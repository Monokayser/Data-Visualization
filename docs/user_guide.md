# User Guide

## Data Visualization Web Application

This guide explains how to use the Bangladesh Educational Institutes Explorer dashboard.

## 1. Open the App

Run the app locally with:

```bash
streamlit run app.py
```

Then open the browser URL shown by Streamlit.

## 2. Select Dataset Sheet

Use the sidebar `Dataset sheet / category` dropdown to choose one of the workbook sheets. The `All` sheet is selected by default.

## 3. Apply Filters

Use sidebar filters to narrow the dataset by:

- District
- Upazila / Thana
- Institute Type
- Institute Level
- Management
- MPO Status
- Study Type
- Area
- Geography

The upazila/thana filter updates based on the selected district.

## 4. Search Records

Use the search box to find records by:

- EIIN
- Institute name
- Address
- Post
- District
- Upazila / Thana

## 5. Explore Dashboard Sections

### Overview

Shows KPI cards, district-level institute concentration, top districts, and public/private comparison.

### Analytics

Shows institute type, institute level, management, MPO, study type, area, and geography distributions.

### Records

Shows the filtered data table and download buttons.

### Methodology & About

Shows dataset summary, preprocessing notes, and project information.

## 6. Download Data

In the `Records` tab, click:

- `Download CSV`
- `Download Excel`

The downloaded file contains the current filtered records.

## 7. Important Map Note

The dataset does not include latitude and longitude. The dashboard uses district-level aggregation only and does not show exact institute locations.

## 8. Troubleshooting

If the app does not load:

1. Confirm `data/raw/edu_institutes.xlsx` exists.
2. Install dependencies with `pip install -r requirements.txt`.
3. Use Python 3.11 or 3.12 for the most stable deployment experience.
4. Re-run `streamlit run app.py`.

