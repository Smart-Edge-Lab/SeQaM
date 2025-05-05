import os

from flask import Flask
import re

class RestFactory:
    def __init__(self):
        self.app = Flask(__name__)
        self.ipv4_pattern = re.compile(r'^(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])$')
        self.ipv6_pattern = re.compile(r"^((:|(0?|([1-9a-f][0-9a-f]{0,3}))):)((0?|([1-9a-f][0-9a-f]{0,3})):){0,6}(:|(0?|([1-9a-f][0-9a-f]{0,3})))$")
        self.create_GET_route('/health', lambda : os.environ['VERSION'])

    def create_GET_route(self, route, function, methods=['GET']):
        self.app.route(route, methods=methods)(function)

    def create_POST_route(self, route, function, methods=['POST']):
        self.app.route(route, methods=methods)(function)