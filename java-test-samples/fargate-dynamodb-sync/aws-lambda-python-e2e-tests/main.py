import os

print('Loading function')
def lambda_handler():
    os.system("pytest --html=report.html --self-contained-html")

if __name__ == "__main__":
    lambda_handler()