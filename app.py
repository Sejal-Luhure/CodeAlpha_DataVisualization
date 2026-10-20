
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

st.set_page_config(
    page_title="Superstore Sales Analytics",
    page_icon="📊",
    layout="wide"
)

# -------------------- THEME --------------------
BG = "#111827"
PANEL = "#1F2937"
TEXT = "#E5E7EB"
MUTED = "#9CA3AF"
COLORS = ["#729FCF", "#76B7A0", "#B5A0D5", "#D9B779", "#D98989"]

st.markdown("""
<style>
.stApp { background-color: #111827; color: #E5E7EB; }
[data-testid="stHeader"] { background-color: #111827; }
[data-testid="stMetric"] {
    background: #1F2937;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #374151;
}
[data-testid="stMetricLabel"] { color: #9CA3AF; }
[data-testid="stMetricValue"] { color: #E5E7EB; }
h1, h2, h3 { color: #E5E7EB; }
</style>
""", unsafe_allow_html=True)


# -------------------- DATA LOADING --------------------
DATA_URLS = [
    "https://raw.githubusercontent.com/curran/data/gh-pages/superstoreSales/superstoreSales.csv",
    "https://raw.githubusercontent.com/aarushiibisht/Super-store-sales-Data-Analysis/main/Sample%20-%20Superstore.csv",
]

def normalize_columns(df):
    df.columns = [
        str(c).replace("\ufeff", "").strip().lower().replace("_", " ")
        for c in df.columns
    ]

    aliases = {
        "sales": ["sales", "revenue", "total sales"],
        "profit": ["profit", "net profit"],
        "quantity": ["quantity", "order quantity", "qty"],
        "order date": ["order date", "date", "purchase date"],
        "order id": ["order id", "order number", "transaction id"],
        "region": ["region", "market", "sales region"],
        "category": ["category", "product category"],
        "segment": ["segment", "customer segment"],
        "sub category": ["sub category", "product sub category"],
        "customer name": ["customer name", "customer"],
        "ship mode": ["ship mode", "shipping mode"],
        "state": ["state", "province"],
        "city": ["city"],
        "discount": ["discount"],
        "product name": ["product name", "product"],
    }

    rename = {}
    for standard, possible_names in aliases.items():
        for name in possible_names:
            if name in df.columns:
                rename[name] = standard
                break

    return df.rename(columns=rename)


def read_csv_robust(source):
    errors = []
    for encoding in ["utf-8", "cp1252", "latin1"]:
        try:
            if isinstance(source, bytes):
                return pd.read_csv(BytesIO(source), encoding=encoding, on_bad_lines="skip")
            return pd.read_csv(source, encoding=encoding, on_bad_lines="skip")
        except Exception as exc:
            errors.append(str(exc))
    raise ValueError("Could not read CSV: " + " | ".join(errors))


@st.cache_data(show_spinner=False)
def load_public_data():
    errors = []

    for url in DATA_URLS:
        try:
            df = read_csv_robust(url)
            df = normalize_columns(df)

            required = {"sales", "profit", "quantity"}
            if required.issubset(df.columns):
                return df, url, None

            errors.append(
                f"{url}\nAvailable columns: {', '.join(df.columns)}"
            )
        except Exception as exc:
            errors.append(f"{url}\n{exc}")

    return None, None, "\n\n".join(errors)


# -------------------- HEADER --------------------
st.title("📊 Superstore Sales Analytics")
st.caption("Interactive Data Visualization Dashboard")

uploaded = st.sidebar.file_uploader(
    "Upload your Superstore CSV (optional)",
    type=["csv"]
)

if uploaded is not None:
    try:
        df = read_csv_robust(uploaded.getvalue())
        df = normalize_columns(df)
        source_name = uploaded.name
    except Exception as exc:
        st.error(f"Unable to read uploaded CSV: {exc}")
        st.stop()
else:
    with st.spinner("Loading public Superstore dataset..."):
        df, source_name, load_error = load_public_data()

    if df is None:
        st.error("Unable to load a compatible public dataset.")
        st.warning(
            "Upload a Superstore CSV from the sidebar. "
            "It should include Sales, Profit and Quantity columns."
        )
        with st.expander("Technical details"):
            st.code(load_error or "Unknown dataset loading error")
        st.stop()


# -------------------- VALIDATE & CLEAN --------------------
required_columns = ["sales", "profit", "quantity"]
missing = [col for col in required_columns if col not in df.columns]

if missing:
    st.error(f"Missing required columns: {missing}")
    st.write("Columns detected in your dataset:")
    st.code(", ".join(df.columns))
    st.info(
        "Upload a CSV containing Sales, Profit and Quantity columns."
    )
    st.stop()

for col in ["sales", "profit", "quantity", "discount"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

df["sales"] = df["sales"].fillna(0)
df["profit"] = df["profit"].fillna(0)
df["quantity"] = df["quantity"].fillna(0)

if "order date" in df.columns:
    df["order date"] = pd.to_datetime(
        df["order date"], errors="coerce"
    )

if "order id" not in df.columns:
    df["order id"] = pd.Series(range(1, len(df) + 1), index=df.index)

for col in ["region", "category", "segment", "sub category",
            "customer name", "ship mode", "state", "city"]:
    if col not in df.columns:
        df[col] = "Unknown"
    df[col] = df[col].fillna("Unknown").astype(str)

if "discount" not in df.columns:
    df["discount"] = 0

df = df.dropna(subset=["sales", "profit", "quantity"])

if df.empty:
    st.error("The dataset contains no usable rows.")
    st.stop()


# -------------------- FILTERS --------------------
st.sidebar.header("Dashboard Filters")

def filter_options(column, label):
    options = sorted(df[column].dropna().unique().tolist())
    return st.sidebar.multiselect(
        label, options, default=options
    )

regions = filter_options("region", "Region")
categories = filter_options("category", "Category")
segments = filter_options("segment", "Customer Segment")

filtered = df[
    df["region"].isin(regions)
    & df["category"].isin(categories)
    & df["segment"].isin(segments)
].copy()

if "order date" in filtered.columns and filtered["order date"].notna().any():
    valid_dates = filtered["order date"].dropna()
    start_date = valid_dates.min().date()
    end_date = valid_dates.max().date()

    date_range = st.sidebar.date_input(
        "Order Date Range",
        value=(start_date, end_date),
        min_value=start_date,
        max_value=end_date
    )

    if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
        start, end = date_range
        filtered = filtered[
            filtered["order date"].isna()
            | (
                (filtered["order date"].dt.date >= start)
                & (filtered["order date"].dt.date <= end)
            )
        ]

if filtered.empty:
    st.warning("No records match the selected filters.")
    st.stop()


# -------------------- KPI CARDS --------------------
total_sales = filtered["sales"].sum()
total_profit = filtered["profit"].sum()
total_quantity = filtered["quantity"].sum()
total_orders = filtered["order id"].nunique()
profit_margin = (total_profit / total_sales * 100) if total_sales else 0

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Sales", f"${total_sales:,.2f}")
c2.metric("Total Profit", f"${total_profit:,.2f}")
c3.metric("Orders", f"{total_orders:,}")
c4.metric("Quantity Sold", f"{total_quantity:,.0f}")
c5.metric("Profit Margin", f"{profit_margin:.1f}%")

st.caption(f"Dataset: {source_name} | Records shown: {len(filtered):,}")


# -------------------- CHART HELPERS --------------------
def style_chart(fig, height=400):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=BG,
        plot_bgcolor=PANEL,
        font=dict(color=TEXT),
        height=height,
        margin=dict(l=20, r=20, t=55, b=20),
        legend_title_text=""
    )
    return fig


# -------------------- TABS --------------------
overview, products, trends, records = st.tabs([
    "Overview", "Products & Regions", "Sales Trends", "Data Explorer"
])

with overview:
    left, right = st.columns(2)

    with left:
        category_sales = (
            filtered.groupby("category", as_index=False)["sales"]
            .sum().sort_values("sales", ascending=False)
        )
        fig = px.bar(
            category_sales, x="category", y="sales",
            color="category", color_discrete_sequence=COLORS,
            title="Sales by Category",
            labels={"category": "Category", "sales": "Sales"}
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(style_chart(fig), use_container_width=True)

    with right:
        region_sales = (
            filtered.groupby("region", as_index=False)["sales"]
            .sum().sort_values("sales", ascending=False)
        )
        fig = px.pie(
            region_sales, names="region", values="sales",
            hole=0.55, title="Sales Share by Region",
            color_discrete_sequence=COLORS
        )
        st.plotly_chart(style_chart(fig), use_container_width=True)

    left, right = st.columns(2)

    with left:
        segment_profit = (
            filtered.groupby("segment", as_index=False)["profit"]
            .sum().sort_values("profit", ascending=True)
        )
        fig = px.bar(
            segment_profit, x="profit", y="segment",
            orientation="h", color="segment",
            color_discrete_sequence=COLORS,
            title="Profit by Customer Segment"
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(style_chart(fig), use_container_width=True)

    with right:
        fig = px.scatter(
            filtered, x="sales", y="profit",
            color="category", size="quantity",
            hover_data=["region", "segment"],
            color_discrete_sequence=COLORS,
            title="Sales vs Profit"
        )
        st.plotly_chart(style_chart(fig), use_container_width=True)


with products:
    left, right = st.columns(2)

    with left:
        subcat = (
            filtered.groupby("sub category", as_index=False)["sales"]
            .sum().sort_values("sales", ascending=False).head(12)
        )
        fig = px.bar(
            subcat, x="sales", y="sub category",
            orientation="h", color="sales",
            color_continuous_scale=["#374151", "#729FCF"],
            title="Top 12 Sub-Categories by Sales"
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(style_chart(fig), use_container_width=True)

    with right:
        region_profit = (
            filtered.groupby("region", as_index=False)["profit"]
            .sum().sort_values("profit", ascending=False)
        )
        fig = px.bar(
            region_profit, x="region", y="profit",
            color="region", color_discrete_sequence=COLORS,
            title="Profit by Region"
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(style_chart(fig), use_container_width=True)

    st.subheader("Category Summary")
    summary = filtered.groupby("category", as_index=False).agg(
        Sales=("sales", "sum"),
        Profit=("profit", "sum"),
        Quantity=("quantity", "sum"),
        Orders=("order id", "nunique")
    )
    st.dataframe(summary, use_container_width=True, hide_index=True)


with trends:
    if "order date" in filtered.columns and filtered["order date"].notna().any():
        dated = filtered.dropna(subset=["order date"]).copy()
        dated["Month"] = dated["order date"].dt.to_period("M").astype(str)
        monthly = dated.groupby("Month", as_index=False).agg(
            Sales=("sales", "sum"),
            Profit=("profit", "sum")
        )

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=monthly["Month"], y=monthly["Sales"],
            mode="lines+markers", name="Sales",
            line=dict(color=COLORS[0], width=3)
        ))
        fig.add_trace(go.Scatter(
            x=monthly["Month"], y=monthly["Profit"],
            mode="lines+markers", name="Profit",
            line=dict(color=COLORS[1], width=3)
        ))
        fig.update_layout(title="Monthly Sales and Profit Trend")
        st.plotly_chart(style_chart(fig, 450), use_container_width=True)

        yearly = dated.copy()
        yearly["Year"] = yearly["order date"].dt.year.astype(str)
        yearly = yearly.groupby("Year", as_index=False).agg(
            Sales=("sales", "sum"),
            Profit=("profit", "sum")
        )

        fig = px.bar(
            yearly, x="Year", y="Sales",
            color="Year", color_discrete_sequence=COLORS,
            title="Yearly Sales"
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(style_chart(fig), use_container_width=True)
    else:
        st.info("This dataset has no valid order dates for trend analysis.")


with records:
    st.subheader("Filtered Dataset")
    st.dataframe(filtered, use_container_width=True, hide_index=True)

    csv_data = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Filtered Data as CSV",
        data=csv_data,
        file_name="filtered_superstore_sales.csv",
        mime="text/csv"
    )

    st.subheader("Data Quality")
    quality = pd.DataFrame({
        "Column": filtered.columns,
        "Missing Values": filtered.isna().sum().values,
        "Data Type": filtered.dtypes.astype(str).values
    })
    st.dataframe(quality, use_container_width=True, hide_index=True)

st.sidebar.divider()
st.sidebar.caption("Interactive Sales Analytics | Python + Streamlit + Plotly")
