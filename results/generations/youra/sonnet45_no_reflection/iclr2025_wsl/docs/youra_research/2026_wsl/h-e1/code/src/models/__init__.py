"""Model implementations"""
from .baseline import DeepSetsEncoder
from .proposed import SlotEquivariantEncoder

__all__ = ['DeepSetsEncoder', 'SlotEquivariantEncoder']
