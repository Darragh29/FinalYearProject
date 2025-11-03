import os
import requests
import pandas as pd

#Load the csv file
csv_file = "album_data.csv"
df = pd.read_csv(csv_file)

#Creating the ouput folder
output_folder = "album_images"
os.makedirs(output_folder, exist_ok=True)

#Headers to simulate a real browser request - necessary for some image URLs
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Referer": "https://www.google.com/"
}

#Iterating over each row in the csv file
for index, row in df.iterrows():
    album_name = row['Album Name'].replace(" ", "_").replace("/", "_")
    artist_name = row['Artist(s)'].replace(" ", "_").replace("/", "_")
    
    #Getting all the image URLs
    image_urls = str(row['Cover Image URLs']).split(', ')

    for i, image_url in enumerate(image_urls, start=1):
        if not image_url or image_url == "N/A":
            continue  # Skip empty image URLs

        #Constructing filename
        filename = f"{album_name}_{artist_name}_{i}.jpg" if len(image_urls) > 1 else f"{album_name}_{artist_name}.jpg"
        file_path = os.path.join(output_folder, filename)

        try:
            #Make request with headers
            response = requests.get(image_url.strip(), headers=headers, timeout=10)
            response.raise_for_status()  #Raise an error for bad status codes

            # Save the image
            with open(file_path, "wb") as file:
                file.write(response.content)

            print(f"Downloaded: {filename}")

        except requests.exceptions.RequestException as e:
            print(f"Failed to download {filename}: {e}")
