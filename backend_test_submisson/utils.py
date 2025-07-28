import random
import string

def generate_shortcode(length=5):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))