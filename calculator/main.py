import random
import os

def create_random_number(file_path):
    # Create directories if they don't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Generate a random number between 1 and 10
    number = random.randint(1, 10)
    
    # Write the number to the file
    with open(file_path, 'w') as f:
        f.write(str(number))
    
    print(f"Random number {number} written to {file_path}")

def read_and_multiply(base_path):
    
    # Find the result.txt file
    for root, dirs, files in os.walk(base_path):
        if 'result.txt' in files:
            file_path = os.path.join(root, 'result.txt')
            break
    else:
        print("result.txt not found")
        return
    
    # Read the number from the file
    with open(file_path, 'r') as f:
        number = int(f.read().strip())
    
    # Generate a random multiplier between 1 and 10
    multiplier = random.randint(1, 10)
    
    # Multiply the numbers
    result = number * multiplier
    
    print(f"Number from file: {number}")
    print(f"Random multiplier: {multiplier}")
    print(f"Result: {result}")
    
    return result

def sum_all_results(base_path):
    total_sum = 0
    files_found = 0

    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file == 'result.txt':
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r') as f:
                        value = int(f.read().strip())
                        total_sum += value
                        files_found += 1
                        print(f"Found {file_path}: value = {value}")
                except ValueError:
                    print(f"Error: {file_path} does not contain a valid integer")
                except Exception as e:
                    print(f"Error reading {file_path}: {str(e)}")

    print(f"\nTotal files found: {files_found}")
    print(f"Sum of all values: {total_sum}")
    return total_sum

def main():
    # Path for the first function's output
    file_path = './input/x/result.txt'
    
    # Call the first function
    create_random_number(file_path)
    
    # Call the second function
    read_and_multiply("./input")
    sum_all_results("./input")
if __name__ == "__main__":
    main()