class Spec:
    '''
    Defines the platform-specific specs for building to OSX using Metal. The
    purpose for such split is to enable different combinations for Apple
    platforms, such as OSX, iOS, tvOS, etc using different backends, like
    Metal, OpenGL, OpenGLES (or even Vulkan).
    '''
    def __init__(self):
        self.folder = 'osx-metal'

    def output_exe(self, file):
        return "{0}/{1}.app/Contents/MacOS/{1}".format(file.fold, file.base)
