class Trie(object):
    flat_list = set()
    @property
    def children(self): 
        try:
            return self._children
        except AttributeError:
            self._children = dict()
            return self._children
    @property
    def previous(self): return self._p

    @previous.setter
    def previous(self, v): self._p = v

    @property
    def value(self): 
        try:
            return self._v
        except AttributeError:
            return None

    @value.setter
    def value(self, v): self._v = v

    @property
    def count(self): 
        try:
            return self._c
        except AttributeError:
            return 0

    @count.setter
    def count(self, v): self._c = v

    @property
    def reported_by(self): 
        try:
            return self._rb
        except AttributeError:
            self._rb = set()
            return self._rb

    def add(self, key, value, previous = ""):
        self.reported_by.update(value)
        self.count += 1
        self.previous = previous
        if key == "":
            self.value = value
            return

        for inkey in self.children:
            substring = self.compare(key, inkey)
            if substring == "":
                continue
            if substring == inkey:
                # the starting part is already there, can go straight ahead.
                self.children[inkey].add(key[len(inkey):], value, self.children[inkey].previous)
                return
            self.children[substring] = Trie()
            Trie.flat_list.add(self.children[substring])
            self.children[substring].children[inkey[len(substring):]] = self.children[inkey]
            self.children[substring].count = self.children[inkey].count
            self.children[substring].reported_by.update(self.children[inkey].reported_by)
            del self.children[inkey]
            self.children[substring].add(key[len(substring):], value, self.previous + substring)
            return
        self.children[key] = Trie()
        Trie.flat_list.add(self.children[key])
        self.children[key].add("", value, self.previous + key)
            
    def compare(self, default, incoming):
        if default == incoming:
            return default
        s1 = min([default, incoming])
        s2 = max([default, incoming])
        final = ""
        for i, c in enumerate(s1):
            if c != s2[i]:
                return s1[:i]
            
        return s1[:i+1]

    def get(self, key):
        if key == "":
            if self.value != None:
                return self.value
            else:
                raise KeyError()

        for inkey in self.children:
            if key.startswith(inkey):
                return self.children[inkey].get(key[len(inkey):])
        raise KeyError()

    def __getitem__(self, key):
        self.get(key)

    def __set__(self, key, value):
        self.add(key, value)





if __name__ == "__main__":
    t = Trie()

    t.add("hello world", 10)
    t.add("hello world234", 11)
    t.add("hello 234", 12)
    t.add("he234", 13)
    t.add("world", 14)
    t.add("ziggurat", 15)

    for t in sorted(Trie.flat_list, key = lambda x: x.count, reverse = True):
        print t.previous, t.count
