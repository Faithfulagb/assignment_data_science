import streamlit as st
import pandas as pd
import plotly.express as px


@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['property_size'] = pd.to_numeric(df['property_size'], errors='coerce')
    df['bedrooms'] = pd.to_numeric(df['bedrooms'], errors='coerce')
    df['bathrooms'] = pd.to_numeric(df['bathrooms'], errors='coerce')
    return df

def plot_listings_per_state(df):
    data = df['state_mapped'].value_counts().reset_index()
    data.columns = ['State', 'Listings']
    fig = px.bar(data, x='State', y='Listings', color='Listings',
                 title="Number of Listings per State")
    fig.update_traces(text=None)
    return fig

def plot_avg_price_per_state(df):
    data = df.groupby('state_mapped')['price'].mean().reset_index()
    fig = px.bar(data, x='state_mapped', y='price', color='price', 
                 title="Average House Price per State")
    fig.update_traces(text=None)
    return fig

def plot_price_distribution(df):
    fig = px.histogram(df, x='price', nbins=50, title="Distribution of Property Prices")
    return fig

def plot_price_by_bedrooms(df):
    fig = px.box(df, x='bedrooms', y='price', title="Price by Number of Bedrooms")
    return fig

def plot_size_vs_price(df):
    fig = px.scatter(df, x='property_size', y='price', color='bedrooms', 
                     hover_data=['state_mapped','region_name'], title="Property Size vs Price")
    return fig

def plot_furnishing_distribution(df):
    data = df['furnishing'].value_counts().reset_index()
    data.columns = ['Furnishing', 'Count']
    fig = px.pie(data, names='Furnishing', values='Count', title="Furnishing Type Distribution")
    return fig

def plot_correlation_heatmap(df):
    corr = df[['price','property_size','bedrooms','bathrooms']].corr()
    fig = px.imshow(corr, text_auto=True, color_continuous_scale='Viridis', 
                    title="Correlation Heatmap: Price, Size, Bedrooms, Bathrooms")
    return fig

def main():
    st.set_page_config(page_title="Jiji Housing Dashboard", layout="wide")
    st.title("Market Analysis of Housing Sales on Jiji.ng")
    
    df = load_data("jiji_housing_cleaned.csv")
    
    st.sidebar.header("Filters")
    states_selected = st.sidebar.multiselect(
        "Select States", options=df['state_mapped'].unique(), default=df['state_mapped'].unique()
    )
    furnishing_selected = st.sidebar.multiselect(
        "Select Furnishing Type", options=df['furnishing'].unique(), default=df['furnishing'].unique()
    )
    listing_type_selected = st.sidebar.multiselect(
        "Select Listing Type", options=df['is_boost'].unique(), default=df['is_boost'].unique()
    )
    
    df_filtered = df[
        (df['state_mapped'].isin(states_selected)) &
        (df['furnishing'].isin(furnishing_selected)) &
        (df['is_boost'].isin(listing_type_selected))
    ]
    
    col1, col2, col3, col4 = st.columns([1.3, 1, 1, 1])
    
    col1.metric("Average House Price", f"₦{df_filtered['price'].mean():,.0f}")
    col2.metric("Highest Priced State", df_filtered.groupby('state_mapped')['price'].mean().idxmax())
    col3.metric("Most Affordable State", df_filtered.groupby('state_mapped')['price'].mean().idxmin())
    col4.metric("Total Listings", f"{len(df_filtered):,}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(plot_listings_per_state(df_filtered), use_container_width=True)
    with col2:
        st.plotly_chart(plot_avg_price_per_state(df_filtered), use_container_width=True)
    
    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(plot_price_distribution(df_filtered), use_container_width=True)
    with col4:
        st.plotly_chart(plot_price_by_bedrooms(df_filtered), use_container_width=True)
    
    col5, col6 = st.columns(2)
    with col5:
        st.plotly_chart(plot_size_vs_price(df_filtered), use_container_width=True)
    with col6:
        st.plotly_chart(plot_furnishing_distribution(df_filtered), use_container_width=True)
    
    st.plotly_chart(plot_correlation_heatmap(df_filtered), use_container_width=True)

if __name__ == "__main__":
    main()