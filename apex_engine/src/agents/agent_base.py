"""
Abstract Base Class for APEX Engine Agents.

This module provides the foundational structure for all agents in the
hierarchical agentic framework. Each agent inherits from BaseAgent and
implements domain-specific logic while sharing common patterns for:
- State management
- Error handling
- Logging
- Safe execution wrappers

Reference: Section 3 "The Agentic Hierarchy" from the framework documentation
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, TypeVar, Generic
from dataclasses import dataclass
from enum import Enum
import logging
import traceback
from datetime import datetime


class AgentRole(Enum):
    """Enumeration of agent roles in the APEX hierarchy."""
    EXECUTIVE = "executive"
    LYRICAL_ARCHITECT = "lyrical_architect"
    SONAUTO_OPERATOR = "sonauto_operator"
    FLOW_SUPERVISOR = "flow_supervisor"
    MIX_ENGINEER = "mix_engineer"
    FRISSON_DETECTOR = "frisson_detector"
    RHYME_ANALYZER = "rhyme_analyzer"
    GROOVE_ANALYZER = "groove_analyzer"
    TIMBRE_ANALYZER = "timbre_analyzer"
    SPECTRAL_ANALYZER = "spectral_analyzer"
    CONTEXT_ANALYZER = "context_analyzer"
    CULTURAL_ANALYST = "cultural_analyst"


@dataclass
class AgentResult:
    """
    Standardized result container for agent operations.
    
    All agents return this structure to ensure consistent
    error handling and state updates across the pipeline.
    """
    success: bool
    state_updates: Dict[str, Any]
    errors: List[str]
    warnings: List[str]
    execution_time_ms: float
    metadata: Dict[str, Any]
    
    @classmethod
    def success_result(
        cls, 
        state_updates: Dict[str, Any], 
        execution_time_ms: float = 0,
        warnings: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'AgentResult':
        """Create a successful result."""
        return cls(
            success=True,
            state_updates=state_updates,
            errors=[],
            warnings=warnings if warnings is not None else [],
            execution_time_ms=execution_time_ms,
            metadata=metadata if metadata is not None else {}
        )
    
    @classmethod
    def failure_result(
        cls, 
        errors: List[str], 
        execution_time_ms: float = 0,
        state_updates: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'AgentResult':
        """Create a failure result."""
        return cls(
            success=False,
            state_updates=state_updates if state_updates is not None else {},
            errors=errors,
            warnings=[],
            execution_time_ms=execution_time_ms,
            metadata=metadata if metadata is not None else {}
        )


class BaseAgent(ABC):
    """
    Abstract base class for all APEX Engine agents.
    
    Provides common infrastructure for:
    - Standardized execution flow with error handling
    - Logging with agent-specific context
    - State validation before and after execution
    - Performance monitoring
    
    Each specialized agent must implement:
    - role: The agent's role in the hierarchy
    - _execute: The core processing logic
    - _validate_input: Input state validation
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the agent with optional configuration.
        
        Args:
            config: Agent-specific configuration parameters
        """
        self.config = config or {}
        self.logger = self._setup_logger()
        self._execution_count = 0
        self._total_execution_time = 0.0
        
    def _setup_logger(self) -> logging.Logger:
        """Configure agent-specific logger with proper formatting."""
        logger = logging.getLogger(f"apex.{self.role.value}")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                f'[%(asctime)s] [{self.role.value.upper()}] %(levelname)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    @property
    @abstractmethod
    def role(self) -> AgentRole:
        """Return the agent's role in the hierarchy."""
        pass
    
    @property
    def name(self) -> str:
        """Human-readable name for the agent."""
        return self.role.value.replace('_', ' ').title()
    
    @abstractmethod
    def _execute(self, state: Dict[str, Any]) -> AgentResult:
        """
        Core execution logic to be implemented by each agent.
        
        Args:
            state: The current RapGenerationState
            
        Returns:
            AgentResult with state updates and status
        """
        pass
    
    @abstractmethod
    def _validate_input(self, state: Dict[str, Any]) -> List[str]:
        """
        Validate that required input state is present and valid.
        
        Args:
            state: The current RapGenerationState
            
        Returns:
            List of validation error messages (empty if valid)
        """
        pass
    
    def execute(self, state: Dict[str, Any]) -> AgentResult:
        """
        Main execution entry point with error handling and monitoring.
        
        This method wraps the agent's _execute method with:
        - Input validation
        - Error catching and reporting
        - Execution timing
        - Logging
        
        Args:
            state: The current RapGenerationState
            
        Returns:
            AgentResult with state updates and execution status
        """
        start_time = datetime.now()
        self._execution_count += 1
        
        self.logger.info(f"Starting execution #{self._execution_count}")
        
        try:
            validation_errors = self._validate_input(state)
            if validation_errors:
                self.logger.warning(f"Input validation failed: {validation_errors}")
                return AgentResult.failure_result(
                    errors=validation_errors,
                    execution_time_ms=self._calculate_elapsed(start_time)
                )
            
            result = self._execute(state)
            
            elapsed = self._calculate_elapsed(start_time)
            result.execution_time_ms = elapsed
            self._total_execution_time += elapsed
            
            if result.success:
                self.logger.info(f"Execution completed successfully in {elapsed:.2f}ms")
            else:
                self.logger.warning(f"Execution failed: {result.errors}")
                
            return result
            
        except Exception as e:
            elapsed = self._calculate_elapsed(start_time)
            error_msg = f"Unhandled exception: {str(e)}"
            self.logger.error(f"{error_msg}\n{traceback.format_exc()}")
            
            return AgentResult.failure_result(
                errors=[error_msg],
                execution_time_ms=elapsed,
                metadata={'exception_type': type(e).__name__}
            )
    
    def _calculate_elapsed(self, start_time: datetime) -> float:
        """Calculate elapsed time in milliseconds."""
        return (datetime.now() - start_time).total_seconds() * 1000
    
    def get_statistics(self) -> Dict[str, Any]:
        """Return execution statistics for this agent."""
        return {
            'agent': self.name,
            'role': self.role.value,
            'execution_count': self._execution_count,
            'total_execution_time_ms': self._total_execution_time,
            'avg_execution_time_ms': (
                self._total_execution_time / self._execution_count 
                if self._execution_count > 0 else 0
            )
        }


class AnalysisAgent(BaseAgent):
    """
    Base class for agents that perform analysis on audio or text.
    
    Provides additional infrastructure for:
    - Metric calculation
    - Threshold-based quality checks
    - Report generation
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.thresholds = self._load_thresholds()
        
    def _load_thresholds(self) -> Dict[str, float]:
        """Load quality thresholds from config or use defaults."""
        defaults = {
            'rhyme_factor_min': 0.5,
            'syllable_variance_max': 5.0,
            'bpm_deviation_max': 0.05,
            'onset_confidence_min': 0.7,
            'frisson_score_min': 0.3,
            'syncopation_index_min': 15,
            'syncopation_index_max': 50
        }
        return {**defaults, **self.config.get('thresholds', {})}
    
    def check_threshold(self, metric_name: str, value: float, higher_is_better: bool = True) -> bool:
        """
        Check if a metric value passes its threshold.
        
        Args:
            metric_name: Name of the metric to check
            value: The metric value
            higher_is_better: If True, value must be >= threshold
            
        Returns:
            True if the threshold is passed
        """
        threshold = self.thresholds.get(f"{metric_name}_min" if higher_is_better else f"{metric_name}_max")
        if threshold is None:
            return True
            
        if higher_is_better:
            return value >= threshold
        return value <= threshold


class GenerativeAgent(BaseAgent):
    """
    Base class for agents that generate content (lyrics, audio).
    
    Provides additional infrastructure for:
    - LLM integration
    - API client management
    - Retry logic
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.max_retries = self.config.get('max_retries', 3)
        self.retry_delay = self.config.get('retry_delay', 1.0)
        
    def with_retry(self, operation, *args, **kwargs):
        """
        Execute an operation with retry logic.
        
        Args:
            operation: The function to execute
            *args, **kwargs: Arguments to pass to the operation
            
        Returns:
            The result of the operation
            
        Raises:
            The last exception if all retries fail
        """
        import time
        
        last_exception: Optional[Exception] = None
        for attempt in range(self.max_retries):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                last_exception = e
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))
                    
        if last_exception is not None:
            raise last_exception
        raise RuntimeError("Retry logic failed without capturing exception")
