#!/usr/bin/env python3
"""
Optimized Health KPI Data Extraction System
Supports WHO GHO, World Bank, and OECD databases
"""

import requests
import pandas as pd
from io import StringIO
import json
import time
from typing import Dict, List, Optional

class HealthKPIExtractor:
    def __init__(self):
        # Combined WHO GHO KPIs (includes both WHO and WHO GHO indicators)
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
            "Age-standardized DALYs, diabetes mellitus, per 100,000": "SA_0000001421"
            #https://ghoapi.azureedge.net/api/Indicator
            #"Tobacco use (age 15+, %)": "M_Est_tob_smk_curr",
            #"Fruit & vegetable intake (less than 5 servings)": "NCD_FRTVG",
            #"Alcohol consumption (liters per capita)": "SA_0000001400",
            #"TB incidence (per 100k)": "TB_1",
            #"HIV incidence (per 1,000)": "HIV_0000000026",
            #"Hepatitis B prevalence": "WHS4_128",
            #"Malaria incidence (per 1,000)": "MALARIA_EST_INCIDENCE",
            #"Physicians per 1,000 people": "HWF_0001",
            #"Nurses and midwives per 1,000": "HWF_0002",
            #"Pharmacists per 1,000": "HWF_0003",
            #"Health workforce density (SDG 3.c.1)": "SDG_HWF_DENSITY",
            #"Hospital beds per 1,000 people": "WHS6_102",
            #"IHR core capacity score": "IHR_CAPACITY",
            #"Number of surveillance and response systems in place": "SURVEILLANCE_SYSTEMS",
            #"Health emergency response index (country self-assessed)": "EMERGENCY_RESPONSE"
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

        
        # Unified country code mapping (ISO 3-letter codes)
        self.country_codes = {
            "afghanistan": "AFG", "albania": "ALB", "algeria": "DZA", "argentina": "ARG",
            "armenia": "ARM", "australia": "AUS", "austria": "AUT", "azerbaijan": "AZE",
            "bangladesh": "BGD", "belgium": "BEL", "brazil": "BRA", "bulgaria": "BGR",
            "canada": "CAN", "chile": "CHL", "china": "CHN", "colombia": "COL",
            "denmark": "DNK", "egypt": "EGY", "finland": "FIN", "france": "FRA",
            "germany": "DEU", "ghana": "GHA", "greece": "GRC", "india": "IND",
            "indonesia": "IDN", "iran": "IRN", "iraq": "IRQ", "ireland": "IRL",
            "israel": "ISR", "italy": "ITA", "japan": "JPN", "jordan": "JOR",
            "kenya": "KEN", "south korea": "KOR", "malaysia": "MYS", "mexico": "MEX",
            "netherlands": "NLD", "nigeria": "NGA", "norway": "NOR", "pakistan": "PAK",
            "poland": "POL", "portugal": "PRT", "russia": "RUS", "saudi arabia": "SAU",
            "south africa": "ZAF", "spain": "ESP", "sweden": "SWE", "switzerland": "CHE",
            "thailand": "THA", "turkey": "TUR", "ukraine": "UKR", "united kingdom": "GBR",
            "united states": "USA", "vietnam": "VNM"
        }
        
        # API base URLs
        self.api_urls = {
            "WHO_GHO": "https://ghoapi.azureedge.net/api/",
            "WORLD_BANK": "https://api.worldbank.org/v2/",
            "OECD": "https://sdmx.oecd.org/public/rest/data/"
        }
    
    def get_country_input(self) -> str:
        """Get country input from user"""
        country = input("🏳️ Enter country name: ").lower().strip()
        return self.country_codes.get(country, country.upper())
    
    def display_kpis_and_get_selection(self) -> Dict[str, List[str]]:
        """Display all KPIs and get user selection"""
        all_kpis = {}
        counter = 1
        
        print("\n📊 Available Health KPIs:")
        print("=" * 60)
        
        # WHO GHO KPIs
        print(f"\n🏥 WHO GHO Indicators ({len(self.who_gho_kpis)} available):")
        for kpi in self.who_gho_kpis:
            print(f"{counter:2d}. {kpi}")
            all_kpis[counter] = ("WHO_GHO", kpi)
            counter += 1
        
        # World Bank KPIs
        print(f"\n🌍 World Bank Indicators ({len(self.world_bank_kpis)} available):")
        for kpi in self.world_bank_kpis:
            print(f"{counter:2d}. {kpi}")
            all_kpis[counter] = ("WORLD_BANK", kpi)
            counter += 1
        
        # OECD KPIs
        print(f"\n💼 OECD Indicators ({len(self.oecd_kpis)} available):")
        for kpi in self.oecd_kpis:
            print(f"{counter:2d}. {kpi}")
            all_kpis[counter] = ("OECD", kpi)
            counter += 1
        
        # Get user selection
        selection = input(f"\n📝 Select KPIs (1-{counter-1}), e.g., '1,2,3': ").strip()
        selected_numbers = [int(x.strip()) for x in selection.split(',')]
        
        selected_kpis = {"WHO_GHO": [], "WORLD_BANK": [], "OECD": []}
        
        for num in selected_numbers:
            if num in all_kpis:
                db, kpi = all_kpis[num]
                selected_kpis[db].append(kpi)
        
        return selected_kpis
    
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
            
            if not records:
                print(f"❌ Data unavailable for that KPI: {kpi_name}")
                return pd.DataFrame()
            
            return pd.DataFrame(records)
            
        except Exception as e:
            print(f"❌ Data unavailable for that KPI: {kpi_name} - Error: {e}")
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
            
            if not records:
                print(f"❌ Data unavailable for that KPI: {kpi_name}")
                return pd.DataFrame()
            
            return pd.DataFrame(records)
            
        except Exception as e:
            print(f"❌ Data unavailable for that KPI: {kpi_name} - Error: {e}")
            return pd.DataFrame()
    
    def extract_oecd_data(self, country_code: str, kpi_name: str, indicator_code: str) -> pd.DataFrame:
        """Extract data from OECD API using correct health protection dataset"""
        
        try:
            # Use the healthcare coverage dataset
            if "insurance" in kpi_name.lower():
                dataset = "OECD.ELS.HD,DSD_HEALTH_PROT@DF_HEALTH_PROT"
                url = f"{self.api_urls['OECD']}{dataset}/{country_code}.{indicator_code}.._T"
            else:
                # Use health statistics for other indicators
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
            
            if not records:
                print(f"❌ Data unavailable for that KPI: {kpi_name}")
                return pd.DataFrame()
            
            return pd.DataFrame(records)
            
        except Exception as e:
            print(f"❌ Data unavailable for that KPI: {kpi_name} - Error: {e}")
            return pd.DataFrame()

    
    def extract_all_data(self, country_code: str, selected_kpis: Dict[str, List[str]]) -> pd.DataFrame:
        """Extract all selected KPI data"""
        all_data = []
        
        print(f"\n🔄 Extracting data for country: {country_code}")
        print("=" * 50)
        
        # Extract WHO GHO data
        if selected_kpis["WHO_GHO"]:
            print(f"📊 Extracting {len(selected_kpis['WHO_GHO'])} WHO GHO indicators...")
            for kpi in selected_kpis["WHO_GHO"]:
                indicator_code = self.who_gho_kpis[kpi]
                data = self.extract_who_gho_data(country_code, kpi, indicator_code)
                if not data.empty:
                    all_data.append(data)
                time.sleep(0.5)  # Rate limiting
        
        # Extract World Bank data
        if selected_kpis["WORLD_BANK"]:
            print(f"🌍 Extracting {len(selected_kpis['WORLD_BANK'])} World Bank indicators...")
            for kpi in selected_kpis["WORLD_BANK"]:
                indicator_code = self.world_bank_kpis[kpi]
                data = self.extract_world_bank_data(country_code, kpi, indicator_code)
                if not data.empty:
                    all_data.append(data)
                time.sleep(0.5)  # Rate limiting
        
        # Extract OECD data
        if selected_kpis["OECD"]:
            print(f"💼 Extracting {len(selected_kpis['OECD'])} OECD indicators...")
            for kpi in selected_kpis["OECD"]:
                indicator_code = self.oecd_kpis[kpi]
                data = self.extract_oecd_data(country_code, kpi, indicator_code)
                if not data.empty:
                    all_data.append(data)
                time.sleep(0.5)  # Rate limiting
        
        # Combine all data
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            combined_df = combined_df.sort_values(['KPI', 'Year'])
            return combined_df
        else:
            return pd.DataFrame()
    
    def display_comprehensive_table(self, df: pd.DataFrame, country_code: str):
        """Display all data in one comprehensive table in terminal"""
        if df.empty:
            print("❌ No data found for the selected criteria.")
            return
        
        print(f"\n📈 COMPREHENSIVE HEALTH KPI DATA FOR {country_code}")
        print("=" * 100)
        
        # Summary statistics
        print(f"📊 Total records: {len(df)}")
        print(f"📅 Year range: {df['Year'].min()} - {df['Year'].max()}")
        print(f"🏥 KPIs covered: {df['KPI'].nunique()}")
        print(f"🔗 Data sources: {', '.join(df['Source'].unique())}")
        
        # Create pivot table for comprehensive view
        pivot_df = df.pivot_table(
            index='KPI', 
            columns='Year', 
            values='Value', 
            aggfunc='first'
        )
        
        # Display the comprehensive table
        print(f"\n📋 COMPREHENSIVE DATA TABLE:")
        print("=" * 100)
        
        # Format the table for better display
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', 50)
        
        print(pivot_df.to_string())
        
        # Additional detailed view by source
        print(f"\n📊 DATA BY SOURCE:")
        print("=" * 100)
        
        for source in df['Source'].unique():
            source_data = df[df['Source'] == source]
            print(f"\n🔸 {source} ({len(source_data)} records)")
            
            source_pivot = source_data.pivot_table(
                index='KPI', 
                columns='Year', 
                values='Value', 
                aggfunc='first'
            )
            
            print(source_pivot.to_string())
        
        # Save to CSV
        filename = f"health_kpis_{country_code}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False)
        print(f"\n💾 Data saved to: {filename}")
        
        # Reset pandas display options
        pd.reset_option('display.max_columns')
        pd.reset_option('display.max_rows')
        pd.reset_option('display.width')
        pd.reset_option('display.max_colwidth')
    
    def run(self):
        """Main execution function"""
        print("🏥 HEALTH KPI DATA EXTRACTION SYSTEM")
        print("=" * 50)
        
        # Get country selection
        country_code = self.get_country_input()
        print(f"✅ Selected country: {country_code}")
        
        # Get KPI selection
        selected_kpis = self.display_kpis_and_get_selection()
        
        # Show selection summary
        total_selected = sum(len(kpis) for kpis in selected_kpis.values())
        print(f"\n✅ Selected {total_selected} KPIs:")
        for db, kpis in selected_kpis.items():
            if kpis:
                print(f"  {db}: {len(kpis)} indicators")
        
        # Extract data
        df = self.extract_all_data(country_code, selected_kpis)
        
        # Display comprehensive table
        self.display_comprehensive_table(df, country_code)

# Main execution
if __name__ == "__main__":
    try:
        extractor = HealthKPIExtractor()
        extractor.run()
    except KeyboardInterrupt:
        print("\n\n👋 Extraction cancelled by user.")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
