#!/usr/bin/env python3
import requests
import pandas as pd
from io import StringIO
import sys

def extract_oecd_data(dataset_id, filters=None, start_period=None, end_period=None):
    """Extract OECD data and print results"""
    
    base_url = "https://sdmx.oecd.org/public/rest/data/"
    url = f"{base_url}{dataset_id}"
    
    if filters:
        url += f"/{filters}"
    
    params = {
        'dimensionAtObservation': 'AllDimensions',
        'format': 'csvfilewithlabels'
    }
    
    if start_period:
        params['startPeriod'] = start_period
    if end_period:
        params['endPeriod'] = end_period
    
    try:
        print(f"🔄 Fetching data from OECD API...")
        print(f"📊 Dataset: {dataset_id}")
        print(f"🔗 URL: {url}")
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        df = pd.read_csv(StringIO(response.text))
        
        print(f"✅ Successfully extracted {len(df)} records")
        print(f"📈 Dataset shape: {df.shape}")
        print(f"📋 Columns: {list(df.columns)}")
        print("\n" + "="*50)
        print("📊 FIRST 10 ROWS:")
        print("="*50)
        print(df.head(10).to_string())
        
        if len(df) > 10:
            print(f"\n... and {len(df) - 10} more rows")
        
        return df
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching data: {e}")
        return None
    except Exception as e:
        print(f"❌ Error processing data: {e}")
        return None

def main():
    print("🌍 OECD Data Extractor")
    print("="*30)
    
    # Example 1: GDP data
    print("\n1️⃣ Extracting GDP Data...")
    gdp_data = extract_oecd_data(
        dataset_id="OECD.SDD.NAD,DSD_NAAG@DF_NAAG_I",
        filters=".A..........",
        start_period="2020"
    )
    
    # Example 2: Composite Leading Indicators
    print("\n2️⃣ Extracting Composite Leading Indicators...")
    cli_data = extract_oecd_data(
        dataset_id="OECD.SDD.STES,DSD_STES@DF_CLI",
        filters=".M.LI...AA...H",
        start_period="2023-01"
    )
    
    print("\n🎉 Extraction complete!")

if __name__ == "__main__":
    main()
