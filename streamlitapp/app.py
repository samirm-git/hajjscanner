import streamlit as st
import pandas as pd
import altair as alt
from dataLoader import loadData 

queryName = 'allData'

def apply_package_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Render sidebar filters and return the filtered dataframe."""
    st.sidebar.header("🔍 Filters")

    # --- Shifting ---
    shifting_options = ["All", "Shifting only", "Non-shifting only"]
    shifting_choice = st.sidebar.radio("Shifting", shifting_options, index=0)
    if shifting_choice == "Shifting only":
        df = df[df['isShifting'] == True]
    elif shifting_choice == "Non-shifting only":
        df = df[df['isSifting'] == False]
  
    #--- boolean options (hasAc, hasWifi isVisaIncluded)
    hasAc, hasWifi, isVisaIncluded = st.sidebar.columns(3)
    hasAc = hasAc.checkbox("AC")
    hasWifi = hasWifi.checkbox("Wifi")
    isVisaIncluded = isVisaIncluded.checkbox("Visa")

    if hasAc:
      df = df.query("makkah_hasAC and madinah_hasAC")
    if hasWifi:
      df = df.query("makkah_hasWifi and madinah_hasWifi")
    if isVisaIncluded:
      df = df.query("isVisaIncluded") 

    # --- Star rating ---
    available_stars = sorted(df['stars'].dropna().unique().tolist())
    selected_stars = st.sidebar.multiselect(
        "Star rating",
        options=available_stars,
        default=available_stars,
        format_func=lambda x: f"{'⭐' * int(x)} ({int(x)} star)"
    )
    if selected_stars:
        df = df[df['stars'].isin(selected_stars)]

    # --- Max distance to Haram ---
    makkah_max_dist = st.sidebar.number_input(
        "Max Makkah hotel distance to Haram (metres)",
        min_value=0,
        max_value=10_000,
        value=10_000,
        step=100,
        help="Only include packages where the Makkah hotel distance is known AND within this limit."
    )
    madinah_max_dist =  st.sidebar.number_input(
        "Max Makkah hotel distance to Masjid Al-Nabawi (metres)",
        min_value=0,
        max_value=10_000,
        value=10_000,
        step=100,
        help="Only include packages where the Madinah hotel distance is known AND within this limit."
    )
    apply_makkah_dist_filter = st.sidebar.checkbox("Apply Makkah distance filter", value=False)
    apply_madinah_dist_filter = st.sidebar.checkbox("Apply Madinah distance filter", value=False)

    if apply_makkah_dist_filter:
        df = df[df['makkah_distanceToHaram'].notna() & (df['makkah_distanceToHaram'] <= makkah_max_dist)]
    
    if apply_madinah_dist_filter:
        df = df[df['madinah_distanceToHaram'].notna() & (df['madinah_distanceToHaram'] <= madinah_max_dist)]

    # --- Exclude companies ---
    all_companies = sorted(df['company'].dropna().unique().tolist())
    excluded = st.sidebar.multiselect("Exclude companies", options=all_companies, default=[])
    if excluded:
        df = df[~df['company'].isin(excluded)]

    return df

def show_piechart(df: pd.DataFrame):
    st.subheader("◔ Datastore demographic by company")

    companyCounts = df['company'].value_counts().reset_index()
    companyCounts['percent'] = companyCounts['count'] / companyCounts['count'].sum()
    chart = (alt.Chart(companyCounts).mark_arc()
             .encode(theta=alt.Theta(field="count", type="quantitative"),
                    color=alt.Color(field="company", type="nominal", scale=alt.Scale(domain=list(companyCounts['company']), scheme='tableau20')),
                    tooltip=[alt.Tooltip('company:N'), alt.Tooltip('count:Q'), alt.Tooltip('percent:Q', format='.1%')]))



    st.altair_chart(chart, width='stretch', theme='streamlit')
  

def show_avg_ppp_bar(df: pd.DataFrame):
    st.subheader("📊 Average price per person by company")

    has_ppp = df[df['ppp'].notna()]
    if has_ppp.empty:
        st.info("No packages with price data match the current filters.")
        return

    avg_ppp = (
        has_ppp.groupby('company')['ppp']
        .mean()
        .reset_index()
        .rename(columns={'ppp': 'avg_ppp'})
        .sort_values('avg_ppp', ascending=False)
    )

    chart = (
        alt.Chart(avg_ppp)
        .mark_bar()
        .encode(
            x=alt.X('company:N', sort='-y', title='Company'),
            y=alt.Y('avg_ppp:Q', title='Avg price per person (£)'),
            tooltip=['company', alt.Tooltip('avg_ppp:Q', format=',.0f', title='Avg PPP (£)')]
        )
        .properties(height=400)
    )
    st.altair_chart(chart, width='stretch', theme="streamlit")
    st.caption(f"Based on {len(has_ppp)} packages with price data out of {len(df)} filtered packages.")

def show_distance_vs_ppp_scatter(df: pd.DataFrame):
    st.subheader("📍 Distance to Haram vs Price per person")

    makkah_df = (
        df[df['ppp'].notna() & df['makkah_distanceToHaram'].notna()]
        .assign(
            distance_m=df['makkah_distanceToHaram'],
            name=df['makkah_name'],
            city='Makkah hotel'
        )[['ppp', 'distance_m', 'company', 'stars', 'isShifting', 'name', 'city']]
    )

    madinah_df = (
        df[df['ppp'].notna() & df['madinah_distanceToHaram'].notna()]
        .assign(
            distance_m=df['madinah_distanceToHaram'],
            name=df['madinah_name'],
            city='Madinah hotel'
        )[['ppp', 'distance_m', 'company', 'stars', 'isShifting', 'name', 'city']]
    )

    scatter_df = pd.concat([makkah_df, madinah_df], ignore_index=True)

    if scatter_df.empty:
        st.info("No packages with both price and distance data match the current filters.")
        return

    chart = (
        alt.Chart(scatter_df)
        .mark_circle(size=80, opacity=0.7)
        .encode(
            x=alt.X('distance_m:Q', title='Distance to Haram (metres)'),
            y=alt.Y('ppp:Q', title='Price per person (£)'),
            color=alt.Color(
                'city:N',
                scale=alt.Scale(
                    domain=['Makkah hotel', 'Madinah hotel'],
                    range=['#2563EB', '#DC2626']
                )
            ),
            tooltip=[
                'company',
                alt.Tooltip('ppp:Q', format=',.0f', title='PPP (£)'),
                alt.Tooltip('distance_m:Q', title='Distance (m)'),
                'stars',
                'isShifting',
                'name',
                'city'
            ]
        )
        .properties(height=450)
    )

    st.altair_chart(chart, width='stretch', theme='streamlit')

    st.caption(
        f"Showing {len(makkah_df)} Makkah data-points and {len(madinah_df)} Madinah data-points."
    )


def main():
  st.set_page_config(page_title="Hajj Package Dashboard", layout="wide")
  st.title("🕋 Hajj Package Dashboard")

  df, err = loadData(queryName)
  if err is not None:
      st.error(f"Error loading data from S3: {err}")
      return

  # df = parse_data(df_raw)
  df_filtered = apply_package_filters(df)

  show_piechart(df_filtered)
  st.divider()
  show_avg_ppp_bar(df_filtered)
  st.divider()
  show_distance_vs_ppp_scatter(df_filtered)


if __name__ == "__main__":
    main()