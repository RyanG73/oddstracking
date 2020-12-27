import pandas as pd
import paramiko
import os

ssh = paramiko.SSHClient()
ssh.connect('127.0.1.1', username='pi', password='ohio',port=22)
ssh.connect('127.0.1.1', username='pi', password='ohio',port=22)
ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd_to_execute)

ssh.connect('192.168.1.40 2603:6011:4206:f5b0:1047:94:c3cf:2ea8', port=22, username='pi', password='ohio')

ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
ssh.connect("ryanpi", username="pi", password="ohio", port=22)