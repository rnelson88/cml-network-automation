# 🛠️ My First Network Automation Lab (CML + Python)

The CCNA taught me how networks work. Now I want to learn how networks get run at scale, and that means automation. I'm not stopping at the cert. This repo is where I'm building those skills, one lab at a time.

First up: connecting my Windows PC to a Cisco router running in **Cisco Modeling Labs (CML)** and pushing config to it with **Python + Netmiko**.

I'll share the real steps I took, including what broke.

---

## 🧱 What I'm Working With

| Thing | Details |
|---|---|
| Host PC | Windows 11 |
| Hypervisor | VMware Workstation |
| Lab | CML-Free 2.9 running as a VM |
| Router | IOL (IOS on Linux) node — `R1` |
| Editor | Visual Studio / VS Code |
| Python library | [Netmiko](https://github.com/ktbyers/netmiko) |

---

## 🗺️ How It's Wired Up

```
[ Windows PC ] ── VMnet8 (192.168.111.0/24) ── [ CML VM ] ── bridge0 ── ext-conn-0 ── E0/0 [ R1 ]
 192.168.111.1                                 192.168.111.129                             192.168.111.132
```

The trick: my CML VM sits on VMware's **NAT network (VMnet8)**. The **External Connector** in CML set to **System Bridge (bridge0)** drops the router right onto that same network. So my PC can talk to R1 directly. No extra routing needed.

---

## Step 1 — Build the Topology in CML

1. Drag in an **IOL router** (`iol-0`)
2. Drag in an **External Connector** (`ext-conn-0`)
3. Set the connector to **System Bridge (bridge0)**
4. Link the router's **E0/0** to the connector
5. Start the lab ▶️

> 💡 Heads up: once a node has been started, its config gets locked. If you want to change the connector type, you have to **wipe** the node first.

---

## Step 2 — Check How CML Is Networked in VMware

When the CML VM boots, it shows its IP on the console:

```
Access the CML UI from https://192.168.111.129/
```

`192.168.111.x` = VMware NAT network. That means my PC can reach it through the **VMware Network Adapter VMnet8**.

Quick check on Windows:

```
ipconfig
```

Look for `VMware Network Adapter VMnet8` with a `192.168.111.x` address. If it's not there, go to **Edit → Virtual Network Editor** in VMware, pick VMnet8, and tick **"Connect a host virtual adapter to this network."**

---

## Step 3 — Give R1 an IP

Open R1's console in CML:

```
enable
conf t
hostname R1
interface Ethernet0/0
 ip address dhcp
 no shutdown
end
```

A few seconds later:

```
%DHCP-6-ADDRESS_ASSIGN: Interface Ethernet0/0 assigned DHCP address 192.168.111.132
```

R1 is on the network. 🎉

---

## Step 4 — Turn On SSH

```
conf t
ip domain-name lab.local
crypto key generate rsa modulus 2048
ip ssh version 2
username admin privilege 15 secret <your-password>
line vty 0 4
 login local
 transport input ssh
end
write memory
```

Check it:

```
show ip ssh
```

Should say **SSH Enabled - version 2.0**.

### 😬 What went wrong for me

```
ssh: connect to host 192.168.111.132 port 22: Connection refused
```

"Connection refused" actually means the network path is **fine**. R1 answered, it just wasn't listening on SSH yet. The RSA key never got generated. Once I set the hostname + domain name and re-ran `crypto key generate rsa`, it worked.

---

## Step 5 — Test SSH From Windows

```
ssh admin@192.168.111.132
```

First time you'll get a fingerprint warning, type `yes`. Enter your password and you're at `R1#`. 

If you can SSH in by hand, Python can too.

---

## Step 6 — Install Netmiko

```
py -m pip install netmiko
```

### 😬 What went wrong for me

```
ModuleNotFoundError: No module named 'netmiko'
```

Netmiko wasn't installed in the Python that my editor was using. If `pip install` didn't fix it, find out which Python your editor runs:

```python
import sys
print(sys.executable)
```

Then install with that exact one:

```
"C:\path\to\python.exe" -m pip install netmiko
```

Or use `pip install -r requirements.txt` from this repo.

---

## Step 7 — Run the Script

Set your password as an environment variable (so it's not sitting in the code):

```
set NET_PASS=your-password-here
```

Then:

```
python r1_test.py
```

What it does:
1. Connects to R1 over SSH
2. Runs `show ip interface brief`
3. Creates `Loopback0` with IP `1.1.1.1`
4. Saves the config

Check on R1:

```
show ip interface brief
```

`Loopback0  1.1.1.1` is there. Python configured my router. 🤖

### What went wrong for me

```python
print(f"Connecting to {R1} at {192.168.111.132}")
SyntaxError: invalid syntax
```

Anything inside `{ }` in an f-string gets run as Python code, and `192.168.111.132` is not valid Python. Fix: put stuff in variables first.

```python
name = "R1"
host = "192.168.111.132"
print(f"Connecting to {name} at {host}")
```

---

## 🧠 Things I Learned

- **"Connection refused" ≠ network problem.** It means something answered and said no.
- **SSH on IOS needs a hostname + domain name** before the RSA key will generate.
- **Python environments matter.** Installing a package somewhere doesn't mean your editor sees it.
- **Never commit passwords.** Env variables are the bare minimum. Real shops use a vault.

---

## 🚀 What's Next

How real teams do this, and where I'm taking this lab:

- [ ] **Backup script**: save `show run` to a timestamped file

---

## 📁 Files

| File | What it is |
|---|---|
| `r1_test.py` | The script that connects and configures R1 |
| `requirements.txt` | Python packages needed |
| `.gitignore` | Keeps junk + secrets out of the repo |

---

*Built in a home lab with CML-Free. Feel free to steal any of this.* 
