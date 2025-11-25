"""
NumPy 2.0 compatibility patch for RecBole
"""
import numpy as np

# Restore deprecated numpy types for RecBole compatibility
if not hasattr(np, 'float_'):
    np.float_ = np.float64
if not hasattr(np, 'int_'):
    np.int_ = np.int64
if not hasattr(np, 'bool_'):
    np.bool_ = bool
if not hasattr(np, 'complex_'):
    np.complex_ = np.complex128
if not hasattr(np, 'object_'):
    np.object_ = object
if not hasattr(np, 'str_'):
    np.str_ = str
if not hasattr(np, 'unicode_'):
    np.unicode_ = str
