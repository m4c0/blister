class Spec:
    def __init__(self):
        self.folder = 'linux'

    def output_exe(self, file):
        return "{0}/{1}-prefix/bin/{1}".format(file.fold, file.base)
