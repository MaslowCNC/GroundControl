import os
import pkg_resources

def get_asset(path):
    return pkg_resources.resource_filename(__name__, os.path.join("assets", path) )