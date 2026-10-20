# Data Visualization — Sales Analytics Dashboard

## Project Overview

This project is an interactive Sales Analytics Dashboard developed using Python, Pandas, Streamlit, and Plotly. It helps users explore sales performance, profitability, product categories, customer segments, and sales trends through interactive charts and filters.

## Features

- Key performance indicators for total sales, profit, orders, quantity sold, and profit margin.
- Interactive sales analysis by product category and region.
- Profit analysis by customer segment and region.
- Top sub-categories by sales.
- Monthly and yearly sales trends.
- Interactive filters for region, category, customer segment, and date range.
- Data explorer with CSV export.
- Data quality overview.

## Technologies Used

- Python
- Pandas
- Streamlit
- Plotly

## Project Structure

```text
DataVisualization/
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/DataVisualization.git
cd DataVisualization
```

Replace `YOUR-USERNAME` with your GitHub username.

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Run the dashboard

```bash
python -m streamlit run app.py
```

Open the local URL displayed in your terminal, usually `http://localhost:8501`.

## Dataset

The dashboard attempts to load a public Superstore sales dataset. If the public source is unavailable, users can upload a compatible CSV file through the dashboard sidebar.

The dataset should contain numeric Sales, Profit, and Quantity columns. Additional columns such as Order Date, Region, Category, and Segment enable more visualizations.

Check the dataset source and its license before redistributing the data.

## Learning Outcomes

- Data cleaning and preparation with Pandas.
- Interactive data visualization using Plotly.
- Building dashboards with Streamlit.
- Exploratory sales and profitability analysis.
- Filtering and exporting data.

## Project Status

Developed as a data visualization learning project.

## Author

sejal-Luhure
git clone https://github.com/Sejal-Luhure/DataVisualization.git


