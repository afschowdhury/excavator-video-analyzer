"""
Tests for POML Parser functionality
"""

import pytest
from prompts import POMLParser


class TestPOMLParser:
    """Test suite for POML parsing"""

    def test_parse_cycles_single_cycle(self):
        """Test parsing a single cycle"""
        poml_text = """
        <cycle id="1" start="00:15.2" end="00:47.8" total_duration="32.6s">
          <dig start="00:15.2" end="00:25.1" duration="9.9s" description="Bucket descends"/>
          <swing_to_dump start="00:25.1" end="00:35.6" duration="10.5s" description="Swing to dump"/>
          <dump start="00:35.6" end="00:40.2" duration="4.6s" description="Release material"/>
          <return start="00:40.2" end="00:47.8" duration="7.6s" description="Return to dig"/>
        </cycle>
        """
        
        parser = POMLParser()
        cycles = parser.parse_cycles(poml_text)
        
        assert len(cycles) == 1
        assert cycles[0]['id'] == 1
        assert cycles[0]['start'] == "00:15.2"
        assert cycles[0]['end'] == "00:47.8"
        assert cycles[0]['total_duration'] == "32.6s"
        assert 'phases' in cycles[0]
        assert 'dig' in cycles[0]['phases']
        assert cycles[0]['phases']['dig']['duration'] == "9.9s"

    def test_parse_cycles_multiple_cycles(self):
        """Test parsing multiple cycles"""
        poml_text = """
        <cycle id="1" start="00:15.2" end="00:47.8" total_duration="32.6s">
          <dig start="00:15.2" end="00:25.1" duration="9.9s"/>
          <swing_to_dump start="00:25.1" end="00:35.6" duration="10.5s"/>
        </cycle>
        <cycle id="2" start="00:48.0" end="01:19.5" total_duration="31.5s">
          <dig start="00:48.0" end="00:57.2" duration="9.2s"/>
          <swing_to_dump start="00:57.2" end="01:07.8" duration="10.6s"/>
        </cycle>
        """
        
        parser = POMLParser()
        cycles = parser.parse_cycles(poml_text)
        
        assert len(cycles) == 2
        assert cycles[0]['id'] == 1
        assert cycles[1]['id'] == 2

    def test_parse_summary(self):
        """Test parsing summary section"""
        poml_text = """
        <summary>
          <total_cycles>12</total_cycles>
          <video_duration>05:30</video_duration>
          <average_cycle_time>38.5s</average_cycle_time>
          <fastest_cycle id="5" time="31.2s">5</fastest_cycle>
          <slowest_cycle id="9" time="45.8s">9</slowest_cycle>
        </summary>
        """
        
        parser = POMLParser()
        summary = parser.parse_summary(poml_text)
        
        assert 'total_cycles' in summary
        assert summary['total_cycles'] == "12"
        assert summary['average_cycle_time'] == "38.5s"

    def test_parse_evaluation(self):
        """Test parsing evaluation section"""
        poml_text = """
        <evaluation>
          <control_precision score="85/100">
            <strength timestamp="00:25.3">Smooth coordinated movement</strength>
            <improvement timestamp="00:42.1">Practice smoother control</improvement>
          </control_precision>
          <efficiency score="78/100">
            <strength timestamp="00:30.0">Optimal swing path</strength>
          </efficiency>
        </evaluation>
        """
        
        parser = POMLParser()
        evaluation = parser.parse_evaluation(poml_text)
        
        assert 'control_precision' in evaluation
        assert evaluation['control_precision']['score'] == "85/100"
        assert len(evaluation['control_precision']['strengths']) == 1
        assert len(evaluation['control_precision']['improvements']) == 1
        assert evaluation['efficiency']['score'] == "78/100"

    def test_extract_plain_text(self):
        """Test extracting plain text from POML"""
        poml_text = """
        <cycle id="1">
          <dig>Some content</dig>
        </cycle>
        More text here
        """
        
        parser = POMLParser()
        plain_text = parser.extract_plain_text(poml_text)
        
        assert "<cycle" not in plain_text
        assert "<dig>" not in plain_text
        assert "Some content" in plain_text

    def test_parse_empty_cycles(self):
        """Test parsing when no cycles are present"""
        poml_text = "Some text without any cycle markup"
        
        parser = POMLParser()
        cycles = parser.parse_cycles(poml_text)
        
        assert len(cycles) == 0

    def test_parse_empty_summary(self):
        """Test parsing when no summary is present"""
        poml_text = "Some text without any summary markup"
        
        parser = POMLParser()
        summary = parser.parse_summary(poml_text)
        
        assert len(summary) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

