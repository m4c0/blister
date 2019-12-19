class Spec:
    def __init__(self):
        self.folder = 'windows'
    
    def output_exe(self, file):
        return "{0}/{1}-redist/{1}.exe".format(file.fold, file.base)
