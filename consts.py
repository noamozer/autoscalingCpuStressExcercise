from helpers import readFile, base64EncodeScript

# define env vars - public Linux us-west-2 AMI, ELB Name
US_WEST_2_LINUX_AMI = "ami-0518bb0e75d3619ca"
ELB_NAME = "GuestTestELB"

# read a user data script that creates a simple index.html file at /var/www/html
# and starts an apache web server 
plaintextUserdata = readFile("userdata.sh")
BASE64_ENCODED_USERDATA = base64EncodeScript(plaintextUserdata)

# set cpu threshold to scale when reached
AUTOSCALE_CPU_THRESHOLD = 80