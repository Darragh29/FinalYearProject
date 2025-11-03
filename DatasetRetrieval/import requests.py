import requests
import csv

#Discogs API key
token = "**************"
headers = {
    "User-Agent": "RecordDataScraper/1.0",
    "Authorization": f"Discogs token={token}"
}

#List of release IDs to search
releases = [
    "8478418", "21433636", "11256175", "14408244", "16190187", "32367828", "20415259", "28365832", "22856405", "27491511",  
    "31020487", "31555906", "31552768", "25416913", "492118", "436642", "11507204", "8308758", "3796250", "2630594",  
    "4635536", "10718124", "26050453", "427699", "3433715", "4037430", "5790430", "5790430", "14060447", "21928573",  
    "16883925", "26524775", "31918606", "30891144", "1655018", "3050226", "16758117", "21099064", "21099064", "359107",  
    "3370020", "168314", "733049", "227020", "152946", "600965", "1323551", "1395530", "1580639", "10781508", "7264443",  
    "120096", "373375", "31240957", "19673320", "19676632", "30697537", "24894176", "32803917", "30439715", "28638304",  
    "27604608", "21862852", "29001391", "32869278", "13374531", "247391", "733779", "965956", "2102722", "548886",  
    "1600568", "3574709", "852682", "1772093", "1466566", "1802251", "19911112", "27940218", "28831528", "1134155",  
    "395079", "496426", "204238", "237560", "676619", "714519", "11150319", "27080568", "4181251", "19444477", "26330912",  
    "11540861", "380627", "380627", "331234", "380614", "417369", "204856", "30832263"  
]

#Function to get release details using the release ID
def get_release_details(release_id):
    url = f"https://api.discogs.com/releases/{release_id}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None


csv_file = "album_data.csv"

#Opening the csv file for writing
with open(csv_file, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    #Title rows being written
    writer.writerow(["Album Name", "Release ID", "Artist(s)", "Year", "Genres", "Styles", "Tracklist", "Cover Image URLs"])

    #Looping through the release IDs and writing the data for each one to the csv file
    for release_id in releases:
        details = get_release_details(release_id)
        if details:
            #Extracting the specific details below from the API response
            album_name = details.get("title", "Unknown Album")
            year = details.get("year", "N/A")
            genres = ", ".join(details.get("genres", []))
            styles = ", ".join(details.get("styles", []))
            tracklist = ", ".join([track["title"] for track in details.get("tracklist", [])])

            #Extracting all of the image URLs and seperating them with a comma
            image_urls = [img["uri"] for img in details.get("images", [])]
            cover_images = ", ".join(image_urls) if image_urls else "N/A"

            #Getting the artist names
            artists = ", ".join([artist["name"] for artist in details.get("artists", [])])

            #Writing the data to the csv file
            writer.writerow([album_name, release_id, artists, year, genres, styles, tracklist, cover_images])
        else:
            print(f"Release ID {release_id} details not found")