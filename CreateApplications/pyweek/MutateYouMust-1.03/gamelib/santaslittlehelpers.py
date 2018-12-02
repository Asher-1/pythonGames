'''
Created on 15.09.2011

@author: Archy
'''

class SaferList:
    
    _PrimaryList = None
    _SecondaryList = None
    _editList = None    
    
    def __init__(self):
        self.clear()
        
    def add_item(self, item):
        self._SecondaryList.add(item)
        self._editList.append((True, item))
            
    def remove_item(self, item):
        self._SecondaryList.remove(item)
        self._editList.append((False, item))
    
    def get_safe_list(self):
        for eventType, item in self._editList:
            if eventType: self._PrimaryList.add(item)
            else: self._PrimaryList.remove(item)
        self._editList[:] = [] 
        return self._PrimaryList
    
    def get_unsafe_list(self):
        return self._SecondaryList
            
    def clear(self):
        self._PrimaryList = set()
        self._SecondaryList = set()
        self._editList = []
        
    def set_list(self, newList):
        self.clear()
        for item in newList:
            self.add_item(item)            

class EntityList(SaferList):
    
    _TypeList = None
    
    def __init__(self):
        SaferList.__init__(self)    
        
    def clear(self):
        SaferList.clear(self)
        self._TypeList = dict()
    
    def add_item(self, item):
        SaferList.add_item(self, item)
        subList = self._TypeList.get(item.get_archetype())
        if not subList:
            subList = set()
            self._TypeList[item.get_archetype()] = subList
        subList.add(item)
        
    def remove_item(self, item):
        SaferList.remove_item(self, item)
        subList = self._TypeList.get(item.get_archetype())
        subList.remove(item)
    
    def get_of_type(self, archetype):
        subList = self._TypeList.get(archetype)
        if not subList:
            subList = set()
            self._TypeList[archetype] = subList
        return subList