#!/usr/bin/env python3
"""
Test suite for echo-tool
"""

import sys
import os
import json
import tempfile
import pytest
from io import StringIO
from unittest.mock import patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import after path modification
import importlib.util
spec = importlib.util.spec_from_file_location("echo_tool", "echo-tool.py")
echo_tool_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(echo_tool_module)
EchoTool = echo_tool_module.EchoTool


class TestEchoTool:
    """Test cases for echo-tool"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.tool = EchoTool()
        
    def test_basic_echo(self):
        """Test basic echo functionality"""
        with patch('sys.stdout', new=StringIO()) as mock_stdout:
            self.tool.run(['Hello World'])
            assert mock_stdout.getvalue().strip() == 'Hello World'
    
    def test_uppercase_transformation(self):
        """Test uppercase transformation"""
        with patch('sys.stdout', new=StringIO()) as mock_stdout:
            self.tool.run(['hello', '--upper'])
            assert mock_stdout.getvalue().strip() == 'HELLO'
    
    def test_lowercase_transformation(self):
        """Test lowercase transformation"""
        with patch('sys.stdout', new=StringIO()) as mock_stdout:
            self.tool.run(['HELLO', '--lower'])
            assert mock_stdout.getvalue().strip() == 'hello'
    
    def test_title_case_transformation(self):
        """Test title case transformation"""
        with patch('sys.stdout', new=StringIO()) as mock_stdout:
            self.tool.run(['hello world', '--title'])
            assert mock_stdout.getvalue().strip() == 'Hello World'
    
    def test_reverse_transformation(self):
        """Test reverse transformation"""
        with patch('sys.stdout', new=StringIO()) as mock_stdout:
            self.tool.run(['hello', '--reverse'])
            assert mock_stdout.getvalue().strip() == 'olleh'
    
    def test_prefix_suffix(self):
        """Test prefix and suffix formatting"""
        with patch('sys.stdout', new=StringIO()) as mock_stdout:
            self.tool.run(['test', '--prefix', '>>> ', '--suffix', ' <<<'])
            assert mock_stdout.getvalue().strip() == '>>> test <<<'
    
    def test_repeat(self):
        """Test repeat functionality"""
        with patch('sys.stdout', new=StringIO()) as mock_stdout:
            self.tool.run(['echo', '--repeat', '3'])
            output = mock_stdout.getvalue().strip().split('\n')
            assert len(output) == 3
            assert all(line == 'echo' for line in output)
    
    def test_line_numbers(self):
        """Test line numbering"""
        with patch('sys.stdout', new=StringIO()) as mock_stdout:
            self.tool.run(['line1\nline2', '--line-numbers'])
            output = mock_stdout.getvalue().strip().split('\n')
            assert output[0] == '1: line1'
            assert output[1] == '2: line2'
    
    def test_json_output(self):
        """Test JSON output format"""
        with patch('sys.stdout', new=StringIO()) as mock_stdout:
            self.tool.run(['test', '--json'])
            output = json.loads(mock_stdout.getvalue())
            assert output['input'] == 'test'
            assert output['output'] == 'test'
            assert 'transformations' in output
            assert 'formatting' in output
    
    def test_box_formatting(self):
        """Test ASCII box formatting"""
        with patch('sys.stdout', new=StringIO()) as mock_stdout:
            self.tool.run(['Hello', '--box'])
            output = mock_stdout.getvalue().strip().split('\n')
            assert output[0].startswith('┌')
            assert output[1].startswith('│')
            assert output[2].startswith('└')
            assert 'Hello' in output[1]
    
    def test_count_feature(self):
        """Test word/character counting"""
        with patch('sys.stdout', new=StringIO()) as mock_stdout:
            self.tool.run(['Hello World', '--count'])
            output = mock_stdout.getvalue()
            assert 'Characters: 11' in output
            assert 'Words: 2' in output
    
    def test_file_output(self):
        """Test output to file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_file = f.name
        
        try:
            with patch('sys.stdout', new=StringIO()) as mock_stdout:
                self.tool.run(['test content', '--output', temp_file])
                assert f'Output written to {temp_file}' in mock_stdout.getvalue()
            
            with open(temp_file, 'r') as f:
                assert f.read().strip() == 'test content'
        finally:
            os.unlink(temp_file)
    
    def test_file_append(self):
        """Test append to file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write('existing content\n')
            temp_file = f.name
        
        try:
            with patch('sys.stdout', new=StringIO()) as mock_stdout:
                self.tool.run(['new content', '--append', temp_file])
                assert f'Output appended to {temp_file}' in mock_stdout.getvalue()
            
            with open(temp_file, 'r') as f:
                content = f.read()
                assert 'existing content' in content
                assert 'new content' in content
        finally:
            os.unlink(temp_file)
    
    def test_piped_input(self):
        """Test handling of piped input"""
        with patch('sys.stdin', StringIO('piped text')):
            with patch('sys.stdin.isatty', return_value=False):
                with patch('sys.stdout', new=StringIO()) as mock_stdout:
                    self.tool.run([])
                    assert mock_stdout.getvalue().strip() == 'piped text'
    
    def test_combined_transformations(self):
        """Test combining multiple transformations"""
        with patch('sys.stdout', new=StringIO()) as mock_stdout:
            self.tool.run(['hello world', '--upper', '--reverse'])
            assert mock_stdout.getvalue().strip() == 'DLROW OLLEH'
    
    def test_complex_formatting(self):
        """Test complex formatting combinations"""
        with patch('sys.stdout', new=StringIO()) as mock_stdout:
            self.tool.run(['test', '--upper', '--prefix', '[', '--suffix', ']', '--repeat', '2'])
            output = mock_stdout.getvalue().strip().split('\n')
            assert len(output) == 2
            assert all(line == '[TEST]' for line in output)
    
    def test_multiline_input(self):
        """Test handling of multiline input"""
        with patch('sys.stdout', new=StringIO()) as mock_stdout:
            self.tool.run(['line1\nline2\nline3', '--upper'])
            output = mock_stdout.getvalue().strip()
            assert 'LINE1' in output
            assert 'LINE2' in output
            assert 'LINE3' in output
    
    def test_empty_input_handling(self):
        """Test handling of empty input"""
        # Empty string is valid input now
        with patch('sys.stdout', new=StringIO()) as mock_stdout:
            self.tool.run([''])
            assert mock_stdout.getvalue().strip() == ''
    
    def test_special_characters(self):
        """Test handling of special characters"""
        with patch('sys.stdout', new=StringIO()) as mock_stdout:
            self.tool.run(['!@#$%^&*()', '--upper'])
            assert mock_stdout.getvalue().strip() == '!@#$%^&*()'
    
    def test_unicode_support(self):
        """Test Unicode character support"""
        with patch('sys.stdout', new=StringIO()) as mock_stdout:
            self.tool.run(['Hello 世界 🌍', '--upper'])
            assert mock_stdout.getvalue().strip() == 'HELLO 世界 🌍'
    
    def test_json_with_counts(self):
        """Test JSON output with counts"""
        with patch('sys.stdout', new=StringIO()) as mock_stdout:
            self.tool.run(['Hello World', '--json', '--count'])
            output = json.loads(mock_stdout.getvalue())
            assert 'counts' in output
            assert output['counts']['words'] == 2
            assert output['counts']['characters'] == 11
    
    def test_error_handling_no_input(self):
        """Test error handling for no input"""
        # Simulate TTY (not piped) with no arguments
        with patch('sys.stdin.isatty', return_value=True):
            with patch('sys.stderr', new=StringIO()) as mock_stderr:
                with pytest.raises(SystemExit):
                    self.tool.run([])
    
    def test_rainbow_effect(self):
        """Test rainbow color effect (just ensure no crash)"""
        with patch('sys.stdout', new=StringIO()) as mock_stdout:
            self.tool.run(['rainbow', '--rainbow'])
            # Just check it produces output with ANSI codes
            output = mock_stdout.getvalue()
            assert '\033[' in output  # ANSI escape code
            # The word 'rainbow' is split with ANSI codes between each character


if __name__ == '__main__':
    pytest.main([__file__, '-v'])