"""
MongoDB connection and data access layer
"""
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from pymongo import MongoClient
from bson import ObjectId

# MongoDB connection
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://127.0.0.1:27017/")
DB_NAME = os.getenv("DB_NAME", "codereview")

client = MongoClient(MONGODB_URL)
db = client[DB_NAME]

# Collections
analyses_collection = db["analyses"]
issues_collection = db["issues"]
repositories_collection = db["repositories"]
pull_requests_collection = db["pull_requests"]


def get_db():
    """Get database instance"""
    return db


class AnalysisStatus:
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class IssueSeverity:
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class IssueCategory:
    SECURITY = "security"
    PERFORMANCE = "performance"
    CODE_QUALITY = "code_quality"
    BEST_PRACTICES = "best_practices"
    MAINTAINABILITY = "maintainability"


def create_analysis(pull_request_id: Optional[str] = None) -> str:
    """Create a new analysis record"""
    analysis = {
        "pull_request_id": pull_request_id,
        "status": AnalysisStatus.IN_PROGRESS,
        "total_issues": 0,
        "critical_issues": 0,
        "high_issues": 0,
        "medium_issues": 0,
        "low_issues": 0,
        "info_issues": 0,
        "created_at": datetime.utcnow(),
        "started_at": datetime.utcnow(),
        "completed_at": None,
        "analysis_duration_seconds": None,
    }
    result = analyses_collection.insert_one(analysis)
    return str(result.inserted_id)


def update_analysis(
    analysis_id: str,
    status: str,
    total_issues: int = 0,
    critical_issues: int = 0,
    high_issues: int = 0,
    medium_issues: int = 0,
    low_issues: int = 0,
    info_issues: int = 0,
    completed_at: Optional[datetime] = None,
    analysis_duration_seconds: Optional[float] = None,
):
    """Update analysis record"""
    update_data = {
        "status": status,
        "total_issues": total_issues,
        "critical_issues": critical_issues,
        "high_issues": high_issues,
        "medium_issues": medium_issues,
        "low_issues": low_issues,
        "info_issues": info_issues,
    }

    if completed_at:
        update_data["completed_at"] = completed_at
    if analysis_duration_seconds is not None:
        update_data["analysis_duration_seconds"] = analysis_duration_seconds

    analyses_collection.update_one(
        {"_id": ObjectId(analysis_id)},
        {"$set": update_data}
    )


def create_issue(
    analysis_id: str,
    file_path: str,
    line_start: int,
    severity: str,
    category: str,
    rule_id: str,
    title: str,
    description: str,
    code_snippet: Optional[str] = None,
    suggested_fix: Optional[str] = None,
    extra_data: Optional[Dict[str, Any]] = None,
) -> str:
    """Create a new issue record"""
    issue = {
        "analysis_id": analysis_id,
        "file_path": file_path,
        "line_start": line_start,
        "line_end": line_start,
        "severity": severity,
        "category": category,
        "rule_id": rule_id,
        "title": title,
        "description": description,
        "code_snippet": code_snippet,
        "suggested_fix": suggested_fix,
        "extra_data": extra_data or {},
        "created_at": datetime.utcnow(),
    }
    result = issues_collection.insert_one(issue)
    return str(result.inserted_id)


def get_stats() -> Dict[str, Any]:
    """Get overall statistics"""
    total_analyses = analyses_collection.count_documents({})

    # Count critical issues
    critical_pipeline = [
        {"$match": {"severity": IssueSeverity.CRITICAL}},
        {"$count": "total"}
    ]
    critical_result = list(issues_collection.aggregate(critical_pipeline))
    critical_issues = critical_result[0]["total"] if critical_result else 0

    # Count completed PRs (analyses)
    prs_reviewed = analyses_collection.count_documents({"status": AnalysisStatus.COMPLETED})

    # Calculate average analysis time
    avg_pipeline = [
        {"$match": {"analysis_duration_seconds": {"$ne": None}}},
        {"$group": {"_id": None, "avg_time": {"$avg": "$analysis_duration_seconds"}}}
    ]
    avg_result = list(analyses_collection.aggregate(avg_pipeline))
    avg_analysis_time = round(avg_result[0]["avg_time"], 2) if avg_result else 0

    return {
        "total_analyses": total_analyses,
        "critical_issues": critical_issues,
        "prs_reviewed": prs_reviewed,
        "avg_analysis_time": avg_analysis_time,
    }


def get_recent_analyses(limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent analyses"""
    analyses = analyses_collection.find().sort("created_at", -1).limit(limit)
    result = []
    for analysis in analyses:
        result.append({
            "id": str(analysis["_id"]),
            "status": analysis["status"],
            "total_issues": analysis["total_issues"],
            "critical_issues": analysis["critical_issues"],
            "high_issues": analysis["high_issues"],
            "medium_issues": analysis["medium_issues"],
            "low_issues": analysis["low_issues"],
            "info_issues": analysis["info_issues"],
            "created_at": analysis["created_at"].isoformat() if analysis.get("created_at") else None,
            "completed_at": analysis["completed_at"].isoformat() if analysis.get("completed_at") else None,
        })
    return result


def get_issues_by_analysis(analysis_id: str) -> List[Dict[str, Any]]:
    """Get all issues for an analysis"""
    issues = issues_collection.find({"analysis_id": analysis_id})
    result = []
    for issue in issues:
        result.append({
            "id": str(issue["_id"]),
            "file_path": issue["file_path"],
            "line_start": issue["line_start"],
            "severity": issue["severity"],
            "category": issue["category"],
            "rule_id": issue["rule_id"],
            "title": issue["title"],
            "description": issue["description"],
            "code_snippet": issue.get("code_snippet"),
            "suggested_fix": issue.get("suggested_fix"),
        })
    return result


def get_issues_by_severity() -> Dict[str, int]:
    """Get issue counts by severity"""
    pipeline = [
        {"$group": {"_id": "$severity", "count": {"$sum": 1}}}
    ]
    results = issues_collection.aggregate(pipeline)

    severity_counts = {
        IssueSeverity.CRITICAL: 0,
        IssueSeverity.HIGH: 0,
        IssueSeverity.MEDIUM: 0,
        IssueSeverity.LOW: 0,
        IssueSeverity.INFO: 0,
    }

    for result in results:
        severity = result["_id"]
        if severity in severity_counts:
            severity_counts[severity] = result["count"]

    return severity_counts
