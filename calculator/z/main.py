import random
import os
output_path = '/output/result.txt'

def read_and_divide(base_path):
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
    
    # Generate a random divider between 1 and 10
    divider = random.randint(1, 10)
    
    # Divide the numbers
    result = number * divider
    
    print(f"Number from file: {number}")
    print(f"Random divider: {divider}")
    with open(output_path, 'w') as f:
        f.write(str(number))
    
    print(f"Division result: {result} written to {output_path}")
    return result

def main():
    read_and_divide("/input")
    
if __name__ == "__main__":
    main()