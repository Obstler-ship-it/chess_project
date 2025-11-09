class TranspositionTable:
    def __init__(self, size=1000000):
        self.size = size
        self.table = {}
        
    def store(self, key, value):
        self.table[key % self.size] = value
        
    def lookup(self, key):
        return self.table.get(key % self.size)
