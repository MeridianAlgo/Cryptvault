"""ML Models for cryptocurrency price prediction."""

from .ensemble_model import AdvancedEnsembleModel
from .linear_models import LinearPredictor

# Alias for backward compatibility
EnsembleModel = AdvancedEnsembleModel

__all__ = ["LinearPredictor", "AdvancedEnsembleModel", "EnsembleModel"]
