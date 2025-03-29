import requests

def get_instagram_business_data(user_id, access_token, username):
    """
    Retrieves public data about an Instagram Business or Creator account using the Business Discovery API.

    Args:
        user_id (str): The Instagram User ID of the user making the query.
        access_token (str): The access token.
        username (str): The username of the Instagram account to query.

    Returns:
        dict: A dictionary containing the data, or None if an error occurs.
              The dictionary structure corresponds to the fields requested.
    """
    # Construct the API endpoint.
    endpoint = f"https://graph.facebook.com/v19.0/{user_id}"  # Use a specific API version
    fields = "business_discovery.username(" + username + \
        "){followers_count,media_count,media{id,caption,like_count,comments_count,timestamp},website,biography,username,profile_picture_url}"
    params = {
        "fields": fields,
        "access_token": access_token,
    }

    try:
        # Make the API request.
        response = requests.get(endpoint, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes.
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def main():
    """
    Main function to execute the API call and print the result.
    """
    # Replace with your actual values.
    user_id = "17841472218888122"  #  Replace with the User ID of the account making the request.
    access_token = "IGAAQzZBwNjKrdBZAE1sblRLQVN4cXAxQU4temlFbFlLNU9XTkFqYnk3RC1iS2V3TFRFS012bDQzR0JSYnZAGVnpqeUh5b3NGWkQxbkdsMVB2bGNUZAnJKN3NpaHc1a3ZAubUZADUVFwM2VQTEU1WTVab3FUZAEFKdW9vemYzNk40Q1BZAbwZDZD"  #  Replace with your actual access token
    username = "saucotec"

    data = get_instagram_business_data(user_id, access_token, username)

    if data:
        print(data)  #  Print the entire response.  You can then process it as needed.
        # Example of accessing specific data:
        # followers_count = data.get("business_discovery", {}).get("followers_count")
        # print(f"Followers: {followers_count}")
    else:
        print("Failed to retrieve data.")


if __name__ == "__main__":
    main()

