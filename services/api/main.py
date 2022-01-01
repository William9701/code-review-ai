"""
API Service - REST API for dashboard and code submission (MongoDB version)
"""
import os
import sys
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from shared.database import mongodb as db
from shared.logging import setup_logging, get_logger

# Add analyzers
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "analysis-engine"))
from analyzers.python_analyzer import PythonAnalyzer
from analyzers.typescript_analyzer import TypeScriptAnalyzer
from analyzers.security_analyzer import SecurityAnalyzer

# Setup logging
setup_logging(service_name="api-service")
logger = get_logger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="CodeReview AI - API",
    description="REST API for CodeReview AI Dashboard",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class CodeSubmission(BaseModel):
    filename: str
    content: str
    language: str  # python, typescript, javascript

class AnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    total_issues: int
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    info_issues: int

class IssueResponse(BaseModel):
    id: str
    file_path: str
    line_start: int
    severity: str
    category: str
    title: str
    description: str
    code_snippet: Optional[str]

class StatsResponse(BaseModel):
    total_analyses: int
    critical_issues: int
    prs_reviewed: int
    avg_analysis_time: float


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "CodeReview AI API", "status": "online"}


@app.get("/health")
async def health_check():
    """Health check"""
    return {"status": "healthy", "service": "api-service"}


@app.get("/api/stats", response_model=StatsResponse)
async def get_stats():
    """Get dashboard statistics"""
    try:
        stats = db.get_stats()
        return StatsResponse(**stats)
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analyses")
async def get_analyses(limit: int = 10):
    """Get recent analyses"""
    try:
        analyses = db.get_recent_analyses(limit=limit)
        return analyses
    except Exception as e:
        logger.error(f"Error fetching analyses: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analyses/{analysis_id}/issues")
async def get_issues(analysis_id: str):
    """Get issues for an analysis"""
    try:
        issues = db.get_issues_by_analysis(analysis_id)
        return issues
    except Exception as e:
        logger.error(f"Error fetching issues: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_code(submission: CodeSubmission):
    """
    Analyze code directly - instant analysis without GitHub
    """
    try:
        logger.info(f"Analyzing {submission.filename} ({submission.language})")
        start_time = datetime.utcnow()

        # Create analysis record
        analysis_id = db.create_analysis()

        # Run analyzers based on language
        all_issues = []

        if submission.language == "python":
            analyzer = PythonAnalyzer()
            all_issues.extend(analyzer.analyze(submission.filename, submission.content))
        elif submission.language in ["typescript", "javascript"]:
            analyzer = TypeScriptAnalyzer()
            all_issues.extend(analyzer.analyze(submission.filename, submission.content))

        # Always run security analyzer
        security_analyzer = SecurityAnalyzer()
        all_issues.extend(security_analyzer.analyze(submission.filename, submission.content))

        # Save issues to database
        for issue_data in all_issues:
            db.create_issue(
                analysis_id=analysis_id,
                file_path=issue_data["file_path"],
                line_start=issue_data["line_start"],
                severity=issue_data["severity"],
                category=issue_data["category"],
                rule_id=issue_data["rule_id"],
                title=issue_data["title"],
                description=issue_data["description"],
                code_snippet=issue_data.get("code_snippet"),
                suggested_fix=issue_data.get("suggested_fix"),
                extra_data=issue_data.get("metadata")
            )

        # Calculate statistics
        critical_issues = sum(1 for i in all_issues if i["severity"] == "critical")
        high_issues = sum(1 for i in all_issues if i["severity"] == "high")
        medium_issues = sum(1 for i in all_issues if i["severity"] == "medium")
        low_issues = sum(1 for i in all_issues if i["severity"] == "low")
        info_issues = sum(1 for i in all_issues if i["severity"] == "info")

        # Calculate duration
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()

        # Update analysis
        db.update_analysis(
            analysis_id=analysis_id,
            status=db.AnalysisStatus.COMPLETED,
            total_issues=len(all_issues),
            critical_issues=critical_issues,
            high_issues=high_issues,
            medium_issues=medium_issues,
            low_issues=low_issues,
            info_issues=info_issues,
            completed_at=end_time,
            analysis_duration_seconds=duration
        )

        logger.info(f"Analysis completed: {len(all_issues)} issues found")

        return AnalysisResponse(
            analysis_id=analysis_id,
            status=db.AnalysisStatus.COMPLETED,
            total_issues=len(all_issues),
            critical_issues=critical_issues,
            high_issues=high_issues,
            medium_issues=medium_issues,
            low_issues=low_issues,
            info_issues=info_issues
        )

    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/issues/by-severity")
async def get_issues_by_severity():
    """Get issue counts by severity"""
    try:
        return db.get_issues_by_severity()
    except Exception as e:
        logger.error(f"Error fetching issue counts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
