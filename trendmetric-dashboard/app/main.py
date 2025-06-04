import streamlit as st
import pandas as pd
import snowflake.connector
import plotly.express as px
import os
import time
from datetime import datetime



st.set_page_config(page_title="Trend Metric | Product Analysis", layout="wide")
# ---------------------- Constants ----------------------
SESSION_DURATION = 4 * 60 * 60  # 4 hours in seconds
LOGO_URL = "https://www.dropbox.com/scl/fi/cie56y5sqe1iwu2xzhbzf/trend.png?rlkey=78mweg7tm9833lugvrtt0bs2v&raw=1"

# ---------------------- Session State Initialization ----------------------
def check_authentication():
    now = time.time()
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.login_time = 0

    if st.session_state.authenticated and (now - st.session_state.login_time) < SESSION_DURATION:
        return True
    else:
        st.session_state.authenticated = False
        return False


def show_login():
    st.markdown("""
        <style>
            .login-logo {
                display: flex;
                justify-content: center;
                margin-top: 30px;
                margin-bottom: 20px;
            }
            .login-title {
                text-align: center;
                font-size: 24px;
                font-weight: 700;
                margin-bottom: 6px;
            }
            .login-subtext {
                text-align: center;
                font-size: 14px;
                color: #888;
                margin-bottom: 24px;
            }
            .social-icons {
                display: flex;
                justify-content: center;
                gap: 20px;
                margin-top: 24px;
            }
            .social-icons img {
                width: 36px;
                cursor: pointer;
            }
        </style>
    """, unsafe_allow_html=True)

    logo_col1, logo_col2, logo_col3 = st.columns([4, 1, 4])
    with logo_col2:
        st.image(LOGO_URL, width=160)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown('<div class="login-title">Login to your account</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtext">Hello, welcome back to your account</div>', unsafe_allow_html=True)

        email = st.text_input("E-mail", placeholder="example@email.com", label_visibility="collapsed", key="email")
        password = st.text_input("Password", placeholder="Your Password", type="password", label_visibility="collapsed", key="password")
        st.checkbox("Remember me", key="remember")

        if st.button("Login", key="login", use_container_width=True):
            if email == "arincubuk" and password == "demo123":  # 🔐 Replace this later with env/secrets
                st.session_state.authenticated = True
                st.session_state.login_time = time.time()
                st.rerun()
            else:
                st.error("Invalid credentials")

        st.markdown("""
            <div class="social-icons">
                <img src="https://img.icons8.com/color/48/facebook.png" />
                <img src="https://img.icons8.com/color/48/google-logo.png" />
                <img src="https://img.icons8.com/ios-filled/50/mac-os.png" />
            </div>
        </div>
        """, unsafe_allow_html=True)


# ---------------------- Authentication Check ----------------------
if not check_authentication():
    show_login()
    st.stop()
# ---------------------- Page Title & Sidebar ----------------------
st.markdown("""
    <style>
        .card {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 18px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
        margin-bottom: 30px;
    }
    .main-container {
        background-color: #f7f8fc;
        padding: 2rem;
    }
    /* Shrink sidebar width */
    [data-testid="stSidebar"] {
        width: 220px;
        min-width: 220px;
        background-color: #f8f9fa;
        padding: 1rem 1rem 2rem 1rem;
        border-radius: 16px;
        box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
    }

    /* Shrink logo size inside sidebar */
    [data-testid="stSidebar"] img {
        width: 120px !important;
        border-radius: 8px;
        margin-bottom: 16px;
    }

    /* Sidebar links style */
    .sidebar-links {
        font-family: 'Segoe UI', sans-serif;
        font-size: 15px;
        margin-top: 16px;
    }
    .nav-link {
        display: block;
        padding: 10px 14px;
        margin: 6px 0;
        border-radius: 8px;
        color: #333;
        text-decoration: none;
        background-color: #f1f1f1;
        transition: background-color 0.2s ease-in-out;
    }
    .nav-link:hover {
        background-color: #e2e6ea;
    }
    .active-link {
        background-color: #007bff !important;
        color: white !important;
    }
    group-box {
        background-color: #fff;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 30px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
        transition: box-shadow 0.2s ease-in-out;
    }
    .group-box:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .product-title {
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 12px;
    }
    .header-row, .data-row {
        display: flex;
        justify-content: space-between;
        padding: 6px 0;
        border-bottom: 1px solid #f0f0f0;
        font-size: 14px;
    }
    .header-row {
        font-weight: bold;
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 10px;
    }
    .data-col {
        flex: 1;
        text-align: center;
    }
    .image-wrapper {
        text-align: center;
        margin-bottom: 10px;
    }
    .product-title {
        font-size: 18px;
        font-weight: 600;
        color: #212529;
        margin-bottom: 8px;
    }
    .variant-size {
        font-size: 14px;
        font-weight: 500;
        color: #333333;
        padding-top: 8px;
    }
    .main-title {
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .subtext {
        font-size: 16px;
        color: #6c757d;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    sidebar-links {
        font-family: 'Segoe UI', sans-serif;
        font-size: 16px;
        margin-top: 20px;
    }
    .nav-link {
        display: block;
        padding: 10px 16px;
        margin: 8px 0;
        border-radius: 8px;
        color: #333;
        text-decoration: none;
        background-color: #f1f1f1;
        transition: background-color 0.2s ease-in-out;
    }
    .nav-link:hover {
        background-color: #e2e6ea;
    }
    .active-link {
        background-color: #007bff !important;
        color: white !important;
    }
    .main-title {
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .subtext {
        font-size: 16px;
        color: #6c757d;
    }
    </style>
""", unsafe_allow_html=True)

# Apply light background globally
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# --------- Sidebar Navigation with Custom HTML ---------
if "active_page" not in st.session_state:
    st.session_state.active_page = "Dashboard"

LOGO_URL = "https://www.dropbox.com/scl/fi/cie56y5sqe1iwu2xzhbzf/trend.png?rlkey=78mweg7tm9833lugvrtt0bs2v&raw=1"
st.sidebar.image(LOGO_URL, width=120, use_container_width=False)
st.sidebar.markdown("## Navigation")
st.sidebar.markdown("<div class='sidebar-links'>", unsafe_allow_html=True)
if st.sidebar.button("Dashboard"):
    st.session_state.active_page = "Dashboard"
if st.sidebar.button("Product Analysis"):
    st.session_state.active_page = "Product Analysis"
if st.sidebar.button("Reports"):
    st.session_state.active_page = "Reports"
st.sidebar.markdown("</div>", unsafe_allow_html=True)

page = st.session_state.active_page

# Page Title (with new style & Lucide icon)
if page == "Dashboard":
    st.markdown(f"<div class='main-title'><i class='lu lu-presentation'></i> Dashboard</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtext'>Overview of production, sales, and return KPIs</div>", unsafe_allow_html=True)
elif page == "Product Analysis":
    st.markdown(f"<div class='main-title'><i class='lu lu-package-check'></i> Product Analysis</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtext'>Live SKU Ranking Table — Powered by Snowflake</div>", unsafe_allow_html=True)

# ---------------------- Session Init ----------------------
if "visible_skus" not in st.session_state:
    st.session_state.visible_skus = 10

# ---------------------- Snowflake Connection ----------------------
@st.cache_data
def get_production_data():
    conn = snowflake.connector.connect(
        user=st.secrets["snowflake"]["user"],
        password=st.secrets["snowflake"]["password"],
        account=st.secrets["snowflake"]["account"],
        warehouse=st.secrets["snowflake"]["warehouse"],
        database=st.secrets["snowflake"]["database"],
        schema=st.secrets["snowflake"]["schema"],
        role=st.secrets["snowflake"]["role"]
    )

    query = """
    SELECT
        MASTER_SKU,
        VARIANT_SKU,
        PRODUCT_SIZE,
        TOTAL_SALES,
        SHOPIFY_INVENTORY AS STOCK,
        DAILY_SALES_VELOCITY_SCORE AS MARKETABILITY,
        RETURN_PERCENTAGE,
        IMAGE_LINK,
        RANKS
    FROM UNIFIED_DATA
    ORDER BY MASTER_SKU, PRODUCT_SIZE
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


@st.cache_data
def get_order_data():
    conn = snowflake.connector.connect(
        user=st.secrets["snowflake"]["user"],
        password=st.secrets["snowflake"]["password"],
        account=st.secrets["snowflake"]["account"],
        warehouse=st.secrets["snowflake"]["warehouse"],
        database=st.secrets["snowflake"]["database"],
        schema=st.secrets["snowflake"]["schema"],
        role=st.secrets["snowflake"]["role"]
    )

    query = """
        SELECT CREATED_DATE_ORDERS_ORDER_LINES AS CREATED_DATE,
               QUANTITY_ORDERS_ORDER_LINES AS QUANTITY
        FROM ORDERS_ORDER_LINES_NEW
        """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


df_orders = get_order_data()
df_orders["CREATED_DATE"] = pd.to_datetime(df_orders["CREATED_DATE"])
df_orders["Month"] = df_orders["CREATED_DATE"].dt.to_period("M").astype(str)
monthly_sales = df_orders.groupby("Month")["QUANTITY"].sum().reset_index()

# ---------------------- Load Data ----------------------
df = get_production_data()
# Replace broken/empty image links with placeholder
placeholder_img = "https://via.placeholder.com/120"
df["IMAGE"] = df["IMAGE_LINK"].apply(lambda x: x if isinstance(x, str) and x.strip() != "" else placeholder_img)



st.markdown('</div>', unsafe_allow_html=True)  # Close main container

# ---------------------- Ensure Order for Pagination ----------------------
if "selected_sku" not in st.session_state:
    st.session_state.selected_sku = None
# Initialize session state variable for sorted_skus
if "sorted_skus" not in st.session_state:
    st.session_state.sorted_skus = (
        df.drop_duplicates(subset="MASTER_SKU")
          .sort_values("RANKS")["MASTER_SKU"]
          .tolist()
    )

df["MASTER_SKU"] = pd.Categorical(df["MASTER_SKU"], categories=st.session_state.sorted_skus, ordered=True)
df = df.sort_values(["MASTER_SKU", "PRODUCT_SIZE"])

# ---------------------- Filter for Pagination ----------------------
visible_count = st.session_state.visible_skus
visible_skus = st.session_state.sorted_skus[:visible_count]
filtered_df = df[df["MASTER_SKU"].isin(visible_skus)]

# ---------------------- Custom Styling ----------------------
st.markdown("""
    <style>
        .metric-label { font-size: 18px; color: #6c757d; }
        .metric-value { font-size: 18px; font-weight: 600; }
        .product-title { font-size: 18px; font-weight: bold; margin-bottom: 0.5rem; }
        .variant-size { font-size: 18px; font-weight: 500; margin-top: 0.5rem; }
        .group-box { background-color: #f9f9f9; border-radius: 12px; padding: 1rem; margin-bottom: 2rem; }
    </style>
""", unsafe_allow_html=True)
# ---------------------- Dashboard Content ----------------------
if page == "Dashboard":
    # ---- KPIs (replace these with dynamic values if needed) ----
    total_sales = 1788
    total_returns = 430
    return_pct = 24.0
    cancellations = 238

    # ---- Top White Strip with Date Filter and KPIs ----
    st.markdown("""
        <style>
        .top-strip {
            background-color: #ffffff;
            padding: 20px 30px;
            border-bottom: 1px solid #e0e0e0;
            border-radius: 0 0 16px 16px;
            margin-left: -3rem;
            margin-right: -3rem;
        }
        .kpi-container {
            display: flex;
            justify-content: space-between;
            gap: 2rem;
            margin-top: 10px;
        }
        .kpi-box {
            flex: 1;
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 16px;
            text-align: center;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        }
        .kpi-title {
            font-size: 14px;
            color: #6c757d;
            margin-bottom: 8px;
        }
        .kpi-value {
            font-size: 24px;
            font-weight: 700;
            color: #333;
        }
        .date-range-box {
            display: flex;
            gap: 1rem;
            align-items: center;
            margin-bottom: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="top-strip">', unsafe_allow_html=True)

        col1, col2 = st.columns([2, 6])
        with col1:
            start_date = st.date_input("Start date", datetime(2024, 1, 1))
        with col2:
            end_date = st.date_input("End date", datetime.today())

        st.markdown("""
            <div class="kpi-container">
                <div class="kpi-box">
                    <div class="kpi-title">Total Sales</div>
                    <div class="kpi-value">{:,}</div>
                </div>
                <div class="kpi-box">
                    <div class="kpi-title">Total Returns</div>
                    <div class="kpi-value">{:,}</div>
                </div>
                <div class="kpi-box">
                    <div class="kpi-title">Return %</div>
                    <div class="kpi-value">{:.1f}%</div>
                </div>
                <div class="kpi-box">
                    <div class="kpi-title">Cancellations</div>
                    <div class="kpi-value">{:,}</div>
                </div>
            </div>
        </div>
        """.format(total_sales, total_returns, return_pct, cancellations), unsafe_allow_html=True)
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### Monthly Units Sold")

        fig = px.bar(
            monthly_sales,
            x="Month",
            y="QUANTITY",
            labels={"QUANTITY": "Units Sold", "Month": "Month"},
            color_discrete_sequence=["#7367f0"]
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#333", size=14),
            margin=dict(t=30, b=10)
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Dummy sales-by-location data (replace with your real sales data)
    map_data = pd.DataFrame({
        'City': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Miami'],
        'Sales': [300, 200, 150, 180, 220],
        'Lat': [40.7128, 34.0522, 41.8781, 29.7604, 25.7617],
        'Lon': [-74.0060, -118.2437, -87.6298, -95.3698, -80.1918]
        })

    # Styling + map container
    st.markdown("""
    <style>
        .card-map {
            background-color: #ffffff;
            padding: 30px;
            border-radius: 18px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
            margin-bottom: 30px;
        }
    </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="card-map">', unsafe_allow_html=True)
        st.markdown("### Sales by Location")

    fig = px.scatter_mapbox(
        map_data,
        lat="Lat",
        lon="Lon",
        size="Sales",
        color="Sales",
        hover_name="City",
        zoom=3,
        height=500,
        color_continuous_scale=px.colors.sequential.Purples
    )
    fig.update_layout(
        mapbox_style="carto-positron",
        margin={"r":0,"t":0,"l":0,"b":0},
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
# ---------------------- Render Grouped Table ----------------------
unique_skus = df["MASTER_SKU"].drop_duplicates().tolist()
visible_skus = unique_skus[:visible_count]
filtered_df = df[df["MASTER_SKU"].isin(visible_skus)]

# Only render table for Product Analysis
if page == "Product Analysis":
    # ---------------------- Search ----------------------
    st.markdown("""
        <style>
            input[type="text"] {
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                border: 1px solid #ccc;
                width: 100%;
            }
        </style>
    """, unsafe_allow_html=True)

    search_input = st.text_input("🔍 Type to search SKU")
    if search_input:
        df = df[df["MASTER_SKU"].str.contains(search_input, case=False, na=False)]

    for master_sku, group in filtered_df.groupby("MASTER_SKU"):
        if group.empty:
            continue

        with st.container():
            st.markdown("<div class='group-box'>", unsafe_allow_html=True)

            col_image, col_data = st.columns([1.2, 5])
            with col_image:
                st.markdown(f"<div class='product-title'>{master_sku}</div>", unsafe_allow_html=True)
                st.image(group["IMAGE"].iloc[0], width=160)

            with col_data:
                # Header Row
                header_cols = st.columns([1.5, 1, 1, 1, 1])
                header_cols[0].markdown("**Size**")
                header_cols[1].markdown("**Sales**")
                header_cols[2].markdown("**Stock**")
                header_cols[3].markdown("**Marketability**")
                header_cols[4].markdown("**Returns**")

                # Data Rows
                for _, row in group.iterrows():
                    cols = st.columns([1.5, 1, 1, 1, 1])
                    cols[0].markdown(f"{row['PRODUCT_SIZE']}")
                    sales = int(row["TOTAL_SALES"]) if pd.notna(row["TOTAL_SALES"]) else 0
                    stock = int(row["STOCK"]) if pd.notna(row["STOCK"]) else 0
                    market = round(row["MARKETABILITY"], 2) if pd.notna(row["MARKETABILITY"]) else 0
                    returns = round(row["RETURN_PERCENTAGE"], 1) if pd.notna(row["RETURN_PERCENTAGE"]) else 0

                    cols[1].markdown(f"{sales}")
                    cols[2].markdown(f"{stock}")
                    cols[3].markdown(f"{market}")
                    cols[4].markdown(f"{returns}%")

            st.markdown("</div>", unsafe_allow_html=True)  # Close group-box
             # ---- Modal simulation ----
    if st.session_state.selected_sku:
        clicked_data = df[df["MASTER_SKU"] == st.session_state.selected_sku]

        with st.expander(f"🔍 Product Details — {st.session_state.selected_sku}", expanded=True):
            st.image(clicked_data["IMAGE"].iloc[0], width=200)
            st.markdown("### This will be replaced with AI-powered insights...")
            st.markdown(f"**Total Variants:** {clicked_data.shape[0]}")
            st.dataframe(clicked_data[["PRODUCT_SIZE", "TOTAL_SALES", "STOCK", "MARKETABILITY", "RETURN_PERCENTAGE"]])

        if st.button("❌ Close", key="close_modal"):
            st.session_state.selected_sku = None

elif page == "Reports":
    from Daily_sales_report import generate_daily_sales_report
    st.markdown("### 📥 Download Reports")
    if st.button("Download Daily Sales Report"):
        output, filename = generate_daily_sales_report()
        st.download_button(
            label="📄 Click to Download Excel Report",
            data=output,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


    # --------------- Load More Button ------------------
    if visible_count < len(unique_skus):
        if st.button("🔄 Load More SKUs"):
            st.session_state.visible_skus += 10
            st.rerun()
