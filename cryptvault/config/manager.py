"""Configuration manager for loading, saving, and managing settings."""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import asdict, fields
import logging

from .settings import (
    SensitivitySettings, DisplaySettings, PatternSettings, 
    AnalysisSettings, SensitivityLevel
)


class ConfigManager:
    """Manages configuration loading, saving, and validation."""
    
    def __init__(self, config_dir: str = None):
        """Initialize configuration manager."""
        if config_dir is None:
            # Default to user's home directory
            config_dir = os.path.join(os.path.expanduser("~"), ".crypto_chart_analyzer")
        
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "config.json"
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize settings with defaults
        self.sensitivity = SensitivitySettings()
        self.display = DisplaySettings()
        self.patterns = PatternSettings()
        self.analysis = AnalysisSettings()
        
        # Load existing configuration
        self.load_config()
        
        # Setup logging
        self._setup_logging()
    
    def load_config(self) -> bool:
        """Load configuration from file."""
        try:
            if not self.config_file.exists():
                # Create default config file
                self.save_config()
                return True
            
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)
            
            # Load each settings section
            if 'sensitivity' in config_data:
                self._load_sensitivity_settings(config_data['sensitivity'])
            
            if 'display' in config_data:
                self._load_display_settings(config_data['display'])
            
            if 'patterns' in config_data:
                self._load_pattern_settings(config_data['patterns'])
            
            if 'analysis' in config_data:
                self._load_analysis_settings(config_data['analysis'])
            
            return True
            
        except Exception as e:
            logging.warning(f"Failed to load configuration: {e}. Using defaults.")
            return False
    
    def save_config(self) -> bool:
        """Save current configuration to file."""
        try:
            config_data = {
                'sensitivity': self._serialize_settings(self.sensitivity),
                'display': self._serialize_settings(self.display),
                'patterns': self._serialize_settings(self.patterns),
                'analysis': self._serialize_settings(self.analysis),
                'version': '1.0',
                'created_by': 'Crypto Chart Analyzer'
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2, default=str)
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to save configuration: {e}")
            return False
    
    def reset_to_defaults(self):
        """Reset all settings to default values."""
        self.sensitivity = SensitivitySettings()
        self.display = DisplaySettings()
        self.patterns = PatternSettings()
        self.analysis = AnalysisSettings()
        self.save_config()
    
    def set_sensitivity_preset(self, level: SensitivityLevel):
        """Set sensitivity to a predefined level."""
        self.sensitivity = SensitivitySettings.get_preset(level)
        self.save_config()
    
    def update_sensitivity(self, **kwargs):
        """Update sensitivity settings."""
        for key, value in kwargs.items():
            if hasattr(self.sensitivity, key):
                setattr(self.sensitivity, key, value)
        self.save_config()
    
    def update_display(self, **kwargs):
        """Update display settings."""
        for key, value in kwargs.items():
            if hasattr(self.display, key):
                setattr(self.display, key, value)
        self.save_config()
    
    def update_patterns(self, **kwargs):
        """Update pattern settings."""
        for key, value in kwargs.items():
            if hasattr(self.patterns, key):
                setattr(self.patterns, key, value)
        self.save_config()
    
    def update_analysis(self, **kwargs):
        """Update analysis settings."""
        for key, value in kwargs.items():
            if hasattr(self.analysis, key):
                setattr(self.analysis, key, value)
        self.save_config()
    
    def enable_pattern(self, pattern_name: str, enabled: bool = True):
        """Enable or disable a specific pattern."""
        self.patterns.enable_pattern(pattern_name, enabled)
        self.save_config()
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of current configuration."""
        return {
            'sensitivity_level': self.sensitivity.level.value,
            'patterns_enabled': len(self.patterns.get_enabled_patterns()),
            'colors_enabled': self.display.enable_colors,
            'chart_size': f"{self.display.chart_width}x{self.display.chart_height}",
            'config_file': str(self.config_file),
            'config_exists': self.config_file.exists()
        }
    
    def validate_config(self) -> Dict[str, list]:
        """Validate current configuration and return any issues."""
        issues = {
            'errors': [],
            'warnings': []
        }
        
        # Validate sensitivity settings
        if not (0.0 <= self.sensitivity.geometric_patterns <= 1.0):
            issues['errors'].append("Geometric patterns sensitivity must be between 0.0 and 1.0")
        
        if not (0.0 <= self.sensitivity.volume_confirmation_weight <= 1.0):
            issues['errors'].append("Volume confirmation weight must be between 0.0 and 1.0")
        
        # Validate display settings
        if self.display.chart_width < 40:
            issues['warnings'].append("Chart width is very small, may affect readability")
        
        if self.display.chart_height < 15:
            issues['warnings'].append("Chart height is very small, may affect pattern visibility")
        
        # Validate pattern settings
        if not any(self.patterns.enabled_patterns.values()):
            issues['errors'].append("No patterns are enabled")
        
        if self.patterns.max_total_patterns < 1:
            issues['errors'].append("Maximum total patterns must be at least 1")
        
        # Validate analysis settings
        if self.analysis.min_data_points < 10:
            issues['warnings'].append("Minimum data points is very low, may affect pattern detection")
        
        if self.analysis.max_data_points > 10000:
            issues['warnings'].append("Maximum data points is very high, may affect performance")
        
        return issues
    
    def _load_sensitivity_settings(self, data: Dict[str, Any]):
        """Load sensitivity settings from dictionary."""
        for field in fields(SensitivitySettings):
            if field.name in data:
                value = data[field.name]
                if field.name == 'level' and isinstance(value, str):
                    try:
                        value = SensitivityLevel(value)
                    except ValueError:
                        continue
                setattr(self.sensitivity, field.name, value)
    
    def _load_display_settings(self, data: Dict[str, Any]):
        """Load display settings from dictionary."""
        for field in fields(DisplaySettings):
            if field.name in data:
                setattr(self.display, field.name, data[field.name])
    
    def _load_pattern_settings(self, data: Dict[str, Any]):
        """Load pattern settings from dictionary."""
        for field in fields(PatternSettings):
            if field.name in data:
                setattr(self.patterns, field.name, data[field.name])
    
    def _load_analysis_settings(self, data: Dict[str, Any]):
        """Load analysis settings from dictionary."""
        for field in fields(AnalysisSettings):
            if field.name in data:
                setattr(self.analysis, field.name, data[field.name])
    
    def _serialize_settings(self, settings_obj) -> Dict[str, Any]:
        """Serialize settings object to dictionary."""
        data = asdict(settings_obj)
        
        # Handle enum serialization
        for key, value in data.items():
            if hasattr(value, 'value'):  # Enum
                data[key] = value.value
        
        return data
    
    def _setup_logging(self):
        """Setup logging based on analysis settings."""
        log_level = self.analysis.get_log_level_numeric()
        
        # Configure logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Add file handler if enabled
        if self.analysis.log_to_file:
            try:
                file_handler = logging.FileHandler(self.analysis.log_file_path)
                file_handler.setLevel(log_level)
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                file_handler.setFormatter(formatter)
                logging.getLogger().addHandler(file_handler)
            except Exception as e:
                logging.warning(f"Failed to setup file logging: {e}")
    
    def get_pattern_config(self, pattern_name: str) -> Dict[str, Any]:
        """Get configuration for a specific pattern."""
        pattern_key = pattern_name.lower()
        
        return {
            'enabled': self.patterns.is_pattern_enabled(pattern_key),
            'sensitivity': self.sensitivity.get_pattern_sensitivity('geometric'),  # Default category
            'min_confidence': self.sensitivity.get_min_confidence('geometric'),
            'require_volume': self.patterns.require_volume_confirmation,
            'min_duration': self.sensitivity.min_pattern_duration,
            'max_duration': self.sensitivity.max_pattern_duration
        }