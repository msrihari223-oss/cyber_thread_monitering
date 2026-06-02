import random

otp_storage = {}

def generate_otp():
    return str(
        random.randint(100000,999999)
    )