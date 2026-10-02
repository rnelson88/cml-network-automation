import os
from netmiko import ConnectHandler

# --- Device info ---
name = "R1"
host = "192.168.111.132"

# Password comes from an environment variable so it's not in the code.
# Windows:  set NET_PASS=your-password-here
password = os.environ.get("NET_PASS")
if not password:
    raise SystemExit("Set the NET_PASS environment variable first.")

r1 = {
    "device_type": "cisco_ios",
    "host": host,
    "username": "admin",
    "password": password,
}

print(f"Connecting to {name} at {host}...")

with ConnectHandler(**r1) as conn:
    # Read something
    print(conn.send_command("show ip interface brief"))

    # Change something
    output = conn.send_config_set([
        "interface Loopback0",
        "ip address 1.1.1.1 255.255.255.255",
        "description Configured by Python",
    ])
    print(output)

    # Save it
    conn.save_config()

print("Done ✅")
