import platform

from . import linux, osx_metal, windows;

def create_platform_specs():
    if platform.system() == 'Darwin':
        return osx_metal.Spec()
    
    if platform.system() == 'Linux':
        return linux.Spec()
    
    if platform.system() == 'Windows':
        return windows.Spec()
