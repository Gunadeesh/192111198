from flask import Flask, jsonify
import requests
from collections import deque
import time
import logging

app = Flask(__name__)

# Configuration
WINDOW_SIZE = 10
TIMEOUT = 0.5

# Deques to maintain window of numbers
number_window = deque(maxlen=WINDOW_SIZE)

# Third-party server URL templates for different number types
THIRD_PARTY_URLS = {
    'p': "https://20.244.56.144/test/numbers/primes",
    'f': "https://20.244.56.144/test/numbers/fibo",
    'e': "https://20.244.56.144/test/numbers/even",
    'r': "https://20.244.56.144/test/numbers/rand"  # Assuming there is a random endpoint
}

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Helper function to fetch numbers
def fetch_numbers(numberid):
    url = THIRD_PARTY_URLS.get(numberid)
    if not url:
        logging.debug(f"No URL found for number ID: {numberid}")
        return []
    
    try:
        response = requests.get(url, timeout=TIMEOUT, verify=False)
        response.raise_for_status()
        numbers = response.json().get("numbers", [])
        logging.debug(f"Fetched numbers: {numbers} for number ID: {numberid}")
        return numbers
    except (requests.RequestException, ValueError) as e:
        logging.error(f"Error fetching numbers for number ID {numberid}: {e}")
        return []

# Helper function to calculate average
def calculate_average(numbers):
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)

@app.route('/numbers/<numberid>', methods=['GET'])
def get_numbers(numberid):
    start_time = time.time()
    
    # Fetch new numbers from third-party server
    new_numbers = fetch_numbers(numberid)
    
    # Ensure numbers are unique and within timeout
    unique_numbers = list(set(new_numbers))
    if time.time() - start_time > TIMEOUT:
        unique_numbers = []

    # Update the window of numbers
    prev_window_state = list(number_window)
    for num in unique_numbers:
        if num not in number_window:
            number_window.append(num)
    curr_window_state = list(number_window)

    # Calculate the average
    avg = calculate_average(curr_window_state)
    
    response = {
        "windowPrevState": prev_window_state,
        "windowCurrState": curr_window_state,
        "numbers": unique_numbers,
        "avg": avg
    }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
