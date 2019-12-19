class Spec:
    def __init__(self):
        self.folder = 'linux'
        self.includes = ['/usr/local/include']
        self.ninja_preamble = ''

    def bundle_folder(self, file):
        return "{0}/{1}-prefix".format(file.fold, file.base)

    def output_exe(self, file):
        return "bin/{0}".format(file.base)
