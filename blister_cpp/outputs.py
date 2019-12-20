from os import makedirs

from . import arch

root = arch.create_platform_specs().root()

def get_filename(file):
    return '{0}/build/{1}'.format(root, file)

def create_file(file):
    return open(get_filename(file), 'w')

def create_dir(rel=''):
    try:
        makedirs(get_filename(rel))
    except OSError:
        pass
