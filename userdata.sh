# ssh -i ~/.ssh/labsuser.pem ec2-user@<IPv4 address or DNS>

# Update system packages
sudo yum update -y

# Install Python 3, pip, and git
sudo yum install -y python3 python3-pip git

# Install gunicorn for production Flask deployment
sudo pip3 install gunicorn

# Clone the repository (specific branch)
cd /home/ec2-user
git clone -b userdata_script https://github.com/cs298f25/Jamell-Aidan-Caden-Britan.git
cd Jamell-Aidan-Caden-Britan

# Create virtual environment
python3 -m venv .venv


source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install gunicorn in virtual environment
pip install gunicorn

# Change to src directory where app.py is located
cd src

# Run the application with gunicorn on port 8000
# Using 0.0.0.0 to allow external access
gunicorn -w 4 -b 0.0.0.0:8000 app:app --daemon


