import os

if __name__ == "__main__":
    print("Am I the main node?: ", os.environ.get('IS_MAIN_NODE'))
