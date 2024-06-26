import requests
import os
import zipfile

def download_and_unpack_zip_from_url(url, destination_folder):
    # Create the destination folder if it doesn't exist
    os.makedirs(destination_folder, exist_ok=True)

    # Extract the filename from the URL
    file_name = url.split('/')[-1]
    zip_file_path = os.path.join(destination_folder, "spotify.zip")

    # Download the zip file from the URL
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(zip_file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=524288000):
                f.write(chunk)

    # Unpack the zip file
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(destination_folder)

    # Clean up: remove the downloaded zip file
    os.remove(zip_file_path)

if __name__ == "__main__":
    url = "https://spotify-million-playlist-dataset.s3.eu-central-1.wasabisys.com/files/spotify_million_playlist_dataset.zip?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=9CMW6ZOKNMP5PC96SKW9%2F20240516%2Feu-central-1%2Fs3%2Faws4_request&X-Amz-Date=20240516T145914Z&X-Amz-Expires=86400&X-Amz-SignedHeaders=host&X-Amz-Signature=61ff7db3cfeb133c040ea7be2e0399dc928ea0904f81a6699ce99e7f86f573ab"
    destination_folder = '/output'

    download_and_unpack_zip_from_url(url, destination_folder)