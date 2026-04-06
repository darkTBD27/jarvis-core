import subprocess

def gpu_available():

    try:

        subprocess.check_output(["nvidia-smi"])

        return True

    except:

        return False
