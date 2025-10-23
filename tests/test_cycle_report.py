"""
Tests for Cycle Time Report Generator
"""

import pytest
from cycle_time_report import CycleTimeReport


class TestCycleTimeReport:
    """Test suite for cycle time report generation"""

    @pytest.fixture
    def sample_cycles(self):
        """Sample cycle data for testing"""
        return [
            {
                'id': 1,
                'start': '00:15.2',
                'end': '00:47.8',
                'total_duration': '32.6s',
                'phases': {
                    'dig': {'start': '00:15.2', 'end': '00:25.1', 'duration': '9.9s'},
                    'swing_to_dump': {'start': '00:25.1', 'end': '00:35.6', 'duration': '10.5s'},
                    'dump': {'start': '00:35.6', 'end': '00:40.2', 'duration': '4.6s'},
                    'return': {'start': '00:40.2', 'end': '00:47.8', 'duration': '7.6s'}
                }
            },
            {
                'id': 2,
                'start': '00:48.0',
                'end': '01:19.5',
                'total_duration': '31.5s',
                'phases': {
                    'dig': {'start': '00:48.0', 'end': '00:57.2', 'duration': '9.2s'},
                    'swing_to_dump': {'start': '00:57.2', 'end': '01:07.8', 'duration': '10.6s'},
                    'dump': {'start': '01:07.8', 'end': '01:12.1', 'duration': '4.3s'},
                    'return': {'start': '01:12.1', 'end': '01:19.5', 'duration': '7.4s'}
                }
            }
        ]

    @pytest.fixture
    def sample_summary(self):
        """Sample summary data for testing"""
        return {
            'total_cycles': '2',
            'average_cycle_time': '32.05s',
            'video_duration': '01:19.5',
            'fastest_cycle': {'id': '2', 'time': '31.5s'},
            'slowest_cycle': {'id': '1', 'time': '32.6s'}
        }

    def test_parse_duration(self):
        """Test duration parsing"""
        reporter = CycleTimeReport()
        
        assert reporter._parse_duration('9.9s') == 9.9
        assert reporter._parse_duration('32.6s') == 32.6
        assert reporter._parse_duration('0s') == 0.0
        assert reporter._parse_duration('invalid') == 0.0

    def test_calculate_metrics(self, sample_cycles):
        """Test metrics calculation"""
        reporter = CycleTimeReport()
        metrics = reporter._calculate_metrics(sample_cycles)
        
        assert metrics['avg_dig'] > 0
        assert metrics['avg_swing_to_dump'] > 0
        assert metrics['avg_dump'] > 0
        assert metrics['avg_return'] > 0
        assert metrics['avg_total'] > 0
        assert metrics['productivity_rate'] > 0

    def test_generate_markdown_report(self, sample_cycles, sample_summary):
        """Test markdown report generation"""
        reporter = CycleTimeReport()
        report = reporter.generate_markdown_report(
            cycles=sample_cycles,
            summary=sample_summary,
            metadata={'video_url': 'https://example.com/video'}
        )
        
        assert '# Excavator Cycle Time Analysis Report' in report
        assert 'Total Cycles Detected' in report
        assert 'Cycle 1' in report or '| 1 |' in report
        assert 'Performance Metrics' in report

    def test_generate_recommendations(self, sample_cycles):
        """Test recommendation generation"""
        reporter = CycleTimeReport()
        metrics = reporter._calculate_metrics(sample_cycles)
        recommendations = reporter._generate_recommendations(sample_cycles, metrics)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

    def test_empty_cycles(self):
        """Test handling empty cycle data"""
        reporter = CycleTimeReport()
        metrics = reporter._calculate_metrics([])
        
        assert metrics['avg_total'] == 0.0
        assert metrics['productivity_rate'] == 0.0

    def test_report_with_no_metadata(self, sample_cycles, sample_summary):
        """Test report generation without metadata"""
        reporter = CycleTimeReport()
        report = reporter.generate_markdown_report(
            cycles=sample_cycles,
            summary=sample_summary
        )
        
        assert '# Excavator Cycle Time Analysis Report' in report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

