import requests
import json

class WHODataExtractor:
    def __init__(self):
        self.base_url = "https://ghoapi.azureedge.net/api/"
    
    def get_indicator_data(self, indicator_code):
        """Fetch data for a specific indicator"""
        headers = {'Content-type': 'application/json'}
        
        response = requests.get(f"{self.base_url}{indicator_code}", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return data['value']
        else:
            print(f"Error: {response.status_code}")
            return None
    
    def print_data(self, data, limit=20):
        """Print data to terminal in a formatted way"""
        if not data:
            print("No data available")
            return
        
        print(f"\n{'Country':<15} {'Year':<8} {'Sex':<12} {'Value':<10}")
        print("-" * 50)
        
        count = 0
        for record in data:
            if record.get('SpatialDimType') == 'COUNTRY' and count < limit:
                country_code = record.get('SpatialDim', 'N/A')
                year = record.get('TimeDim', 'N/A')
                sex_code = record.get('Dim1', 'N/A')
                value = record.get('NumericValue', 'N/A')
                
                # Convert sex codes
                sex_mapping = {
                    'FMLE': 'Female',
                    'MLE': 'Male', 
                    'BTSX': 'Both Sexes'
                }
                sex = sex_mapping.get(sex_code, 'Unknown')
                
                print(f"{country_code:<15} {year:<8} {sex:<12} {value:<10}")
                count += 1
        
        print(f"\nShowing first {count} records (countries only)")

# Usage
extractor = WHODataExtractor()
print("Fetching life expectancy data...")
data = extractor.get_indicator_data('WHOSIS_000001')
extractor.print_data(data, limit=30)
