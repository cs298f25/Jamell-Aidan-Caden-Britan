# **View Steps To Deploy Repo**

## Local Deployment
###  Clone the repo 
```bash
git clone https://github.com/cs298f25/Jamell-Aidan-Caden-Britan.git
```

### Install dependencies 
Make a virtual environment for dependencies 
```bash
python3 venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Set environment variables
Set the environment variables in the `.env` file.

```bash
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_SESSION_TOKEN=
REGION=us-east-1
BUCKET_NAME=<bucket-name>
```

### Run the app
Runs the program on port 8000
```bash
python3 -m src.app
```
See the app running at **`http://localhost:8000/`**

## Cloud Deployment
### 1. Launch EC2 Instance

1. Navigate to EC2 Dashboard in AWS Console
2. Click Launch Instance

### 2. Configure Instance Settings

**Name and OS:**
- Name: `image-hosting-server` (or your preferred name)
- AMI: **Amazon Linux 2023** (or Amazon Linux 2)

**Instance Type:**
- Select `t2.micro` (or `t3.micro` for better performance)

**Key Pair:**
- Select an existing key pair or create a new one

**Network Settings:**
- Click **Edit** on Network settings
- **Firewall (security groups):** Create new security group
- Add the following rules:
  -  **Allow SSH traffic from:** Anywhere (0.0.0.0/0) or My IP
  -  **Allow HTTP traffic from:** Anywhere (0.0.0.0/0)
  -  **Allow HTTPS traffic from:** Anywhere (0.0.0.0/0)

### 3. Configure IAM Role

- Scroll down to **Advanced Details**
- Under **IAM instance profile**, select **LabRole**
  - This grants your EC2 instance permissions to create and manage S3 buckets

### 4. Add User Data

- Still in **Advanced Details**, scroll to the bottom
- Find the **User data** text box
- Copy and paste the entire contents of your `userdata.sh` script
- change bucket-name to your bucket name
- change region to your region

### 5. Launch Instance

- Review your settings
- Click **Launch Instance**
- Wait for the instance to reach **Running** state (2-3 minutes)

### 6. Verify Deployment

1. Once the instance is running, note its **Public IPv4 address**
2. Wait 2-3 minutes for the user data script to complete
3. Access your application:





