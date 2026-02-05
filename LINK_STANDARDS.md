# DuggerLinkTools Standards

## Pydantic Migration Standards for Trading & Automation Projects

### Core Principles

1. **Schema-First Development**: Define Pydantic models before implementing logic
2. **Type Safety**: Use native Python 3.11+ types (`dict`, `list`, `| None`)
3. **Validation at Boundaries**: Validate all external data at system entry points
4. **Circular Import Prevention**: DLT is the bottom of the stack - never imports from DGT/DBT

### Migration Strategy

#### Phase 1: Core Extraction ✅
- Extract `@ttl_cache` and `DuggerToolError` from DGT
- Establish DLT as independent foundation
- Create `DuggerProject` model as canonical schema

#### Phase 2: Schema Definition
- Identify data contracts in existing projects
- Create Pydantic models for:
  - Trading strategies
  - Market data
  - Configuration files
  - API request/response schemas
  - System state

#### Phase 3: Gradual Migration
- Replace ad-hoc validation with Pydantic models
- Update existing functions to use typed models
- Maintain backward compatibility during transition

### Model Design Standards

#### Naming Conventions
```python
# Use descriptive, domain-specific names
class TradingStrategy(BaseModel):  # ✅ Good
class Strategy(BaseModel):         # ❌ Too generic

class MarketDataSnapshot(BaseModel):  # ✅ Specific
class Data(BaseModel):                # ❌ Ambiguous
```

#### Field Validation
```python
from pydantic import BaseModel, Field, field_validator
from typing import Literal
from enum import Enum

class TradingSignal(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10)
    action: Literal["BUY", "SELL", "HOLD"]
    confidence: float = Field(..., ge=0.0, le=1.0)
    timestamp: datetime
    
    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, v: str) -> str:
        return v.upper().strip()
```

#### Error Handling
```python
from duggerlink import DuggerToolError

# Use DuggerToolError for tool-specific failures
def execute_trade(symbol: str, quantity: int) -> TradeResult:
    try:
        # Trading logic
        pass
    except BrokerError as e:
        raise DuggerToolError(
            tool_name="broker_api",
            command=["trade", symbol, str(quantity)],
            message=f"Trade execution failed: {e}"
        )
```

### Integration Patterns

#### Configuration Management
```python
# duggerlink/models/config.py
class TradingConfig(BaseModel):
    api_key: str = Field(..., exclude_from_repr=True)
    max_position_size: int = Field(default=1000, ge=1)
    risk_tolerance: float = Field(default=0.02, ge=0.0, le=1.0)
    enabled_strategies: list[str]
    
    @classmethod
    def from_file(cls, path: Path) -> TradingConfig:
        """Load config from YAML/JSON file."""
        # Implementation with validation
        pass
```

#### Data Pipeline Validation
```python
# Market data validation
class MarketData(BaseModel):
    symbol: str
    price: float = Field(..., gt=0)
    volume: int = Field(..., ge=0)
    timestamp: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Use in data pipelines
def process_market_data(raw_data: dict) -> MarketData:
    """Validate and process raw market data."""
    try:
        return MarketData(**raw_data)
    except ValidationError as e:
        raise DuggerToolError(
            tool_name="market_data_processor",
            command=["validate", str(raw_data)],
            message=f"Invalid market data: {e}"
        )
```

### Testing Standards

#### Model Testing
```python
def test_trading_model_validation():
    """Test Pydantic model validation."""
    # Valid data
    signal = TradingSignal(
        symbol="AAPL",
        action="BUY",
        confidence=0.85,
        timestamp=datetime.now()
    )
    assert signal.symbol == "AAPL"
    
    # Invalid data
    with pytest.raises(ValidationError):
        TradingSignal(
            symbol="",  # Invalid: empty string
            action="INVALID",  # Invalid: not in Literal
            confidence=1.5,  # Invalid: > 1.0
            timestamp=datetime.now()
        )
```

#### Integration Testing
```python
def test_config_loading():
    """Test configuration loading with validation."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as f:
        yaml.dump({
            'api_key': 'test_key',
            'max_position_size': 500,
            'risk_tolerance': 0.01,
            'enabled_strategies': ['momentum', 'mean_reversion']
        }, f)
        f.flush()
        
        config = TradingConfig.from_file(Path(f.name))
        assert config.max_position_size == 500
        assert len(config.enabled_strategies) == 2
```

### Performance Considerations

#### Caching Strategy
```python
from duggerlink import ttl_cache

@ttl_cache(ttl_seconds=60)  # Cache for 1 minute
def get_market_data(symbol: str) -> MarketData:
    """Fetch and validate market data with caching."""
    raw_data = fetch_from_api(symbol)
    return MarketData(**raw_data)
```

#### Bulk Operations
```python
from typing import Iterable
from pydantic import TypeAdapter

# Efficient bulk validation
market_data_adapter = TypeAdapter(list[MarketData])

def validate_bulk_market_data(raw_data_list: list[dict]) -> list[MarketData]:
    """Validate multiple market data entries efficiently."""
    try:
        return market_data_adapter.validate_python(raw_data_list)
    except ValidationError as e:
        raise DuggerToolError(
            tool_name="bulk_validator",
            command=["validate_bulk", str(len(raw_data_list))],
            message=f"Bulk validation failed: {e}"
        )
```

### Deployment Guidelines

#### Local Development
```bash
# Install DLT in editable mode
pip install -e C:\Github\DuggerLinkTools

# Use in projects
from duggerlink import DuggerProject, DuggerToolError, ttl_cache
```

#### Production Dependencies
```toml
# pyproject.toml
[project]
dependencies = [
    "duggerlink>=0.1.0",
    "pydantic>=2.0.0",
    # Other project-specific dependencies
]
```

### Migration Checklist

#### For Each Project
- [ ] Identify data structures that need Pydantic models
- [ ] Create models in `models/` directory
- [ ] Replace manual validation with Pydantic validation
- [ ] Update function signatures to use typed models
- [ ] Add comprehensive tests for new models
- [ ] Update documentation with new schema definitions

#### Validation Steps
- [ ] All external data is validated at entry points
- [ ] No circular imports (DLT → DGT/DBT)
- [ ] Native Python 3.11+ types used throughout
- [ ] Tests cover both valid and invalid data scenarios
- [ ] Performance benchmarks meet requirements

### Common Patterns

#### API Client Pattern
```python
class APIClientConfig(BaseModel):
    base_url: str = Field(..., url_scheme="https")
    timeout: int = Field(default=30, ge=1)
    retry_attempts: int = Field(default=3, ge=0)

class APIClient:
    def __init__(self, config: APIClientConfig) -> None:
        self.config = config
        self.session = requests.Session()
        self.session.timeout = config.timeout
    
    @ttl_cache(ttl_seconds=config.cache_ttl)
    def get_data(self, endpoint: str) -> DataModel:
        """Fetch and validate API data."""
        response = self.session.get(f"{self.config.base_url}/{endpoint}")
        response.raise_for_status()
        return DataModel(**response.json())
```

#### Strategy Pattern
```python
class StrategyConfig(BaseModel):
    name: str
    parameters: dict[str, Any]
    enabled: bool = True

class TradingStrategy:
    def __init__(self, config: StrategyConfig) -> None:
        self.config = config
    
    def generate_signal(self, market_data: MarketData) -> TradingSignal:
        """Generate trading signal from market data."""
        if not self.config.enabled:
            raise DuggerToolError(
                tool_name="strategy",
                command=["generate_signal", self.config.name],
                message="Strategy is disabled"
            )
        
        # Strategy implementation
        pass
```

This framework ensures consistent, type-safe, and validated data structures across all trading and automation projects in the Dugger ecosystem.