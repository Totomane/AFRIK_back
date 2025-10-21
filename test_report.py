#!/usr/bin/env python3
"""
Test script for the new professional report generation.
"""
import sys
import os
sys.path.append('.')

from services.report_service import generate_report_pdf

def test_professional_report():
    """Test the new professional report generation."""
    print("🔄 Testing Professional Report Generation...")
    
    # Test configuration
    test_path = 'media/reports/test_professional_Kenya_2025_Political-Instability_Economic-Crisis.pdf'
    country = 'Kenya'
    risks = ['Political Instability', 'Economic Crisis', 'Climate Change']
    year = 2025
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(test_path), exist_ok=True)
    
    try:
        # Generate the report
        result_path = generate_report_pdf(test_path, country, risks, year)
        
        # Check if file was created
        if os.path.exists(result_path):
            file_size = os.path.getsize(result_path)
            print(f"✅ Professional report generated successfully!")
            print(f"📄 File: {result_path}")
            print(f"📊 Size: {file_size:,} bytes")
            print(f"🎯 Country: {country}")
            print(f"📅 Year: {year}")
            print(f"⚠️  Risks analyzed: {len(risks)} ({', '.join(risks)})")
            return True
        else:
            print("❌ Report file was not created")
            return False
            
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_professional_report()
    if success:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n💥 Test failed!")
    
    sys.exit(0 if success else 1)