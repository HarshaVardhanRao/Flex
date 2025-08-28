#!/usr/bin/env python3
"""
Simple test script to verify technology creation functionality
"""

import requests
import json

# Test the create technology endpoint
def test_create_technology():
    url = "http://localhost:8000/create_technology/"
    
    # Test data
    test_technologies = [
        "React.js",
        "Vue.js", 
        "Angular",
        "Node.js",
        "Python",
        "Django"
    ]
    
    print("Testing technology creation endpoint...")
    
    for tech_name in test_technologies:
        data = {"name": tech_name}
        
        try:
            response = requests.post(url, 
                                   data=json.dumps(data),
                                   headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {tech_name}: {result.get('message', 'Created successfully')}")
            else:
                print(f"❌ {tech_name}: Status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {tech_name}: Connection error - {e}")

if __name__ == "__main__":
    print("Technology Creation Test")
    print("=" * 40)
    print("Make sure Django server is running on localhost:8000")
    print("=" * 40)
    test_create_technology()