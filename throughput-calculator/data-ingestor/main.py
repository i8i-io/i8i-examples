import requests
import os

def download_video_from_public_s3_url(url, output_dir='/output'):
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Extract the file name from the URL
    file_name = os.path.basename(url)
    
    # Set the output file path
    output_file = os.path.join(output_dir, file_name)
    
    try:
        # Stream the download to avoid loading the entire file into memory
        with requests.get(url, stream=True) as response:
            response.raise_for_status()  # Check for HTTP errors
            with open(output_file, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
        
        print(f"Downloaded: {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    download_video_from_public_s3_url(os.environ.get("FILE_URL"))
