from domain.value_objects import IMONumber, Tonnage, Cargo

class Ship:
    """A ship. Aggregate Root and Entity, identified by its IMO number."""
    
    def __init__(self, imo_number: IMONumber, name: str, capacity: Tonnage):
        if not name.strip():
            raise ValueError("Ship name must not be empty")
        if capacity.value <= 0:
            raise ValueError("Ship capacity must be greater than zero")
        self._imo_number = imo_number
        self._name = name
        self._capacity = capacity

    @property
    def imo_number(self) -> IMONumber:
        return self._imo_number
    
    def can_carry(self, cargo: Cargo) -> bool:
        return cargo.weight.value <= self._capacity.value
    
    # __eq__ — decides when two objects are equal. Returns True/False. 
    # Returns NotImplemented only when other is not a Ship (a type mismatch)
    def __eq__(self, other) -> bool:
        if not isinstance(other, Ship):
            return NotImplemented
        return self._imo_number == other._imo_number
    
    # the moment you define __eq__, Python sets __hash__ = None automatically, 
    # making the object unhashable (can't go in a set/dict). You must redefine 
    # __hash__ to restore it. That's why they always come as a pair
    def __hash__(self) -> int:
        return hash(self._imo_number)