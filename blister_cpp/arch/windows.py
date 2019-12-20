from os import getcwd

class Spec:
    def __init__(self):
        self.folder = 'windows'
        self.includes = []
        self.ninja_preamble = ''

    def root(self):
        # Removes drive letter and replaces the path bars
        # TODO: find the correct way of handling this in Ninja
        return getcwd()[2:].replace('\\', '/') 

    def bundle_folder(self, file):
        return "{0}/{1}-redist".format(file.fold, file.base)

    def output_exe(self, file):
        return "{0}.exe".format(file.base)
