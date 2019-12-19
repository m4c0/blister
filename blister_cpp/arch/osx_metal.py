import subprocess

preamble = '''
isysroot = -isysroot {0}
app_ldflags = -mmacosx-version-min=10.14.0 -fobjc-arc -fobjc-link-runtime -lpng -lz \
    -framework AppKit \
    -framework AudioToolbox \
    -framework Metal \
    -framework MetalKit
'''

def _get_sdk_root():
    return subprocess.run(['xcrun', '--show-sdk-path'], capture_output=True).stdout.decode('utf-8')

class Spec:
    '''
    Defines the platform-specific specs for building to OSX using Metal. The
    purpose for such split is to enable different combinations for Apple
    platforms, such as OSX, iOS, tvOS, etc using different backends, like
    Metal, OpenGL, OpenGLES (or even Vulkan).
    '''
    def __init__(self):
        self.folder = 'osx-metal'
        self.includes = ['/usr/local/include']
        self.ninja_preamble = preamble.format(_get_sdk_root())

    def bundle_folder(self, file):
        return "{0}/{1}.app/Contents".format(file.fold, file.base)

    def output_exe(self, file):
        return "MacOS/{0}".format(file.base)
