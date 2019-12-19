class Spec:
    def __init__(self):
        self.folder = 'windows'
        self.ninja_preamble = ''

    def bundle_folder(self, file):
        return "{0}/{1}-redist".format(file.fold, file.base)

    def output_exe(self, file):
        return "{0}.exe".format(file.base)
