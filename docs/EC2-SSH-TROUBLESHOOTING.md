# EC2 SSH Timeout — Checklist

If SSH to your wordware instance still times out after fixing the security group, work through this in order.

---

## 1. Confirm the instance’s current public IP

- **EC2 → Instances → wordware**
- Check **Public IPv4 address**. If it’s blank, the instance has no public IP (fix in step 4).
- If you stopped and started the instance, the IP may have **changed** from `32.141.31.178`. Use whatever is shown now in the console.

---

## 2. Security group: one rule that can’t fail

- **EC2 → Instances → wordware → Security tab**
- Click the security group: **sg-065e996c35b5188e0 (launch-wizard-3)**
- **Edit inbound rules**
- **Delete** the existing SSH rule that had source `32.141.31.178/32` (or any narrow source).
- **Add rule:**
  - Type: **SSH**
  - Port: **22**
  - Source: **Anywhere-IPv4** → `0.0.0.0/0`
  - Description: `Temp SSH from anywhere`
- **Save rules**

This removes any chance of “wrong source IP”. You can tighten to “My IP” later once SSH works.

Try again:

```bash
ssh -i ~/.ssh/wordware.pem -o ConnectTimeout=15 ubuntu@<PUBLIC_IP_SHOWN_IN_CONSOLE>
```

If it still times out, go to step 3.

---

## 3. Network ACL (NACL) — often the real blocker

NACLs are **stateless**. You need:

- Inbound: allow TCP 22 from `0.0.0.0/0`
- Outbound: allow return traffic on **ephemeral ports** (e.g. 1024–65535) to `0.0.0.0/0`

Steps:

- **VPC → Subnets**
- Click your instance’s subnet: **subnet-0f13b05f86c96878d**
- Open the **Network ACL** link: **acl-01ac2921d82a14d71**
- **Edit inbound rules**
  - Ensure there is a rule that allows:
    - Type: **SSH (22)** or **Custom TCP**, port **22**
    - Source: **0.0.0.0/0**
  - If the default rule is “Deny all” (e.g. rule 100\*), add a **lower** rule number (e.g. 50) that **Allows** TCP 22 from 0.0.0.0/0.
- **Edit outbound rules**
  - Ensure a rule allows:
    - Type: **Custom TCP**
    - Port: **1024-65535** (ephemeral)
    - Destination: **0.0.0.0/0**
  - (Or “All traffic” to 0.0.0.0/0 if that’s simpler.)
- **Save**

Default NACLs often allow all; custom NACLs often block. After saving, try SSH again.

---

## 4. No public IP?

If **Public IPv4 address** is empty:

- Allocate an **Elastic IP**: **EC2 → Network & Security → Elastic IPs → Allocate**
- **EC2 → Instances → wordware → Actions → Networking → Associate Elastic IP** and pick the new EIP
- Use that Elastic IP in your SSH command (and in the security group source if you lock it down later).

---

## 5. “My IP” vs your real IP

If you used **My IP** in the security group and it still fails:

- Your ISP might use a different outgoing IP than AWS detected.
- **Temporarily** set source to **0.0.0.0/0** (as in step 2). If SSH works, then switch back to **My IP** and compare with your real IP (e.g. from https://whatismyip.com or `curl ifconfig.me`).

---

## 6. Optional: use Session Manager (no port 22)

If you enable SSM, you can get a shell without opening port 22:

- Attach an **IAM role** to the instance with **AmazonSSMManagedInstanceCore**
- **EC2 → Instances → wordware → Connect → Session Manager → Connect**

This confirms the instance is reachable; SSH can be fixed separately.

---

## 7. Other reasons SSH can time out

### You edited a different security group

- The instance uses the SG shown on **wordware → Security tab** (e.g. `launch-wizard-3`).
- If you opened **Security Groups** from the left menu and edited a different SG, the instance never gets that rule.
- **Check:** Instance → Security tab → click the SG name → confirm the inbound rules you see are the ones you edited (SSH from 0.0.0.0/0).

### Instance is in a different subnet (with a different NACL)

- **wordware** might be in a different subnet than the one you checked (e.g. after a stop/start or wrong assumption).
- **Check:** Instance → **Networking** tab → **Subnet ID**. Open that subnet → **Network ACL**. If that NACL is not the default (or has a deny rule for port 22), fix that NACL’s inbound/outbound rules.

### Your network blocks outbound port 22

- Some offices, schools, or ISPs block outbound SSH (TCP 22).
- **Check:** From your Mac run `nc -vz -G 5 8.8.8.8 22` — if that times out too, your network may block outbound 22. Or try from a **phone hotspot** (different network) and SSH again; if it works, the block is on your usual network.

### Instance status checks failed

- If the instance failed status checks, it might not be fully booted or the network stack might be bad.
- **Check:** Instance → **Status checks**. Both “System reachability” and “Instance reachability” should be green. If either is red, try **Reboot instance** or **Stop → Start** (stop/start gives a new public IP — use the new one in SSH).

### Wrong public IP (stale or typo)

- After **Stop → Start**, the public IP changes unless you use an Elastic IP.
- **Check:** Always use the **Public IPv4 address** shown on the instance **Details** tab right now. Don’t reuse an old IP from a previous session.

### Elastic IP not attached (or wrong one)

- If you allocated an Elastic IP but didn’t **Associate** it with wordware, SSH to the instance’s auto-assigned public IP. If you associated an EIP, use the EIP in your SSH command, not the old auto-assigned IP.

### Use EC2 Instance Connect to see who’s blocked

- **EC2 → Instances → wordware → Connect**
- Choose **EC2 Instance Connect** → **Connect**. This opens a browser-based SSH session from AWS to your instance.
- If **EC2 Instance Connect works:** the instance and its security group are fine from AWS’s side; the timeout is likely your IP (security group source) or your network (outbound 22 blocked).
- If **EC2 Instance Connect fails:** the problem is on the instance/security group/VPC (e.g. wrong SG, no public IP, or instance not booted).

### VPC Reachability Analyzer (optional)

- **VPC → Network Analysis → Reachability Analyzer → Create and analyze path**
- **Source:** Internet Gateway (your VPC’s IGW).
- **Destination:** wordware instance.
- **Analyze.** If the path fails, the result shows where it fails (e.g. security group, NACL).

---

## Quick reference

| Check              | Where to look |
|--------------------|----------------|
| Public IP          | EC2 → Instances → wordware |
| Security group     | Instance → Security → security group → Inbound rules |
| NACL               | VPC → Subnets → subnet → Network ACL → Inbound/Outbound |
| Route to internet  | Subnets → subnet → Route table → 0.0.0.0/0 → igw-... |

After step 2 + step 3, SSH with:

```bash
ssh -i ~/.ssh/wordware.pem -o ConnectTimeout=15 ubuntu@<PUBLIC_IP>
```

Replace `<PUBLIC_IP>` with the exact value from the console.
