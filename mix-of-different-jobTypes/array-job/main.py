import os

if __name__ == "__main__":
    print("array index: ", os.environ.get('AWS_BATCH_JOB_ARRAY_INDEX'))
    print("array size: ", os.environ.get('AWS_BATCH_JOB_ARRAY_SIZE'))
