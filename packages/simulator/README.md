# F1 Strategy Simulator - Directory Organization

## 📁 Directory Structure

The F1 Strategy Simulator codebase has been organized into a clean, modular structure for better maintainability and development workflow.

```
simulator/
├── 📂 api/                    # Web API & FastAPI application
│   └── api.py                 # Main FastAPI application with REST endpoints
├── 📂 core/                   # Core simulation & analysis modules
│   ├── circuit_pit_analyzer.py      # Circuit-specific pit loss analysis
│   ├── dynamic_pit_loss_calculator.py # Realistic pit loss calculations
│   ├── models.py                     # Pydantic data models for API
│   ├── pit_loss_analyzer.py          # Pit stop data analysis
│   ├── pit_strategy_simulator.py     # Main simulation engine
│   ├── strategy_analyzer.py          # Advanced strategy optimization
│   └── tire_performance_analyzer.py  # Tire compound analysis
├── 📂 visualization/          # Visualization components
│   ├── generate_all_visualizations.py # Comprehensive viz generator
│   ├── lap_time_visualizer.py        # Main visualization engine
│   └── quick_viz.py                  # Quick visualization tools
├── 📂 data_processing/        # Data fetching & processing
│   └── fetch_race_data.py     # OpenF1 API data fetcher
├── 📂 tests/                  # Comprehensive test suite
│   ├── 📂 unit/               # Unit tests for individual components
│   ├── 📂 integration/        # Integration & system tests
│   ├── 📂 execution/          # Test execution infrastructure
│   └── 📂 manual/             # Manual & development tests
├── 📂 utils/                  # Utility & helper scripts
│   └── debug_identical_strategies.py # Debugging tools
├── 📂 docs/                   # Documentation
│   ├── API_SPECIFICATION.md   # Complete API documentation
│   ├── HOW_TO_UPDATE_SIM.md   # Maintenance guide
│   └── VISUALIZATION_GUIDE.md # Visualization features guide
├── 📂 config/                 # Configuration files
│   └── requirements.txt       # Python dependencies
├── 📂 scripts/                # Example scripts & demos
│   └── demo_strategy_analysis.json # Example analysis output
├── 📂 data/                   # Race data & model coefficients
│   ├── *.csv                  # Race data files
│   └── *.json                 # Model coefficients & configurations
└── 📂 visualizations/         # Generated visualization outputs
    └── *.png                  # All generated charts & graphs
```

## 🚀 Quick Start

### Running Tests
```bash
# Run all tests
python3 run_tests.py all

# Run specific test categories
python3 run_tests.py unit
python3 run_tests.py integration
python3 run_tests.py visualization

# Run specific test file
python3 run_tests.py tests/unit/test_api.py
```

### Generating Visualizations
```bash
# Generate all visualizations
PYTHONPATH=. python3 visualization/generate_all_visualizations.py

# Quick visualization tools
PYTHONPATH=. python3 visualization/quick_viz.py overview
PYTHONPATH=. python3 visualization/quick_viz.py driver 1
```

### Running the API
```bash
# Start the FastAPI server
PYTHONPATH=. python3 -m uvicorn api.api:app --reload
```

## 📦 Module Overview

### 🔧 Core Modules
- **`pit_strategy_simulator.py`** - Main simulation engine comparing pit strategies
- **`strategy_analyzer.py`** - Advanced optimization and analysis tools
- **`models.py`** - Pydantic data models for API requests/responses
- **`dynamic_pit_loss_calculator.py`** - Realistic pit loss calculations
- **`tire_performance_analyzer.py`** - Data-driven tire performance analysis

### 📊 Visualization
- **`lap_time_visualizer.py`** - Comprehensive lap time visualization engine
- **`generate_all_visualizations.py`** - Batch visualization generator
- **`quick_viz.py`** - Command-line visualization tools

### 🌐 API
- **`api.py`** - FastAPI application with complete REST interface

### 🧪 Testing
- **Unit Tests** - Individual component testing
- **Integration Tests** - System-wide functionality testing
- **Execution Infrastructure** - Test runners and verification tools
- **Manual Tests** - Development and debugging tests

## 🔧 Development Guidelines

### Import Structure
All imports now use absolute paths from the package root:
```python
# Core modules
from core.pit_strategy_simulator import F1StrategySimulator
from core.models import PitStopRequest

# Visualization
from visualization.lap_time_visualizer import LapTimeVisualizer

# API
from api.api import app
```

### Adding New Features
1. **Core Logic** → Add to `core/`
2. **Visualizations** → Add to `visualization/`
3. **API Endpoints** → Extend `api/api.py`
4. **Tests** → Add appropriate tests in `tests/`
5. **Documentation** → Update relevant files in `docs/`

### PYTHONPATH Setup
For proper module resolution, always set PYTHONPATH to the simulator root:
```bash
export PYTHONPATH=/path/to/simulator
# OR
PYTHONPATH=. python3 your_script.py
```

## 📈 Recent Improvements

### Directory Organization Benefits
1. **Clear Separation of Concerns** - Each directory has a specific purpose
2. **Better Test Organization** - Tests are categorized by type and purpose
3. **Easier Navigation** - Related files are grouped together
4. **Scalable Structure** - Easy to add new components without clutter
5. **Professional Layout** - Follows Python package best practices

### Migration from Flat Structure
- All imports have been updated to use the new paths
- Test infrastructure has been preserved and enhanced
- Backward compatibility maintained through proper path handling
- Documentation updated to reflect new structure

## 🔍 File Roles Reference

| Directory | Purpose | Key Files |
|-----------|---------|-----------|
| `api/` | Web API interface | `api.py` |
| `core/` | Simulation engine | `pit_strategy_simulator.py`, `strategy_analyzer.py` |
| `visualization/` | Charts & graphs | `lap_time_visualizer.py` |
| `tests/` | Quality assurance | Various test files |
| `data/` | Race data & models | CSV files, JSON coefficients |
| `docs/` | Documentation | Markdown guides |
| `config/` | Configuration | `requirements.txt` |

## 📞 Support

For questions about the new structure or migration issues:
1. Check the documentation in `docs/`
2. Run tests to verify functionality: `python3 run_tests.py all`
3. Use the test runner for proper PYTHONPATH setup
4. Refer to import examples in this README