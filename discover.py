import requests
from typing import Dict, Optional

def get_instagram_business_data(user_id: str, access_token: str, username: str) -> Optional[Dict]:
    """
    Retrieves public data about an Instagram Business or Creator account using the Business Discovery API.
    
    Args:
        user_id (str): The Instagram User ID of the user making the query.
        access_token (str): The access token with required permissions.
        username (str): The username of the Instagram account to query.
    
    Returns:
        dict: A dictionary containing the data, or None if an error occurs.
    """
    # Construct the API endpoint for business discovery
    endpoint = f"https://graph.facebook.com/v19.0/{user_id}"
    
    # Define the fields we want to retrieve based on the documentation
    fields = [
        "business_discovery.username(" + username + "){",
        "id,",
        "username,",
        "followers_count,",
        "media_count,",
        "ig_id,",
        "website,",
        "name,",
        "profile_picture_url,",
        "biography,",
        "media{",
        "  id,",
        "  caption,",
        "  media_type,",
        "  media_url,",
        "  permalink,",
        "  thumbnail_url,",
        "  timestamp,",
        "  username,",
        "  like_count,",
        "  comments_count,",
        "  children{media_url}",
        "}",
        "}"
    ]
    
    # Join fields and remove whitespace
    fields_str = "".join(fields).replace(" ", "")
    
    params = {
        "fields": fields_str,
        "access_token": access_token,
    }

    try:
        # Make the API request
        print(f"Making request to: {endpoint}")
        print(f"With params: {params}")
        
        response = requests.get(endpoint, params=params)
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.text}")
        
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response text: {e.response.text}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def main():
    """
    Main function to test the API call.
    """
    # Replace with your actual values
    user_id = "17841472218888122"  # Your Instagram Business Account ID
    access_token = "IGAAYSBnqbP3JBZAE93N1BjMmZAfRGN6SmJWWDF0d1B2cElYRloxRWlqaDJXenNMQWFPNmF3WHZAtejdwVFI4czQwNGxwMXJvMXNldGtoZAHExVG5IeW9ORGtZAZAGRrOURGYlZAFemtJVzBMck1SVXZAMYW5zeWc1ZAWV5S1NIcU1vSk1iTQZDZD"
    username = "saucotec"

    data = get_instagram_business_data(user_id, access_token, username)

    if data:
        print("Successfully retrieved data:")
        print(data)
    else:
        print("Failed to retrieve data.")

if __name__ == "__main__":
    main()

