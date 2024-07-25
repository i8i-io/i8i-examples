import random
import os

output_path = '/output/result.txt'
random_limit = int(os.environ.get("LIMIT", "10"))

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
    multiplier = random.randint(1, random_limit)
    
    # Multiply the numbers
    result = number * multiplier
    
    print(f"Number from file: {number}")
    print(f"Random multiplier: {multiplier}")
    with open(output_path, 'w') as f:
        f.write(str(result))
    
    print(f"Multiplication result: {result} written to {output_path}")
    
    return result

def main():
    read_and_multiply("/input")
if __name__ == "__main__":
    main()