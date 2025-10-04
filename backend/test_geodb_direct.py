#!/usr/bin/env python3
"""
Direct test of GeoDB API to understand the correct GraphQL schema.
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def test_geodb_schema():
    """Test different GraphQL queries to find the correct schema."""
    
    rapidapi_key = os.environ.get('RAPIDAPI_KEY')
    rapidapi_host = os.environ.get('RAPIDAPI_HOST', 'geodb-cities-graphql.p.rapidapi.com')
    
    if not rapidapi_key:
        print("❌ RAPIDAPI_KEY not found")
        return
    
    headers = {
        'x-rapidapi-key': rapidapi_key,
        'x-rapidapi-host': rapidapi_host,
        'Content-Type': 'application/json'
    }
    
    url = 'https://geodb-cities-graphql.p.rapidapi.com/'
    
    # Test 1: Simple introspection query
    print("=== Testing Schema Introspection ===")
    introspection_query = """
    query IntrospectionQuery {
      __schema {
        queryType {
          name
          fields {
            name
            type {
              name
            }
          }
        }
      }
    }
    """
    
    try:
        response = requests.post(url, json={'query': introspection_query}, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Introspection successful")
            if 'data' in data and '__schema' in data['data']:
                query_fields = data['data']['__schema']['queryType']['fields']
                print("Available query fields:")
                for field in query_fields[:10]:  # Show first 10 fields
                    print(f"  - {field['name']}")
        else:
            print(f"❌ Introspection failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Introspection error: {e}")
    
    # Test 2: Try different query patterns
    print("\n=== Testing Different Query Patterns ===")
    
    test_queries = [
        # Pattern 1: Populated places query
        {
            "name": "Populated places query",
            "query": """
            query {
              populatedPlaces(namePrefix: "Paris", first: 1) {
                edges {
                  node {
                    name
                    country {
                      name
                    }
                    population
                  }
                }
              }
            }
            """
        },
        # Pattern 2: Countries with populated places
        {
            "name": "Countries with populated places",
            "query": """
            query {
              countries(namePrefix: "France", first: 1) {
                edges {
                  node {
                    name
                    populatedPlaces(first: 3) {
                      edges {
                        node {
                          name
                          population
                        }
                      }
                    }
                  }
                }
              }
            }
            """
        },
        # Pattern 3: Simple populated places
        {
            "name": "Simple populated places",
            "query": """
            query {
              populatedPlaces(namePrefix: "Paris", first: 1) {
                edges {
                  node {
                    name
                    population
                  }
                }
              }
            }
            """
        }
    ]
    
    for test in test_queries:
        print(f"\n--- {test['name']} ---")
        try:
            response = requests.post(url, json={'query': test['query']}, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'errors' in data:
                    print(f"❌ GraphQL errors: {data['errors']}")
                else:
                    print(f"✅ Success: {json.dumps(data, indent=2)[:200]}...")
            else:
                print(f"❌ HTTP error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Request error: {e}")

if __name__ == "__main__":
    test_geodb_schema()
