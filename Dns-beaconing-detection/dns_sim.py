import random
import string
import time
import subprocess

DNS_SERVER = "192.168.239.130"
DOMAIN = "lab.local"
COUNT = 40
INTERVAL = 5

def random_label(length=12):
    chars = string.ascii_lowercase + string.digits
    return "".join(random.choice(chars) for _ in range(length))

for i in range(COUNT):
    name = f"{random_label()}.{DOMAIN}"
    subprocess.run(
        ["dig", f"@{DNS_SERVER}", name, "+short", "+time=2", "+tries=1"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print(f"[{i+1}/{COUNT}] {name}")
    time.sleep(INTERVAL)
