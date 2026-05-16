"""Tests for Phase 1: Environment and Config Validation (using unittest)."""

import os
import unittest
from unittest.mock import patch
from src.settings import Settings
from src.validation import validate_environment

class TestPhase1(unittest.TestCase):

    def test_default_safety_modes(self):
        """Test that safety modes default to True."""
        settings = Settings()
        self.assertTrue(settings.is_dry_run())
        self.assertTrue(settings.is_safety_mode())

    def test_validation_logic(self):
        """Test that validation fails when required vars are missing."""
        # Mock environment to ensure required vars are missing
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            # Clear internal settings just in case
            settings.settings = settings.DEFAULT_SETTINGS.copy()
            results = settings.validate()
            
            self.assertFalse(results['valid'])
            self.assertTrue(any("GOOGLE_SERVICE_ACCOUNT_JSON" in err for err in results['errors']))

    def test_validation_warnings(self):
        """Test that warnings are generated when safety modes are disabled."""
        settings = Settings()
        settings.set('automation.dry_run', False)
        settings.set('automation.safety_mode', False)
        
        results = settings.validate()
        self.assertTrue(any("DRY_RUN is disabled" in warn for warn in results['warnings']))
        self.assertTrue(any("SAFETY_MODE is disabled" in warn for warn in results['warnings']))

    def test_validate_environment_wrapper(self):
        """Test the validate_environment wrapper function."""
        with patch.dict(os.environ, {"NODE_ENV": "production"}):
            results = validate_environment()
            self.assertEqual(results['environment'], "production")

if __name__ == "__main__":
    unittest.main()
