# free-space-checker

Zero-dependency Python script that provides API to check for available disc space

```
usage: free_space_checker.py [-h] [--address ADDRESS] [--port PORT] [--single-argument-dirs] DIR [DIR ...]

Simple HTTP server that provides API to perform free disk space checks

positional arguments:
  DIR                   Directories to monitor free space in (path:<10G | 50%>)

optional arguments:
  -h, --help            show this help message and exit
  --address ADDRESS     Address to bind to
  --port PORT           Port to listen to
  --single-argument-dirs
                        Parse first dirs argument as comma-separated list of directories

example: python3 free_space_checker.py --address 192.168.12.34 --port 8081 /var/lib/docker/volumes:10G /var/cache:50%

```
