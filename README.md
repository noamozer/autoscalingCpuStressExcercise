# autoscalingCpuStressExcercise

This is a script that launches an EC2 instance and registers it to an ELB.
The script will monitor that instance's CPU and scale when reaches the cpu threshold.

(The default CPU threshold is 80 and is set in the consts.py file)

## Requirements

boto3 is required in order to run script.

## Instructions

In order to start the script, run:

$ python autoscalingCpuStress.py
