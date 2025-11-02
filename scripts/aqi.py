import requests
from datetime import datetime
import base64
import json

# Function to initialize a session and set cookies
def create_session():
    session = requests.Session()
    session.cookies.set("ccr_captcha", "SatKxsFD4Ks5z8/gqpDbu3zJTtwywNyION3Fk9qIcMnldMOMG3OEQivwpABJ+iZn2IcDNGvwaW07c9VjTS/KpTefNwNFbtx5Nu3wB/Q/5YKEwnzv4ZyekoiBlaZcFOYFNJeQF7UT0lQPU2+Fso9oPrbmwzJ+vGpgaf2A2KS/WuQPbBrj4Yx6I16+skiNa2LQzFkfCecvQh+Vs5CpuIs5AfmKFKJHPr/bsRI5lucO21I=")
    session.cookies.set("ccr_public", "LAWomVSVWHy9pDHi4Q1EXD8+1/w4xnn7p0s0BBWknFUGl/RF7CSbH7Du1TslrFTxWnKPxyCKvc2Cqj7B5xe1eNHY41+eDVHXDVzm+oJmFLsZrFcpusZTzbFbOFoaPD4njzHYllsJrbW435oB1vsJEZxI3sb1/E7Nul41W1nAcrC5RJ+uNonTMlBiyjJncg77gFX5AkQEQC4v/8GEZioFZpRKHWEl9fLSZNHGBcitKHa9kwYhc3DdSxm5aHwNAAbVdNFhsCyeSx9ufSK5a7DkcESYKuuREUOrKVKRgDFI92OkQGQzgH4E1nbC+gReX6hp", domain="airquality.cpcb.gov.in")
    return session

# Function to send the POST request and get the base64-encoded response
def send_request(session, url, data, headers):
    response = session.post(url, headers=headers, data=data)
    return response.text  # This will be the base64-encoded response

# Function to decode the base64 response and parse it into JSON
def decode_base64_and_parse(json_base64):
    try:
        # Step 1: Decode base64 data
        decoded_data = base64.b64decode(json_base64)

        # Step 2: Convert the decoded data into a string
        decoded_string = decoded_data.decode('utf-8')

        # Step 3: Parse the string into a JSON object
        json_data = json.loads(decoded_string)

        return json_data

    except (base64.binascii.Error, json.JSONDecodeError) as e:
        print(f"Error decoding or parsing the data: {e}")
        return None


def encode_to_base64(data: dict) -> str:
    """
    Encodes a dictionary into a base64-encoded string.

    Args:
        data (dict): The dictionary to be encoded.

    Returns:
        str: The base64-encoded string.
    """
    # Convert the dictionary to a JSON string
    json_string = json.dumps(data)

    # Encode the JSON string to bytes and then to base64
    base64_encoded = base64.b64encode(json_string.encode('utf-8'))

    # Decode the base64 bytes to get the string representation
    base64_string = base64_encoded.decode('utf-8')

    return base64_string

# Function to extract and format AQI data for display
def extract_aqi_data(json_data, city):
    result = ""
    if json_data["down"] == "true": return f"{city} sensor is down."
    if json_data:
        try:
            title = city
            chart_data = json_data["chartData"][0]
            aqi_data = []
            try: min_ppm = json_data['metrics'][0]["min"]
            except: min_ppm = "-"
            try: max_ppm = json_data['metrics'][0]["max"]
            except: max_ppm = "-"

            # Collect the last 3 valid AQI readings
            r = -1
            while len(aqi_data) < 3 and abs(r) <= len(chart_data):
                try:
                    # Try to get the AQI data
                    last = chart_data[r]
                    if last[1] is not None:  # Skip None values
                        aqi_data.append((last[0], last[1]))
                except IndexError:
                    break  # Stop if there are less than 3 data points

                r -= 1  # Move to the previous data point

            # Check if we collected 3 valid data points
            if len(aqi_data) >= 3:
                # Find min and max PM2.5
                result = f"{title} [{min_ppm} - {max_ppm}] \n\t {aqi_data[0][0]} : {aqi_data[0][1]} \n\t {aqi_data[1][0]} : {aqi_data[1][1]} \n\t {aqi_data[2][0]} : {aqi_data[2][1]}"
            else:
                result = f"{title} - Not enough data points available."
        except KeyError:
            result = f"Error: Missing expected keys in JSON data for {city}."
    else:
        result = f"No data available for {city}."
    
    return result

# Main function to tie everything together
def main(url, data, headers, city):
    # Create a session
    session = create_session()

    # Send the POST request and get the base64-encoded response
    base64_response = send_request(session, url, data, headers)

    # Decode the base64 response and parse it into JSON
    json_data = decode_base64_and_parse(base64_response)
    # Extract AQI data for the specified city and return the raw string
    raw_string = extract_aqi_data(json_data, city)
    return raw_string

def post(title, data, priority = "default", tags = "", link = None):
    title = title.replace("\r", "").replace("\t", "").replace("\n", "")
    data = data.replace("\r", "").replace("\t", "")
    headers = {"Title": title, "Priority": priority}
    if tags: headers.update({"Tags": tags})
    if link: headers.update({ "Click": link}) #"Attach": link,

    requests.post("https://ntfy.sh/kaptaan",
        data=data.encode("latin-1", "ignore").strip().decode(errors = "ignore"),
        headers=headers)

def AI_AQI(city):
    url = f'https://www.iqair.com/search-results.data?q={city}&filter=aqi&_routes=routes%2F%24%28locale%29.search-results'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:144.0) Gecko/20100101 Firefox/144.0',
        'Accept': '*/*',
        'Accept-Language': 'en-GB,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Referer': 'https://www.iqair.com/india/haryana/',
        'sentry-trace': '5fbf047d4468407e95b8af4cc051a029-8da055d92fbd9559-0',
        'baggage': 'sentry-environment=production,sentry-release=896f861151b432d53a63f5fdf2dab5a3f8b99ec0,sentry-public_key=8e3aea2ba071c511ad8e9f1d0b91dd04,sentry-trace_id=5fbf047d4468407e95b8af4cc051a029,sentry-sample_rate=0.05,sentry-transaction=routes%2F%24,sentry-sampled=false',
        'DNT': '1',
        'Sec-GPC': '1',
        'Connection': 'keep-alive',
        'Cookie': 'aws-waf-token=1159f3cf-5e16-4f7e-982d-3299d9e0e0f5:BQoAhLsq4kGhAQAA:5Huxrqo3McVdIS8hcZ2bIh4RTieKa9M/k5iaG27mTDO5E+xbXl44udLSc3jWY8+T3t021XyuEbiK/okiZkQz1UuRetQokT5YkzHLk+DPoKWFSHmehmkyxxl158KcKsbAKy9Fr7umsPdDaRkYzkmh3mhUOrDaK5VLC64/gLs8lcQfPA/U8PykZQysAT8lpS+m+cy1OebWaPhg8lL3rZK1xg==; _shopify_y=33c58b11-927B-422D-F96C-5B7E312AD467; _shopify_s=33c58b12-04AF-4E51-E4CD-B683DE47902A; dismissedCountryBanner=true',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Priority': 'u=0',
        'TE': 'trailers'
    }

    response = requests.get(url, headers=headers)
    data = response.json()
    return f"{data[36]} -> {data[26]}"

def AI():
    out = ""
    for city in ["jhajjar", "rohtak", "bahadurgarh"]:
        try: out += AI_AQI(city) + "\n"
        except: pass
    return out

# Example usage
if __name__ == "__main__":
    # Define the URL for the API
    url = "https://airquality.cpcb.gov.in/aqi_dashboard/aqi_all_Parameters"

    # Define the headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:144.0) Gecko/20100101 Firefox/144.0",
        "Accept": "text/plain, */*; q=0.01",
        "Accept-Language": "en-GB,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://airquality.cpcb.gov.in/AQI_India/",
        "accessToken": "eyJ0aW1lIjoxNzYxMjQ0NTE1MTkwLCJ0aW1lWm9uZU9mZnNldCI6LTMzMH0=",
        "Origin": "https://airquality.cpcb.gov.in",
        "DNT": "1",
        "Sec-GPC": "1",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Priority": "u=0",
        "TE": "trailers",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache"
    }

    # Locations and their station IDs
    locations = {"Bahadurgarh" : {'station_id': 'site_5045', 'date': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')},
                 "Rohtak" : {'station_id': 'site_147', 'date': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')},
                }

    # Define a message variable to accumulate data
    message = AI() + "\n"

    # Define the body data (Base64 encoded)
    for loc, loc_data in locations.items():
        encoded_loc = encode_to_base64(loc_data)
        # Get the raw string from the main function and append it to the message
        try: message += main(url, encoded_loc, headers, loc) + "\n"
        except: pass

    # Now `message` contains the cumulative text
    if message: post("AQI", message)
