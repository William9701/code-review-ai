"""
Database models for CodeReview AI Assistant
"""

from datetime import datetime
from enum import Enum as PyEnum
from typing import List, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class AnalysisStatus(str, PyEnum):
    """Analysis status enumeration"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class IssueSeverity(str, PyEnum):
    """Issue severity levels"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class IssueCategory(str, PyEnum):
    """Issue category types"""

    SECURITY = "security"
    PERFORMANCE = "performance"
    CODE_QUALITY = "code_quality"
    BEST_PRACTICES = "best_practices"
    MAINTAINABILITY = "maintainability"


class Repository(Base):
    """GitHub repository model"""

    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    github_id = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    full_name = Column(String(512), nullable=False)
    owner = Column(String(255), nullable=False)
    installation_id = Column(Integer, nullable=False, index=True)
    default_branch = Column(String(255), default="main")
    is_active = Column(Boolean, default=True)
    config = Column(JSON, nullable=True)  # Repository-specific configuration
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    pull_requests = relationship("PullRequest", back_populates="repository")

    def __repr__(self):
        return f"<Repository {self.full_name}>"


class PullRequest(Base):
    """GitHub pull request model"""

    __tablename__ = "pull_requests"

    id = Column(Integer, primary_key=True, index=True)
    github_id = Column(Integer, unique=True, nullable=False, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    pr_number = Column(Integer, nullable=False)
    title = Column(String(512), nullable=False)
    description = Column(Text, nullable=True)
    author = Column(String(255), nullable=False)
    base_branch = Column(String(255), nullable=False)
    head_branch = Column(String(255), nullable=False)
    base_sha = Column(String(40), nullable=False)
    head_sha = Column(String(40), nullable=False)
    state = Column(String(50), nullable=False)  # open, closed, merged
    is_draft = Column(Boolean, default=False)
    files_changed = Column(Integer, default=0)
    additions = Column(Integer, default=0)
    deletions = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    repository = relationship("Repository", back_populates="pull_requests")
    analyses = relationship("Analysis", back_populates="pull_request")

    # Indexes
    __table_args__ = (Index("idx_pr_repo_number", "repository_id", "pr_number"),)

    def __repr__(self):
        return f"<PullRequest #{self.pr_number} - {self.title}>"


class Analysis(Base):
    """Code analysis job model"""

    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    pull_request_id = Column(Integer, ForeignKey("pull_requests.id"), nullable=False)
    status = Column(Enum(AnalysisStatus), default=AnalysisStatus.PENDING, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    total_issues = Column(Integer, default=0)
    critical_issues = Column(Integer, default=0)
    high_issues = Column(Integer, default=0)
    medium_issues = Column(Integer, default=0)
    low_issues = Column(Integer, default=0)
    info_issues = Column(Integer, default=0)
    files_analyzed = Column(Integer, default=0)
    analysis_duration_seconds = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)
    extra_data = Column(JSON, nullable=True)  # Renamed from metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    pull_request = relationship("PullRequest", back_populates="analyses")
    issues = relationship("Issue", back_populates="analysis")

    def __repr__(self):
        return f"<Analysis {self.id} - {self.status}>"


class Issue(Base):
    """Code issue/finding model"""

    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False)
    file_path = Column(String(1024), nullable=False)
    line_start = Column(Integer, nullable=False)
    line_end = Column(Integer, nullable=True)
    column_start = Column(Integer, nullable=True)
    column_end = Column(Integer, nullable=True)
    severity = Column(Enum(IssueSeverity), nullable=False, index=True)
    category = Column(Enum(IssueCategory), nullable=False, index=True)
    rule_id = Column(String(255), nullable=False, index=True)
    title = Column(String(512), nullable=False)
    description = Column(Text, nullable=False)
    code_snippet = Column(Text, nullable=True)
    suggested_fix = Column(Text, nullable=True)
    explanation = Column(Text, nullable=True)  # LLM-generated explanation
    references = Column(JSON, nullable=True)  # Links to documentation, etc.
    is_false_positive = Column(Boolean, default=False)
    github_comment_id = Column(Integer, nullable=True)  # ID of GitHub comment
    extra_data = Column(JSON, nullable=True)  # Renamed from metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    analysis = relationship("Analysis", back_populates="issues")

    # Indexes
    __table_args__ = (
        Index("idx_issue_severity_category", "severity", "category"),
        Index("idx_issue_file_path", "file_path"),
    )

    def __repr__(self):
        return f"<Issue {self.rule_id} - {self.severity}>"


class AnalysisRule(Base):
    """Analysis rule configuration"""

    __tablename__ = "analysis_rules"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(512), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(Enum(IssueCategory), nullable=False)
    default_severity = Column(Enum(IssueSeverity), nullable=False)
    language = Column(String(50), nullable=True)  # python, typescript, etc.
    is_enabled = Column(Boolean, default=True)
    pattern = Column(Text, nullable=True)  # Regex or AST pattern
    config = Column(JSON, nullable=True)  # Rule-specific configuration
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<AnalysisRule {self.rule_id}>"


class AuditLog(Base):
    """Audit log for tracking system events"""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    event_source = Column(String(100), nullable=False)  # Service name
    user_id = Column(String(255), nullable=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=True)
    pull_request_id = Column(Integer, ForeignKey("pull_requests.id"), nullable=True)
    event_data = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(512), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)

    def __repr__(self):
        return f"<AuditLog {self.event_type} - {self.created_at}>"


class APIKey(Base):
    """API keys for authentication"""

    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key_hash = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(String(255), nullable=False)
    scopes = Column(JSON, nullable=False)  # List of permissions
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<APIKey {self.name}>"


class AnalyticsMetric(Base):
    """Analytics and metrics tracking"""

    __tablename__ = "analytics_metrics"

    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(255), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=True)
    dimensions = Column(JSON, nullable=True)  # Additional dimensions for grouping
    timestamp = Column(DateTime, server_default=func.now(), index=True)

    # Indexes
    __table_args__ = (Index("idx_metric_name_timestamp", "metric_name", "timestamp"),)

    def __repr__(self):
        return f"<AnalyticsMetric {self.metric_name} - {self.metric_value}>"
