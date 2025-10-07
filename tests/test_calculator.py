# Author: Rajat Pednekar, UCID-rp2348

import datetime
from pathlib import Path
import pandas as pd
import pytest
from unittest.mock import Mock, patch, PropertyMock
from decimal import Decimal
from tempfile import TemporaryDirectory
from app.calculator import Calculator
from app.calculator_repl import calculator_repl
from app.calculator_config import CalculatorConfig
from app.exceptions import OperationError, ValidationError
from app.history import LoggingObserver, AutoSaveObserver
from app.operations import OperationFactory

# Fixture to initialize Calculator with a temporary directory for file paths
@pytest.fixture
def calculator():
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config = CalculatorConfig(base_dir=temp_path)

        # Patch properties to use the temporary directory paths
        with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
             patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file, \
             patch.object(CalculatorConfig, 'history_dir', new_callable=PropertyMock) as mock_history_dir, \
             patch.object(CalculatorConfig, 'history_file', new_callable=PropertyMock) as mock_history_file:
            
            # Set return values to use paths within the temporary directory
            mock_log_dir.return_value = temp_path / "logs"
            mock_log_file.return_value = temp_path / "logs/calculator.log"
            mock_history_dir.return_value = temp_path / "history"
            mock_history_file.return_value = temp_path / "history/calculator_history.csv"
            
            # Return an instance of Calculator with the mocked config
            yield Calculator(config=config)

# Test Calculator Initialization

def test_calculator_initialization(calculator):
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []
    assert calculator.operation_strategy is None

@patch('logging.basicConfig', side_effect=Exception("Logging setup failed"))
def test_calculator_logging_setup_failure(mock_logging):
    """Test calculator initialization when logging setup fails."""
    with pytest.raises(Exception, match="Logging setup failed"):
        Calculator()

@patch('app.calculator.logging.info')
def test_logging_setup(logging_info_mock):
    with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
         patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file:
        mock_log_dir.return_value = Path('/tmp/logs')
        mock_log_file.return_value = Path('/tmp/logs/calculator.log')
        
        calculator = Calculator(CalculatorConfig())
        logging_info_mock.assert_any_call("Calculator initialized with configuration")

@patch('app.calculator.pd.read_csv', side_effect=Exception("CSV read failed"))
@patch('app.calculator.Path.exists', return_value=True)
def test_calculator_load_history_failure_during_init(mock_exists, mock_read_csv):
    """Test calculator initialization when loading history fails."""
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config = CalculatorConfig(base_dir=temp_path)
        
        with patch.object(CalculatorConfig, 'history_dir', new_callable=PropertyMock) as mock_history_dir, \
             patch.object(CalculatorConfig, 'history_file', new_callable=PropertyMock) as mock_history_file:
            
            mock_history_dir.return_value = temp_path / "history"
            mock_history_file.return_value = temp_path / "history/calculator_history.csv"
            
            calc = Calculator(config=config)
            assert calc.history == []

# Test Observers

def test_add_observer(calculator):
    observer = LoggingObserver()
    calculator.add_observer(observer)
    assert observer in calculator.observers

def test_remove_observer(calculator):
    observer = LoggingObserver()
    calculator.add_observer(observer)
    calculator.remove_observer(observer)
    assert observer not in calculator.observers

# Test Operations

def test_set_operation(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    assert calculator.operation_strategy == operation

def test_perform_operation_addition(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    result = calculator.perform_operation(2, 3)
    assert result == Decimal('5')

def test_perform_operation_validation_error(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    with pytest.raises(ValidationError):
        calculator.perform_operation('invalid', 3)

def test_perform_operation_operation_error(calculator):
    with pytest.raises(OperationError, match="No operation set"):
        calculator.perform_operation(2, 3)

# Test Undo/Redo

def test_undo(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.undo()
    assert calculator.history == []

def test_undo_empty_history(calculator):
    """Test undo when history is empty."""
    result = calculator.undo()
    assert result is False
    assert calculator.history == []

def test_redo(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.undo()
    calculator.redo()
    assert len(calculator.history) == 1

def test_redo_empty_redo_stack(calculator):
    """Test redo when redo stack is empty."""
    result = calculator.redo()
    assert result is False

def test_multiple_undo_redo_operations(calculator):
    """Test multiple undo and redo operations."""
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.perform_operation(5, 5)
    calculator.perform_operation(10, 10)
    
    assert len(calculator.history) == 3
    
    calculator.undo()
    calculator.undo()
    assert len(calculator.history) == 1
    
    calculator.redo()
    assert len(calculator.history) == 2

def test_new_operation_clears_redo_stack(calculator):
    """Test that new operation clears redo stack."""
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    
    calculator.perform_operation(2, 3)
    calculator.undo()
    calculator.perform_operation(5, 5)
    
    result = calculator.redo()
    assert result is False

# Test History Management

@patch('app.calculator.pd.DataFrame.to_csv')
def test_save_history(mock_to_csv, calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.save_history()
    mock_to_csv.assert_called_once()

def test_save_history_empty(calculator):
    """Test saving empty history."""
    calculator.clear_history()
    calculator.save_history()
    
    assert calculator.config.history_file.exists()
    df = pd.read_csv(calculator.config.history_file)
    assert df.empty
    assert list(df.columns) == ['operation', 'operand1', 'operand2', 'result', 'timestamp']

def test_save_empty_history_creates_csv(calculator):
    """Test that saving empty history creates CSV with headers."""
    calculator.clear_history()
    
    if calculator.config.history_file.exists():
        calculator.config.history_file.unlink()
    
    calculator.save_history()
    
    assert calculator.config.history_file.exists()
    df = pd.read_csv(calculator.config.history_file)
    assert df.empty

def test_save_history_with_data(calculator):
    """Test saving history with actual calculations."""
    operation = OperationFactory.create_operation('multiply')
    calculator.set_operation(operation)
    calculator.perform_operation(3, 4)
    
    calculator.save_history()
    
    assert calculator.config.history_file.exists()
    df = pd.read_csv(calculator.config.history_file)
    assert len(df) == 1
    assert df.iloc[0]['operation'] == 'Multiplication'
    assert str(df.iloc[0]['result']) == '12'

@patch('app.calculator.pd.DataFrame.to_csv', side_effect=Exception("Write failed"))
def test_save_history_failure(mock_to_csv, calculator):
    """Test save_history when file write fails."""
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    
    with pytest.raises(OperationError, match="Failed to save history"):
        calculator.save_history()

@patch('app.calculator.pd.read_csv')
@patch('app.calculator.Path.exists', return_value=True)
def test_load_history(mock_exists, mock_read_csv, calculator):
    mock_read_csv.return_value = pd.DataFrame({
        'operation': ['Addition'],
        'operand1': ['2'],
        'operand2': ['3'],
        'result': ['5'],
        'timestamp': [datetime.datetime.now().isoformat()]
    })
    
    try:
        calculator.load_history()
        assert len(calculator.history) == 1
        assert calculator.history[0].operation == "Addition"
        assert calculator.history[0].operand1 == Decimal("2")
        assert calculator.history[0].operand2 == Decimal("3")
        assert calculator.history[0].result == Decimal("5")
    except OperationError:
        pytest.fail("Loading history failed due to OperationError")

def test_load_history_empty_file(calculator):
    """Test loading an empty history file."""
    calculator.config.history_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(columns=['operation', 'operand1', 'operand2', 'result', 'timestamp']
                ).to_csv(calculator.config.history_file, index=False)
    
    calculator.load_history()
    assert calculator.history == []

def test_load_history_no_file(calculator):
    """Test loading history when file doesn't exist."""
    if calculator.config.history_file.exists():
        calculator.config.history_file.unlink()
    
    calculator.load_history()
    assert calculator.history == []

@patch('app.calculator.pd.read_csv', side_effect=Exception("Read failed"))
@patch('app.calculator.Path.exists', return_value=True)
def test_load_history_failure(mock_exists, mock_read_csv, calculator):
    """Test load_history when file read fails."""
    with pytest.raises(OperationError, match="Failed to load history"):
        calculator.load_history()

def test_clear_history(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.clear_history()
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []

def test_history_size_limit(calculator):
    """Test that history respects max_history_size."""
    calculator.config.max_history_size = 3
    
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    
    for i in range(5):
        calculator.perform_operation(i, i)
    
    assert len(calculator.history) == 3
    assert calculator.history[0].operand1 == Decimal('2')

def test_get_history_dataframe_empty(calculator):
    """Test get_history_dataframe with empty history."""
    calculator.clear_history()
    df = calculator.get_history_dataframe()
    assert df.empty
    assert len(df) == 0

def test_get_history_dataframe_with_data(calculator):
    """Test get_history_dataframe with calculations."""
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.perform_operation(5, 5)
    
    df = calculator.get_history_dataframe()
    assert len(df) == 2
    assert list(df.columns) == ['operation', 'operand1', 'operand2', 'result', 'timestamp']
    assert df.iloc[0]['result'] == '5'
    assert df.iloc[1]['result'] == '10'

# REPL Tests

@patch('builtins.input', side_effect=['exit'])
@patch('builtins.print')
def test_calculator_repl_exit(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history') as mock_save_history:
        calculator_repl()
        mock_save_history.assert_called_once()
        mock_print.assert_any_call("History saved successfully.")
        mock_print.assert_any_call("Goodbye!")

@patch('builtins.input', side_effect=['help', 'exit'])
@patch('builtins.print')
def test_calculator_repl_help(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("\nAvailable commands:")

@patch('builtins.input', side_effect=['add', '2', '3', 'exit'])
@patch('builtins.print')
def test_calculator_repl_addition(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("\nResult: 5")

@patch('builtins.print')
@patch('builtins.input', side_effect=['history', 'exit'])
@patch('app.calculator.Calculator.load_history')
def test_calculator_repl_history_empty(mock_load, mock_input, mock_print):
    """Test REPL history command with empty history."""
    calculator_repl()
    mock_print.assert_any_call("No calculations in history")

@patch('builtins.input', side_effect=['clear', 'exit'])
@patch('builtins.print')
def test_calculator_repl_clear(mock_print, mock_input):
    """Test REPL clear command."""
    calculator_repl()
    mock_print.assert_any_call("History cleared")

@patch('builtins.input', side_effect=['undo', 'exit'])
@patch('builtins.print')
def test_calculator_repl_undo_empty(mock_print, mock_input):
    """Test REPL undo command with empty history."""
    calculator_repl()
    mock_print.assert_any_call("Nothing to undo")

@patch('builtins.input', side_effect=['redo', 'exit'])
@patch('builtins.print')
def test_calculator_repl_redo_empty(mock_print, mock_input):
    """Test REPL redo command with empty redo stack."""
    calculator_repl()
    mock_print.assert_any_call("Nothing to redo")

@patch('builtins.input', side_effect=['save', 'exit'])
@patch('builtins.print')
def test_calculator_repl_save(mock_print, mock_input):
    """Test REPL save command."""
    calculator_repl()
    mock_print.assert_any_call("History saved successfully")

@patch('builtins.input', side_effect=['load', 'exit'])
@patch('builtins.print')
def test_calculator_repl_load(mock_print, mock_input):
    """Test REPL load command."""
    calculator_repl()
    printed_calls = [str(call) for call in mock_print.call_args_list]
    assert any('History loaded' in str(call) or 'Error loading' in str(call) for call in printed_calls)

@patch('builtins.input', side_effect=['invalid_command', 'exit'])
@patch('builtins.print')
def test_calculator_repl_unknown_command(mock_print, mock_input):
    """Test REPL with unknown command."""
    calculator_repl()
    printed_calls = [str(call) for call in mock_print.call_args_list]
    assert any("Unknown command" in str(call) for call in printed_calls)

@patch('builtins.input', side_effect=['add', 'cancel', 'exit'])
@patch('builtins.print')
def test_calculator_repl_cancel_first_operand(mock_print, mock_input):
    """Test REPL canceling at first operand."""
    calculator_repl()
    mock_print.assert_any_call("Operation cancelled")

@patch('builtins.input', side_effect=['add', '5', 'cancel', 'exit'])
@patch('builtins.print')
def test_calculator_repl_cancel_second_operand(mock_print, mock_input):
    """Test REPL canceling at second operand."""
    calculator_repl()
    mock_print.assert_any_call("Operation cancelled")

@patch('builtins.input', side_effect=['divide', '10', '0', 'exit'])
@patch('builtins.print')
def test_calculator_repl_division_by_zero(mock_print, mock_input):
    """Test REPL handling division by zero error."""
    calculator_repl()
    printed_calls = [str(call) for call in mock_print.call_args_list]
    assert any("Error:" in str(call) for call in printed_calls)

@patch('builtins.input', side_effect=['add', 'invalid', '5', 'exit'])
@patch('builtins.print')
def test_calculator_repl_invalid_input(mock_print, mock_input):
    """Test REPL handling invalid input."""
    calculator_repl()
    printed_calls = [str(call) for call in mock_print.call_args_list]
    assert any("Error:" in str(call) for call in printed_calls)

@patch('builtins.input', side_effect=EOFError())
@patch('builtins.print')
def test_calculator_repl_eof_error(mock_print, mock_input):
    """Test REPL handling EOF (Ctrl+D)."""
    calculator_repl()
    printed_calls = [str(call) for call in mock_print.call_args_list]
    assert any("Input terminated" in str(call) for call in printed_calls)

@patch('app.calculator_repl.Calculator')
@patch('builtins.input', side_effect=['exit'])
@patch('builtins.print')
def test_repl_exit_save_error(mock_print, mock_input, mock_calc_class):
    """Test REPL exit when save fails."""
    mock_calc = Mock()
    mock_calc.save_history.side_effect = Exception("Save failed")
    mock_calc_class.return_value = mock_calc
    
    calculator_repl()
    
    printed = [str(call) for call in mock_print.call_args_list]
    assert any("Could not save history" in str(call) for call in printed)

@patch('app.calculator_repl.Calculator', side_effect=Exception("Fatal init error"))
@patch('builtins.print')
def test_repl_fatal_initialization_error(mock_print, mock_calc_class):
    """Test REPL with fatal initialization error."""
    with pytest.raises(Exception, match="Fatal init error"):
        calculator_repl()