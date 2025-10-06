# Advanced Calculator Application

A sophisticated, modular calculator application built with Python that integrates advanced design patterns, persistent data management via pandas, and full test automation with GitHub Actions.

## Features

### Core Functionality
- **REPL Interface**: Interactive Read-Eval-Print Loop for continuous user interaction
- **Advanced Arithmetic Operations**: 
  - Addition
  - Subtraction
  - Multiplication
  - Division (with zero-division protection)
  - Power (exponentiation)
  - Root (nth root calculation)

### Design Patterns Implementation
- **Observer Pattern**: Monitors and reacts to calculation events (logging, auto-saving)
- **Memento Pattern**: Enables undo/redo functionality by preserving application state
- **Strategy Pattern**: Interchangeable operation execution strategies
- **Factory Pattern**: Dynamic operation instantiation based on user input
- **Facade Pattern**: Simplified interface to complex subsystems

### Data Management
- **pandas Integration**: DataFrames for calculation history storage and manipulation
- **Auto-Save/Load**: Automatic persistence of calculation history to CSV files
- **History Management**: Complete calculation history with timestamps

### Configuration Management
- **Environment Variables**: Configuration via `.env` file using python-dotenv
- **Validation**: Comprehensive configuration validation with error handling
- **Flexible Settings**: Customizable precision, history size, and file paths



## Requirements

- Python 3.8+
- pandas
- pytest
- pytest-cov
- python-dotenv

## Installation## Installation

### 0. Clone the Repository
```bash
git clone https://github.com/Rajat-njit/calculator.git
cd calculator
```
### 1. Create and Activate Virtual Environment

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root directory:

```env
# Calculator Configuration
CALCULATOR_MAX_HISTORY_SIZE=1000
CALCULATOR_AUTO_SAVE=true
CALCULATOR_PRECISION=10
CALCULATOR_MAX_INPUT_VALUE=1e999
CALCULATOR_DEFAULT_ENCODING=utf-8

# Directory Configuration (optional - defaults to project directories)
# CALCULATOR_BASE_DIR=/path/to/base
# CALCULATOR_LOG_DIR=/path/to/logs
# CALCULATOR_HISTORY_DIR=/path/to/history
```

## Usage

### Running the Calculator

```bash
python main.py
```

### Available Commands

Once the calculator is running, you can use the following commands:

#### Arithmetic Operations
```
> add 5 3
Result: 8

> subtract 10 4
Result: 6

> multiply 6 7
Result: 42

> divide 15 3
Result: 5

> power 2 8
Result: 256

> root 27 3
Result: 3
```

#### History Management
```
> history
Display all calculation history

> clear
Clear calculation history

> save
Manually save history to CSV file

> load
Reload history from CSV file
```

#### Undo/Redo Operations
```
> undo
Undo the last calculation

> redo
Redo the previously undone calculation
```

#### Other Commands
```
> help
Display available commands and usage instructions

> exit
Exit the calculator application
```

## Project Structure

```
ASSIGNMENT_5/
│
├── .github/
│   └── workflows/
│       └── tests.yml              # GitHub Actions CI/CD workflow
│
├── app/
│   ├── __init__.py
│   ├── calculation.py             # Calculation model (Value Object)
│   ├── calculator.py              # Main Calculator class (Facade)
│   ├── calculator_config.py       # Configuration management
│   ├── calculator_memento.py      # Memento pattern for undo/redo
│   ├── calculator_repl.py         # REPL interface
│   ├── exceptions.py              # Custom exception classes
│   ├── history.py                 # Observer pattern implementation
│   ├── input_validators.py        # Input validation utilities
│   └── operations.py              # Operation strategies (Strategy pattern)
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # pytest configuration and fixtures
│   ├── test_calculation.py        # Tests for Calculation class
│   ├── test_calculator.py         # Tests for Calculator class
│   ├── test_config.py             # Tests for configuration
│   ├── test_exceptions.py         # Tests for custom exceptions
│   ├── test_history.py            # Tests for history/observer pattern
│   ├── test_memento.py            # Tests for memento pattern
│   ├── test_operations.py         # Tests for operations
│   └── test_validators.py         # Tests for input validators
│
├── history/                       # Calculation history storage
│   └── calculator_history.csv
│
├── logs/                          # Application logs
│   └── (log files generated here)
│
├── test_history/                  # Test history files
├── test_logs/                     # Test log files
├── htmlcov/                       # Coverage report directory
│
├── .coverage                      # Coverage data file
├── .env                           # Environment configuration (create this)
├── .gitignore                     # Git ignore rules
├── main.py                        # Main entry point
├── pytest.ini                     # pytest configuration
└── README.md                      # This file
```

## Testing

### Run All Tests

```bash
pytest
```

### Run Tests with Coverage

```bash
pytest --cov=app tests/
```

### Generate HTML Coverage Report

```bash
pytest --cov=app --cov-report=html tests/
```

This generates an HTML coverage report in the `htmlcov/` directory.

### Check Coverage Threshold

```bash
coverage report --fail-under=100
```

### View Coverage Report

After generating the HTML report, open `htmlcov/index.html` in your browser to view detailed coverage information.

## Continuous Integration

This project uses GitHub Actions for automated testing and coverage checking. The CI pipeline:

1. Runs on every push and pull request to the `main` branch
2. Sets up Python environment
3. Installs dependencies
4. Runs all tests with coverage
5. Enforces 100% test coverage requirement

### GitHub Actions Workflow

The workflow is defined in `.github/workflows/tests.yml` and automatically:
- Tests the application on Ubuntu latest
- Generates coverage reports
- Fails the build if coverage is below the required threshold

## Design Patterns

### 1. Observer Pattern (`history.py`)
Observers monitor calculation events and react accordingly (e.g., logging, auto-saving to history files).

**Implementation:**
- `HistoryObserver` abstract base class defines the observer interface
- Concrete observers implement the `update()` method
- Calculator notifies all registered observers when calculations occur

### 2. Memento Pattern (`calculator_memento.py`)
Captures and restores calculator state for undo/redo functionality.

**Implementation:**
- `CalculatorMemento` stores calculator history snapshots
- `undo_stack` and `redo_stack` manage state history
- Allows rolling back to previous calculation states

### 3. Strategy Pattern (`operations.py`)
Each operation (add, subtract, etc.) implements the same interface, allowing dynamic operation selection.

**Implementation:**
- `Operation` abstract base class defines the strategy interface
- Concrete operation classes implement `execute()` method
- Calculator can switch between operations at runtime

### 4. Factory Pattern (`operations.py`)
The OperationFactory creates appropriate operation instances based on user input.

**Implementation:**
- `OperationFactory` class with `create_operation()` method
- Maps operation names/symbols to operation classes
- Encapsulates object creation logic


## Configuration Options

All configuration options can be set via environment variables in the `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `CALCULATOR_MAX_HISTORY_SIZE` | 1000 | Maximum number of calculations to store |
| `CALCULATOR_AUTO_SAVE` | true | Auto-save history after each calculation |
| `CALCULATOR_PRECISION` | 10 | Decimal precision for calculations |
| `CALCULATOR_MAX_INPUT_VALUE` | 1e999 | Maximum allowed input value |
| `CALCULATOR_DEFAULT_ENCODING` | utf-8 | File encoding for CSV files |
| `CALCULATOR_BASE_DIR` | project root | Base directory for calculator files |
| `CALCULATOR_LOG_DIR` | logs/ | Directory for log files |
| `CALCULATOR_HISTORY_DIR` | history/ | Directory for history files |

## Author
**Rajat Pednekar - Assignment: 5***
