# autoscalingCpuStressExcercise

This is a script that launches an EC2 instance and registers it to an ELB.
The script will monitor that instance's CPU and scale when reaches the cpu threshold.

Notes: 
1. The default CPU threshold is 80 and is set in the consts.py file.
2. userdata.sh is a bash script that runs on each instance that is launched. It launches a web server (in order for instances to be inService in the ELB), and starts a cpu stress tool.

## Requirements

boto3 is required in order to run script.

## Instructions

In order to start the script, run:

$ python autoscalingCpuStress.py
