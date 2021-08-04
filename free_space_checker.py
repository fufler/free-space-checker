#!/usr/env python3

import sys
import os
import json
import argparse
import re
from http.server import BaseHTTPRequestHandler, HTTPServer

class RequestHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        if self.path != '/status':
            self.send_error(404)

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        ok = True

        response = {'dirs': []}

        for (path, size, unit) in self.server.dirs:
            stat = os.statvfs(path)

            d_reserved = (stat.f_bfree - stat.f_bavail) * stat.f_bsize
            d_free = stat.f_bavail * stat.f_bsize
            d_size = stat.f_blocks * stat.f_bsize
            d_ok = 100 * d_free / (d_size - d_reserved) > size if unit is None else d_free > size * unit

            dir_status = {
                'path': path,
                'free': d_free,
                'size': d_size,
                'ok': d_ok
            }

            response['dirs'].append(dir_status)

            if not d_ok:
                ok = False

        response['ok'] = ok

        self.wfile.write(json.dumps(response).encode())

class Server(HTTPServer):
    def __init__(self, dirs, server_address, request_handler):
        super(Server, self).__init__(server_address, request_handler)

        for (d, _, _) in dirs:
            if not os.path.isdir(d):
                raise ValueError(f'Path is not directory: {d}')

        self.dirs = dirs


UNITS = {
    'B': 1000**0,
    'K': 1000**1,
    'M': 1000**2,
    'G': 1000**3,
    '%': None
}


def parse_directory_spec(d):
    match = None
    try:
        match = re.fullmatch(r'\s*([^:]+):(\d+)([a-zA-Z%]+)\s*', d)
    finally:
        if match is None:
            raise ValueError(f'Invalid directory to monitor specification: {d}')

    path = match.group(1)
    size = match.group(2)
    unit = match.group(3)

    return (path, int(size), UNITS[unit])

example_text = '''example:
    python3 free_space_checker.py --address 192.168.12.34 --port 8081 /var/lib/docker/volumes:10G /var/cache:50%
'''

parser = argparse.ArgumentParser(
    description='Simple HTTP server that provides API to perform free disk space checks',
    epilog=example_text,
)

parser.add_argument(
    '--address',
    default='',
    help='Address to bind to'
)

parser.add_argument(
    '--port',
    default=8080,
    type=int,
    help='Port to listen to'
)

parser.add_argument(
    'dirs',
    metavar='DIR',
    nargs='+',
    help='Directories to monitor free space in (path:<10G | 50%%>)'
)

parser.add_argument(
    '--single-argument-dirs',
    action='store_true',
    default=False,
    help='Parse first dirs argument as comma-separated list of directories'
)

parser.add_argument(
    '--strip-path',
    action='store_true',
    default=False,
    help='Perform str.strip on each path specification'
)

args = parser.parse_args()

if args.single_argument_dirs:
    if len(args.dirs) > 1:
        print('Expected only one positional argument due to --single-argument-dirs switch was specified', file=sys.stderr)
        sys.exit(-1)

    dirs = args.dirs[0].split(',')
else:
    dirs = args.dirs

if args.strip_path:
    dirs = [d.strip() for d in dirs]

server_address = (args.address, args.port)
httpd = Server(
    [parse_directory_spec(d) for d in dirs],
    server_address,
    RequestHandler
)
httpd.serve_forever()
