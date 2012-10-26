
class AssetRemoved:
    def __init__(self, frs, path):
        self.frs = frs
        self.path = path

class AssetMoved:
    def __init__(self, frs, from_path, to_path):
        self.frs = frs
        self.from_path = to_path
        self.to_path = to_path

class AssetCopyed:
    def __init__(self, frs, from_path, to_path):
        self.frs = frs
        self.from_path = to_path
        self.to_path = to_path
