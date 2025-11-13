"""ML Models for cryptocurrency price prediction."""

from .linear_models import LinearPredictor
from .ensemble_model import AdvancedEnsembleModel

# Alias for backward compatibility
EnsembleModel = AdvancedEnsembleModel

__all__ = [
    'LinearPredictor',
    'AdvancedEnsembleModel',
    'EnsembleModel'
]
