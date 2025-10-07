# tests/test_memento.py
# Author: Rajat Pednekar, UCID-rp2348

import pytest
from datetime import datetime
from decimal import Decimal
from app.calculator_memento import CalculatorMemento
from app.calculation import Calculation


class TestCalculatorMemento:
    """Test CalculatorMemento functionality."""

    @pytest.fixture
    def sample_calculations(self):
        """Fixture providing sample calculations."""
        return [
            Calculation(operation="Addition", operand1=Decimal("2"), operand2=Decimal("3")),
            Calculation(operation="Multiplication", operand1=Decimal("4"), operand2=Decimal("5")),
            Calculation(operation="Subtraction", operand1=Decimal("10"), operand2=Decimal("3"))
        ]

    def test_memento_creation(self, sample_calculations):
        """Test creating a memento with history."""
        memento = CalculatorMemento(history=sample_calculations)
        assert memento.history == sample_calculations
        assert isinstance(memento.timestamp, datetime)

    def test_memento_empty_history(self):
        """Test creating a memento with empty history."""
        memento = CalculatorMemento(history=[])
        assert memento.history == []
        assert isinstance(memento.timestamp, datetime)

    def test_memento_to_dict(self, sample_calculations):
        """Test converting memento to dictionary."""
        memento = CalculatorMemento(history=sample_calculations)
        memento_dict = memento.to_dict()
        
        assert 'history' in memento_dict
        assert 'timestamp' in memento_dict
        assert len(memento_dict['history']) == 3
        assert isinstance(memento_dict['timestamp'], str)

    def test_memento_to_dict_empty_history(self):
        """Test converting memento with empty history to dictionary."""
        memento = CalculatorMemento(history=[])
        memento_dict = memento.to_dict()
        
        assert memento_dict['history'] == []
        assert 'timestamp' in memento_dict

    def test_memento_from_dict(self, sample_calculations):
        """Test creating memento from dictionary."""
        original_memento = CalculatorMemento(history=sample_calculations)
        memento_dict = original_memento.to_dict()
        
        restored_memento = CalculatorMemento.from_dict(memento_dict)
        
        assert len(restored_memento.history) == len(original_memento.history)
        assert restored_memento.timestamp == original_memento.timestamp
        
        # Verify each calculation was restored correctly
        for original, restored in zip(original_memento.history, restored_memento.history):
            assert original.operation == restored.operation
            assert original.operand1 == restored.operand1
            assert original.operand2 == restored.operand2
            assert original.result == restored.result

    def test_memento_from_dict_empty_history(self):
        """Test creating memento from dictionary with empty history."""
        memento_dict = {
            'history': [],
            'timestamp': datetime.now().isoformat()
        }
        
        memento = CalculatorMemento.from_dict(memento_dict)
        assert memento.history == []
        assert isinstance(memento.timestamp, datetime)

    @pytest.mark.parametrize("num_calculations", [1, 3, 5, 10])
    def test_memento_various_history_sizes(self, num_calculations):
        """Test mementos with various history sizes."""
        calculations = [
            Calculation(operation="Addition", operand1=Decimal(str(i)), operand2=Decimal(str(i+1)))
            for i in range(num_calculations)
        ]
        
        memento = CalculatorMemento(history=calculations)
        assert len(memento.history) == num_calculations

    def test_memento_serialization_deserialization_roundtrip(self, sample_calculations):
        """Test that serialization and deserialization preserves data."""
        original = CalculatorMemento(history=sample_calculations)
        
        # Serialize to dict
        serialized = original.to_dict()
        
        # Deserialize back to memento
        restored = CalculatorMemento.from_dict(serialized)
        
        # Verify data integrity
        assert len(restored.history) == len(original.history)
        for orig_calc, rest_calc in zip(original.history, restored.history):
            assert orig_calc.operation == rest_calc.operation
            assert orig_calc.operand1 == rest_calc.operand1
            assert orig_calc.operand2 == rest_calc.operand2
            assert orig_calc.result == rest_calc.result

    def test_memento_timestamp_preservation(self, sample_calculations):
        """Test that timestamp is preserved during serialization."""
        memento = CalculatorMemento(history=sample_calculations)
        original_timestamp = memento.timestamp
        
        # Serialize and deserialize
        memento_dict = memento.to_dict()
        restored = CalculatorMemento.from_dict(memento_dict)
        
        assert restored.timestamp == original_timestamp
'''
    def test_memento_history_independence(self, sample_calculations):
        """Test that memento history is independent of original list."""
        original_list = sample_calculations.copy()
        memento = CalculatorMemento(history=original_list)
        
        # Modify original list
        original_list.append(
            Calculation(operation="Division", operand1=Decimal("10"), operand2=Decimal("2"))
        )
        
        # Memento should not be affected
        assert len(memento.history) == len(sample_calculations)
        assert len(memento.history) != len(original_list)
'''