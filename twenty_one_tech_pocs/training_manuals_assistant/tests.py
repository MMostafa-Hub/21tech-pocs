from django.test import TestCase
from unittest.mock import Mock, patch
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status

from .services import TrainingManualsAssistantService
from .schemas import TrainingManualAnalysisOutput, EquipmentQualificationProfile

class TrainingManualsAssistantServiceTests(TestCase):
    def setUp(self):
        self.service = TrainingManualsAssistantService()

    def test_temp_directory_creation(self):
        """Test that the temporary directory is created during service initialization."""
        import os
        self.assertTrue(os.path.exists(self.service.temp_dir))

    @patch('training_manuals_assistant.services.UnstructuredPDFLoader')
    def test_process_document_unsupported_format(self, mock_loader):
        """Test that non-PDF files are rejected."""
        mock_file = SimpleUploadedFile("test.txt", b"test content", content_type="text/plain")
        mock_llm = Mock()
        
        with self.assertRaises(ValueError) as context:
            self.service.process_document(mock_file, mock_llm)
        
        self.assertIn("Only PDF files are supported", str(context.exception))

    def tearDown(self):
        """Clean up any temporary files created during tests."""
        self.service.cleanup()

class ProcessTrainingManualViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_post_no_file_or_document_code(self):
        """Test that the endpoint returns an error when no file or document code is provided."""
        response = self.client.post('/api/training-manuals/process-training-manual/', {})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertIn("No document_code or training_manual_file provided", response.data["error"])

    def test_post_with_invalid_file(self):
        """Test that the endpoint handles invalid files gracefully."""
        invalid_file = SimpleUploadedFile("test.txt", b"test content", content_type="text/plain")
        
        with patch('training_manuals_assistant.views.ConfigManager') as mock_config_manager:
            mock_config_manager.return_value.get_llm_config.return_value = {"name": "gpt-4o"}
            
            with patch('training_manuals_assistant.views.LLMFactory') as mock_llm_factory:
                mock_llm_factory.return_value.get_llm.return_value = Mock()
                
                response = self.client.post(
                    '/api/training-manuals/process-training-manual/',
                    {'training_manual_file': invalid_file}
                )
                
                self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
