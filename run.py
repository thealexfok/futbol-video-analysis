import subprocess

# Define the manage.py command with the desired arguments
command = "streamlit run Home.py --server.port 80"

# Run the command
subprocess.run(command, shell=True)