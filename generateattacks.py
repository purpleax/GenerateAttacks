#!/usr/bin/env python3

import sys
import time
import random
import configparser
import requests
import urllib.parse as urlparse
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def read_config():
    """Read and parse the configuration file."""
    config = configparser.ConfigParser(interpolation=None)
    config.read('config.ini')
    return config

def get_base_url(config):
    """Retrieve the base URL from the configuration."""
    return config.get('settings', 'base_url')

def get_weighted_category(config):
    """Return a category based on the specified weights."""
    categories = config.get("categories", "categories").split(",")
    weights = [int(config.get(cat, 'weight')) for cat in categories]
    return random.choices(categories, weights, k=1)[0]

def parse_params(param_string):
    """Parse a parameter string into a dictionary, handling complex values."""
    params = {}
    for part in param_string.split('&'):
        if '=' in part:
            key, value = part.split('=', 1)  # Split on the first '=', preserving other '=' in the value
            params[key] = value
        else:
            print(f"Skipping malformed parameter: {part}")
    return params

def run_simulation(category, config, base_url):
    """Simulate traffic for a given category."""
    user_agent = config.get(category, 'user_agent')
    path = config.get(category, 'path')
    raw_params = config.get(category, 'params')
    
    try:
        params = parse_params(raw_params)  # Using the new parsing function
    except ValueError as e:
        print(f"Error parsing parameters for category {category}: {e}")
        print(f"Raw params string: '{raw_params}'")
        return  # Skip this iteration

    # URL encode each parameter value
    encoded_params = {key: urlparse.quote_plus(value) for key, value in params.items()}

    full_url = f"{base_url}{path}"

    headers = {
        "Cache-Control": "no-cache",
        "User-Agent": user_agent
    }

    response = requests.get(full_url, params=encoded_params, headers=headers, verify=False)
    print(f"Request to {category} at {full_url} with params {encoded_params}: {response.status_code} - {response.reason}")

    time.sleep(random.randint(1, 10))

def main():
    config = read_config()
    base_url = get_base_url(config)
    try:
        while True:
            selected_category = get_weighted_category(config)
            run_simulation(selected_category, config, base_url)
    except KeyboardInterrupt:
        print("Simulation stopped by user.")

if __name__ == "__main__":
    main()
