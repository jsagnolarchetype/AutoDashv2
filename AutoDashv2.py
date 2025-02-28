import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import matplotlib.ticker as mtick
import warnings
warnings.filterwarnings("ignore", message="missing ScriptRunContext")

st.set_page_config(page_title="Financial Analysis Dashboard", page_icon="📊", layout="wide")

# Sidebar for file selection
st.sidebar.header("Select a File")
page = st.sidebar.selectbox("Choose a report type", ("AFC Profit and Loss", "Real Estate Profit and Loss"))

def load_and_process_data(file, rows_of_interest):
    if file is None:
        return None, None
    
    df = pd.read_excel(file, sheet_name="Profit and Loss", header=4, engine="openpyxl")
    df.rename(columns={"Unnamed: 0": "Description"}, inplace=True)
    
    extracted_data = {}
    for row in rows_of_interest:
        filtered_row = df[df["Description"] == row]
        if not filtered_row.empty:
            extracted_data[row] = filtered_row.iloc[0, 1:].values
    
    # Extract column names (months), removing "Total" if present
    columns = df.columns[1:]
    if "Total" in columns:
        columns = columns[:-1]

    # Convert values to numeric
    for key in extracted_data:
        extracted_data[key] = np.array(extracted_data[key][:len(columns)], dtype=float)

    return extracted_data, columns

def convert_to_dataframe(extracted_data, columns):
    data_list = []
    for idx, col in enumerate(columns):
        try:
            month, year = col.split()
            row_values = {row: extracted_data[row][idx] for row in extracted_data}
            data_list.append({"Year": year, "Month": month, **row_values})
        except ValueError:
            print(f"Skipping column '{col}' due to unexpected format.")
    
    df = pd.DataFrame(data_list)
    df["Year"] = df["Year"].astype(str)
    return df

def plot_time_series(extracted_data, columns):
    plt.figure(figsize=(12, 6))
    for row, values in extracted_data.items():
        plt.plot(columns, values, label=row, marker='o')

    plt.xlabel('Month')
    plt.ylabel('Amount ($)')
    plt.title('Financial Metrics Over Time')
    plt.legend(loc='upper left')
    plt.xticks(rotation=45)

    ax = plt.gca()
    ax.yaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}'))

    plt.tight_layout()
    st.pyplot(plt)

def plot_bar_chart(df, financial_metrics):
    fig = px.bar(
        df, x="Month", y="Net Income", color="Year",
        text_auto=".2s", title="Monthly Net Income Breakdown",
        labels={"Net Income": "Amount ($)", "Month": "Month"},
        hover_data=financial_metrics
    )
    fig.update_yaxes(tickprefix="$", tickformat=",.0f")
    st.plotly_chart(fig)

def plot_comparison_chart(df, selected_month, selected_metrics):
    if not selected_metrics or selected_month not in df["Month"].values:
        st.warning("Please select valid metrics and a month.")
        return

    filtered_df = df[df["Month"] == selected_month]
    melted_df = filtered_df.melt(id_vars=["Year", "Month"], value_vars=selected_metrics, var_name="Metric", value_name="Value")

    fig = px.bar(
        melted_df, x="Metric", y="Value", color="Year",
        text_auto=".2s", title=f"Comparison of Selected Metrics for {selected_month}",
        labels={"Value": "Amount ($)", "Metric": "Financial Metric"}
    )
    fig.update_yaxes(tickprefix="$", tickformat=",.0f")
    st.plotly_chart(fig)

if page == "AFC Profit and Loss":
    st.header("AFC Profit and Loss Analysis")
    file = st.file_uploader("Upload your AFC Profit and Loss Excel file", type=["xlsx"])

    rows_of_interest = ["Total Income", "Total Cost of Goods Sold", "Gross Profit", "Total Expenses", "Net Operating Income", "Net Income"]
    extracted_data, columns = load_and_process_data(file, rows_of_interest)

    if extracted_data:
        df = convert_to_dataframe(extracted_data, columns)
        plot_time_series(extracted_data, columns)
        plot_bar_chart(df, rows_of_interest)

        st.subheader("Compare Specific Month Metrics")
        selected_month = st.selectbox("Select a Month", df["Month"].unique())
        selected_metrics = st.multiselect("Select Metrics to Compare", rows_of_interest, default=["Total Income", "Net Income"])
        plot_comparison_chart(df, selected_month, selected_metrics)

elif page == "Real Estate Profit and Loss":
    st.header("Real Estate Profit and Loss Analysis")
    file = st.file_uploader("Upload your Real Estate Profit and Loss Excel file", type=["xlsx"])

    rows_of_interest = ["Total Income", "Gross Profit", "   Total Payroll & Related", "Total Expenses", "Net Operating Income", "Net Income"]
    extracted_data, columns = load_and_process_data(file, rows_of_interest)

    if extracted_data:
        df = convert_to_dataframe(extracted_data, columns)
        plot_time_series(extracted_data, columns)
        plot_bar_chart(df, rows_of_interest)

        st.subheader("Compare Specific Month Metrics")
        selected_month = st.selectbox("Select a Month", df["Month"].unique())
        selected_metrics = st.multiselect("Select Metrics to Compare", rows_of_interest, default=["Total Income", "Net Income"])
        plot_comparison_chart(df, selected_month, selected_metrics)


