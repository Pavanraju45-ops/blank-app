import streamlit as st
import pandas as pd

st.set_page_config(page_title="Cross Sell Opportunity Finder", layout="wide")

st.title("📊 Cross-Sell Opportunity Analyzer")
st.write("Upload your sales data and discover potential cross-selling opportunities based on industry purchasing patterns.")

# Upload file
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "csv"])

if uploaded_file:

    # Read file
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Required columns
    required_cols = [
        'Business Partner',
        'Industry of customer',
        'Product Category',
        'Product Search Key'
    ]

    if all(col in df.columns for col in required_cols):

        df = df[required_cols].drop_duplicates()

        st.success("File uploaded successfully!")

        # Sidebar Filters
        st.sidebar.header("Filters")

        selected_industry = st.sidebar.selectbox(
            "Select Industry",
            sorted(df['Industry of customer'].unique())
        )

        industry_df = df[df['Industry of customer'] == selected_industry]

        selected_partner = st.sidebar.selectbox(
            "Select Business Partner",
            sorted(industry_df['Business Partner'].unique())
        )

        threshold = st.sidebar.slider(
            "Recommendation Threshold (%)",
            min_value=10,
            max_value=100,
            value=40
        ) / 100

        # Calculate Industry Patterns
        total_customers = industry_df['Business Partner'].nunique()

        category_counts = industry_df.groupby('Product Category')['Business Partner'].nunique()

        common_categories = category_counts[
            category_counts / total_customers >= threshold
        ].index.tolist()

        partner_categories = industry_df[
            industry_df['Business Partner'] == selected_partner
        ]['Product Category'].unique()

        missing_categories = set(common_categories) - set(partner_categories)

        # Display Results
        st.subheader(f"🔍 Analysis for {selected_partner}")

        col1, col2 = st.columns(2)

        with col1:
            st.write("### Purchased Categories")
            st.write(list(partner_categories))

        with col2:
            st.write("### Recommended Cross-Sell Categories")
            if missing_categories:
                st.success(list(missing_categories))
            else:
                st.info("No cross-sell opportunities found.")

        # Show Industry Benchmark
        st.subheader("📈 Industry Purchase Benchmark")

        benchmark_df = pd.DataFrame({
            'Product Category': category_counts.index,
            'Customers Buying': category_counts.values,
            'Penetration %': round((category_counts.values / total_customers) * 100, 2)
        })

        st.dataframe(benchmark_df)

        # Download Button
        output_df = pd.DataFrame({
            'Business Partner': [selected_partner],
            'Industry': [selected_industry],
            'Recommended Categories': [", ".join(missing_categories)]
        })

        st.download_button(
            "📥 Download Recommendations",
            output_df.to_csv(index=False),
            file_name="cross_sell_recommendations.csv"
        )

    else:
        st.error("Uploaded file missing required columns.")
