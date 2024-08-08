import os
import shutil

def copy_files(input_path, output_dir='/output'):
    # Construct the full input path
    full_input_path = os.path.join('/input', input_path)
    
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    try:
        # Check if the input path exists and is a directory
        if not os.path.exists(full_input_path):
            raise FileNotFoundError(f"Input path '{full_input_path}' does not exist.")
        if not os.path.isdir(full_input_path):
            raise NotADirectoryError(f"Input path '{full_input_path}' is not a directory.")
        
        # Iterate over all files in the input directory
        for file_name in os.listdir(full_input_path):
            file_path = os.path.join(full_input_path, file_name)
            
            # Check if it's a file before copying
            if os.path.isfile(file_path):
                shutil.copy(file_path, output_dir)
                print(f"Copied: {file_name} to {output_dir}")
    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    copy_files("data-ingestor")
