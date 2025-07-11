import streamlit as st
import requests
import pandas as pd
from io import StringIO
import time
from typing import Dict, List
import plotly.express as px
import plotly.graph_objects as go

class HealthKPIExtractor:
    def __init__(self):
        # Combined WHO GHO KPIs
        self.who_gho_kpis = {
            "% births attended by skilled health personnel": "MDG_0000000025",
            "Coverage of essential health services (UHC index)": "XX",
            "DTP3 immunization coverage (%)": "WHS4_100",
            "Current health expenditure (% of GDP)": "GHED_CHEGDP_SHA2011",
            "Per capita health expenditure (USD)": "GHED_CHE_pc_US_SHA2011",
            "Out-of-pocket health spending (% of total)": "SDGOOP",
            "Domestic general government health expenditure (GGHE-D) as percentage of GDP": "GHED_GGHE-DCHE_SHA2011",
            "Prevalence of overweight and obesity": "EQ_OVERWEIGHTADULT",
            "Raised blood pressure (SBP>=140 OR DBP>=90) (age-standardized estimate)": "BP_04",
            "Age-standardized DALYs, diabetes mellitus, per 100,000": "SA_0000001421",
            #https://ghoapi.azureedge.net/api/Indicator
            "Estimate of current tobacco use prevalence (%)": "M_Est_tob_curr",
            #"Fruit & vegetable intake (less than 5 servings)": "NCD_FRTVG",
            "Alcohol, recorded per capita (15+) consumption (in litres of pure alcohol), by beverage type": "SA_0000001400",
            "Estimated number of MDR/RR-TB incident cases": "TB_e_inc_rr_num",
            "Estimated number of people (all ages) living with HIV": "HIV_0000000001",
            "Hepatitis B surface antigen (HBsAg) prevalence (%)": "SDGHEPHBSAGPRV",
            "Malaria incidence (per 1 000 population at risk)": "SDGMALARIA",
            "Physicians density (per 1000 population)": "HRH_33",
            "Nursing and midwifery personnel density (per 1000 population)": "HRH_24",
            "Pharmacists  (per 10,000)": "HWF_0014",
            #"Health workforce density (SDG 3.c.1)": "SDG_HWF_DENSITY",
            "Hospital beds per 1,000 people": "WHS6_102",
            #"IHR core capacity score": "IHR_CAPACITY",
            #"Number of surveillance and response systems in place": "SURVEILLANCE_SYSTEMS",
            "Response": "IHR04"
        }
        
        self.world_bank_kpis = {
            "% population with access to basic sanitation": "SH.STA.BASS.ZS",
            "Life expectancy at birth": "SP.DYN.LE00.IN",
            "Under-5 mortality rate (per 1,000)": "SH.DYN.MORT",
            "Maternal mortality ratio (per 100,000)": "SH.STA.MMRT",
            "Infant mortality rate (per 1,000)": "SP.DYN.IMRT.IN",
            "Neonatal mortality rate": "SH.DYN.NMRT",
            "Suicide mortality rate": "SH.STA.SUIC.P5"
        }
        
        self.oecd_kpis = {
            "Unmet need for medical care (% reporting delay or avoidance)": "UNMET_NEED_MED_CARE",
            "% population with health insurance": "HEALTH_INSURANCE_COV",
            "Expenditure on pharmaceuticals per capita": "PHARM_EXP_PC_USD",
            "Expenditure on inpatient care (% of total)": "INPATIENT_CARE_SHARE",
            "Preventive care spending (% of total health spending)": "PREVENT_CARE_SHARE",
            "ICU beds per 100,000 (select countries)": "ICU_BEDS_PER_100K",
            "Medical technology density (MRI/CT scanners per million)": "MED_TECH_DENSITY",
            "Hospital beds by function of healthcare": "HOSP_BEDS_FUNC"
        }
        
        # Country mapping with full names for display
        self.countries = {
            "Afghanistan": "AFG", "Albania": "ALB", "Algeria": "DZA", "Argentina": "ARG",
            "Armenia": "ARM", "Australia": "AUS", "Austria": "AUT", "Azerbaijan": "AZE",
            "Bangladesh": "BGD", "Belgium": "BEL", "Brazil": "BRA", "Bulgaria": "BGR",
            "Canada": "CAN", "Chile": "CHL", "China": "CHN", "Colombia": "COL",
            "Denmark": "DNK", "Egypt": "EGY", "Finland": "FIN", "France": "FRA",
            "Germany": "DEU", "Ghana": "GHA", "Greece": "GRC", "India": "IND",
            "Indonesia": "IDN", "Iran": "IRN", "Iraq": "IRQ", "Ireland": "IRL",
            "Israel": "ISR", "Italy": "ITA", "Japan": "JPN", "Jordan": "JOR",
            "Kenya": "KEN", "South Korea": "KOR", "Malaysia": "MYS", "Mexico": "MEX",
            "Netherlands": "NLD", "Nigeria": "NGA", "Norway": "NOR", "Pakistan": "PAK",
            "Poland": "POL", "Portugal": "PRT", "Russia": "RUS", "Saudi Arabia": "SAU",
            "South Africa": "ZAF", "Spain": "ESP", "Sweden": "SWE", "Switzerland": "CHE",
            "Thailand": "THA", "Turkey": "TUR", "Ukraine": "UKR", "United Kingdom": "GBR",
            "United States": "USA", "Vietnam": "VNM"
        }
        
        # API base URLs
        self.api_urls = {
            "WHO_GHO": "https://ghoapi.azureedge.net/api/",
            "WORLD_BANK": "https://api.worldbank.org/v2/",
            "OECD": "https://sdmx.oecd.org/public/rest/data/"
        }

    def extract_who_gho_data(self, country_code: str, kpi_name: str, indicator_code: str) -> pd.DataFrame:
        """Extract data from WHO GHO API"""
        url = f"{self.api_urls['WHO_GHO']}{indicator_code}"
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            records = []
            if 'value' in data:
                for item in data['value']:
                    if item.get('SpatialDim') == country_code:
                        year = item.get('TimeDim')
                        if year and int(year) >= 2015:
                            records.append({
                                'Year': int(year),
                                'Country': country_code,
                                'KPI': kpi_name,
                                'Value': item.get('NumericValue'),
                                'Source': 'WHO GHO'
                            })
            
            return pd.DataFrame(records) if records else pd.DataFrame()
            
        except Exception as e:
            st.warning(f"Data unavailable for {kpi_name}: {str(e)}")
            return pd.DataFrame()

    def extract_world_bank_data(self, country_code: str, kpi_name: str, indicator_code: str) -> pd.DataFrame:
        """Extract data from World Bank API"""
        url = f"{self.api_urls['WORLD_BANK']}country/{country_code}/indicator/{indicator_code}"
        params = {
            'format': 'json',
            'date': '2015:2024',
            'per_page': 100
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            records = []
            if len(data) > 1 and data[1]:
                for item in data[1]:
                    if item.get('value') is not None:
                        records.append({
                            'Year': int(item['date']),
                            'Country': country_code,
                            'KPI': kpi_name,
                            'Value': item['value'],
                            'Source': 'World Bank'
                        })
            
            return pd.DataFrame(records) if records else pd.DataFrame()
            
        except Exception as e:
            st.warning(f"Data unavailable for {kpi_name}: {str(e)}")
            return pd.DataFrame()

    def extract_oecd_data(self, country_code: str, kpi_name: str, indicator_code: str) -> pd.DataFrame:
        """Extract data from OECD API"""
        try:
            if "insurance" in kpi_name.lower():
                dataset = "OECD.ELS.HD,DSD_HEALTH_PROT@DF_HEALTH_PROT"
                url = f"{self.api_urls['OECD']}{dataset}/{country_code}.{indicator_code}.._T"
            else:
                dataset = "OECD.ELS.HD,DSD_HEALTH_STAT@DF_HEALTH_STAT"
                url = f"{self.api_urls['OECD']}{dataset}/{country_code}.{indicator_code}.._T"
            
            params = {
                'startPeriod': '2015',
                'endPeriod': '2024',
                'dimensionAtObservation': 'AllDimensions',
                'format': 'csvfilewithlabels'
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            df = pd.read_csv(StringIO(response.text))
            
            records = []
            for _, row in df.iterrows():
                if pd.notna(row.get('OBS_VALUE')):
                    year = row.get('TIME_PERIOD')
                    if year and int(year) >= 2015:
                        records.append({
                            'Year': int(year),
                            'Country': country_code,
                            'KPI': kpi_name,
                            'Value': row['OBS_VALUE'],
                            'Source': 'OECD'
                        })
            
            return pd.DataFrame(records) if records else pd.DataFrame()
            
        except Exception as e:
            st.warning(f"Data unavailable for {kpi_name}: {str(e)}")
            return pd.DataFrame()

    def extract_data_for_countries(self, country_codes: List[str], selected_kpis: Dict[str, List[str]]) -> pd.DataFrame:
        """Extract data for multiple countries and KPIs"""
        all_data = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_operations = len(country_codes) * (
            len(selected_kpis.get("WHO_GHO", [])) + 
            len(selected_kpis.get("WORLD_BANK", [])) + 
            len(selected_kpis.get("OECD", []))
        )
        
        current_operation = 0
        
        for country_code in country_codes:
            country_name = [k for k, v in self.countries.items() if v == country_code][0]
            status_text.text(f"Extracting data for {country_name}...")
            
            # Extract WHO GHO data
            for kpi in selected_kpis.get("WHO_GHO", []):
                indicator_code = self.who_gho_kpis[kpi]
                data = self.extract_who_gho_data(country_code, kpi, indicator_code)
                if not data.empty:
                    all_data.append(data)
                current_operation += 1
                progress_bar.progress(current_operation / total_operations)
                time.sleep(0.1)  # Rate limiting
            
            # Extract World Bank data
            for kpi in selected_kpis.get("WORLD_BANK", []):
                indicator_code = self.world_bank_kpis[kpi]
                data = self.extract_world_bank_data(country_code, kpi, indicator_code)
                if not data.empty:
                    all_data.append(data)
                current_operation += 1
                progress_bar.progress(current_operation / total_operations)
                time.sleep(0.1)  # Rate limiting
            
            # Extract OECD data
            for kpi in selected_kpis.get("OECD", []):
                indicator_code = self.oecd_kpis[kpi]
                data = self.extract_oecd_data(country_code, kpi, indicator_code)
                if not data.empty:
                    all_data.append(data)
                current_operation += 1
                progress_bar.progress(current_operation / total_operations)
                time.sleep(0.1)  # Rate limiting
        
        progress_bar.empty()
        status_text.empty()
        
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            combined_df = combined_df.sort_values(['Country', 'KPI', 'Year'])
            return combined_df
        else:
            return pd.DataFrame()

def main():
    st.set_page_config(
        page_title="Health KPI Dashboard",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🏥 Health KPI Data Extraction Dashboard")
    st.markdown("**Extract and analyze health indicators from WHO GHO, World Bank, and OECD databases**")
    
    # Initialize the extractor
    extractor = HealthKPIExtractor()
    
    # Sidebar for selections
    st.sidebar.header("📊 Data Selection")
    
    # Country selection
    st.sidebar.subheader("🌍 Select Countries")
    selected_countries = st.sidebar.multiselect(
        "Choose countries to analyze:",
        options=list(extractor.countries.keys()),
        default=["India", "United States", "Germany"],
        help="Select one or more countries for comparison"
    )
    
    # KPI selection by source
    st.sidebar.subheader("📈 Select Health Indicators")
    
    selected_kpis = {"WHO_GHO": [], "WORLD_BANK": [], "OECD": []}
    
    # WHO GHO KPIs
    with st.sidebar.expander("🏥 WHO GHO Indicators", expanded=True):
        for kpi in extractor.who_gho_kpis.keys():
            if st.checkbox(kpi, key=f"who_{kpi}"):
                selected_kpis["WHO_GHO"].append(kpi)
    
    # World Bank KPIs
    with st.sidebar.expander("🌍 World Bank Indicators", expanded=True):
        for kpi in extractor.world_bank_kpis.keys():
            if st.checkbox(kpi, key=f"wb_{kpi}"):
                selected_kpis["WORLD_BANK"].append(kpi)
    
    # OECD KPIs
    with st.sidebar.expander("💼 OECD Indicators", expanded=True):
        for kpi in extractor.oecd_kpis.keys():
            if st.checkbox(kpi, key=f"oecd_{kpi}"):
                selected_kpis["OECD"].append(kpi)
    
    # Extract data button
    if st.sidebar.button("🔄 Extract Data", type="primary"):
        if not selected_countries:
            st.error("Please select at least one country.")
            return
        
        total_kpis = sum(len(kpis) for kpis in selected_kpis.values())
        if total_kpis == 0:
            st.error("Please select at least one KPI.")
            return
        
        # Convert country names to codes
        country_codes = [extractor.countries[country] for country in selected_countries]
        
        # Extract data
        with st.spinner("Extracting health data..."):
            df = extractor.extract_data_for_countries(country_codes, selected_kpis)
        
        if df.empty:
            st.warning("No data found for the selected criteria.")
            return
        
        # Store data in session state
        st.session_state.health_data = df
        st.session_state.selected_countries = selected_countries
        st.success(f"✅ Successfully extracted {len(df)} records!")
    
    # Display results if data exists
    if 'health_data' in st.session_state:
        df = st.session_state.health_data
        countries = st.session_state.selected_countries
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Records", len(df))
        with col2:
            st.metric("Countries", df['Country'].nunique())
        with col3:
            st.metric("KPIs", df['KPI'].nunique())
        with col4:
            st.metric("Year Range", f"{df['Year'].min()}-{df['Year'].max()}")
        
        # Tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview Table", "📈 By Country", "🏥 By Source", "📋 Raw Data"])
        
        with tab1:
            st.subheader("📊 Comprehensive Health KPI Overview")
            
            # Create pivot table
            pivot_df = df.pivot_table(
                index='KPI',
                columns=['Country', 'Year'],
                values='Value',
                aggfunc='first'
            )
            
            # Display pivot table
            st.dataframe(
                pivot_df,
                use_container_width=True,
                height=600
            )
            
            # Download button
            csv = pivot_df.to_csv()
            st.download_button(
                label="📥 Download Overview Table",
                data=csv,
                file_name=f"health_kpi_overview_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with tab2:
            st.subheader("📈 Data by Country")
            
            for country in countries:
                country_code = extractor.countries[country]
                country_data = df[df['Country'] == country_code]
                
                if not country_data.empty:
                    st.write(f"### 🏳️ {country}")
                    
                    # Create pivot for this country
                    country_pivot = country_data.pivot_table(
                        index='KPI',
                        columns='Year',
                        values='Value',
                        aggfunc='first'
                    )
                    
                    st.dataframe(
                        country_pivot,
                        use_container_width=True
                    )
                    
                    # Source breakdown
                    st.write("**Data Sources:**")
                    source_counts = country_data['Source'].value_counts()
                    for source, count in source_counts.items():
                        st.write(f"- {source}: {count} indicators")
        
        with tab3:
            st.subheader("🏥 Data by Source")
            
            for source in df['Source'].unique():
                source_data = df[df['Source'] == source]
                st.write(f"### 📊 {source}")
                
                source_pivot = source_data.pivot_table(
                    index='KPI',
                    columns=['Country', 'Year'],
                    values='Value',
                    aggfunc='first'
                )
                
                st.dataframe(
                    source_pivot,
                    use_container_width=True
                )
        
        with tab4:
            st.subheader("📋 Raw Data")
            st.dataframe(
                df,
                use_container_width=True,
                height=600
            )
            
            # Download raw data
            csv_raw = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Raw Data",
                data=csv_raw,
                file_name=f"health_kpi_raw_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()
