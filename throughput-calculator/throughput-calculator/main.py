import os
import time
import concurrent.futures

def calculate_throughput(directory, read_repeats):
    try:
        total_throughput = 0
        file_count = 0
        
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    file_size = os.path.getsize(file_path)
                    file_size_mib = file_size / (1024 * 1024)
                    
                    total_time = 0
                    
                    for _ in range(read_repeats):
                        start_time = time.time()
                        
                        with open(file_path, 'rb') as f:
                            f.read()
                        
                        end_time = time.time()
                        elapsed_time = end_time - start_time
                        total_time += elapsed_time
                    
                    # Calculate the average time per read
                    average_time = total_time / read_repeats if read_repeats > 0 else 0
                    # Calculate throughput for this file
                    throughput = file_size_mib / average_time if average_time > 0 else 0
                    
                    total_throughput += throughput
                    file_count += 1
                except Exception as e:
                    print(f"Error reading file {file_path}: {e}")
        
        # Calculate the average throughput for the directory
        average_throughput = total_throughput / file_count if file_count > 0 else 0
        
        return average_throughput, file_count
    except Exception as e:
        print(f"Error processing directory {directory}: {e}")
        return 0, 0

def calculate_throughput_for_directories(directories, read_repeats):
    results = []
    
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(calculate_throughput, dir, read_repeats) for dir in directories]
        
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"Error in future result retrieval: {e}")
                results.append((0, 0))
    
    return results

if __name__ == "__main__":
    directories = [ '/input/data-replicator-1','/input/data-replicator-2','/input/data-replicator-3']
    results = calculate_throughput_for_directories(directories, read_repeats=100)

    for i, (throughput, file_count) in enumerate(results):
        print(f"Directory {directories[i]}: Average Throughput = {throughput:.2f} MiBps, File Count = {file_count}")

    directories = [ '/input/data-replicator-1','/input/data-replicator-1','/input/data-replicator-1',]
    results = calculate_throughput_for_directories(directories, read_repeats=100)

    for i, (throughput, file_count) in enumerate(results):
        print(f"Directory {directories[i]}: Average Throughput = {throughput:.2f} MiBps, File Count = {file_count}")

