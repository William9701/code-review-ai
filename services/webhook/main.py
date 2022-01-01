"""
Webhook Service - Handles GitHub webhook events
"""
import os
import hmac
import hashlib
from typing import Optional, Dict, Any
from fastapi import FastAPI, Request, HTTPException, Header, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import sys

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from shared.database import get_db, Repository, PullRequest
from shared.messaging import get_message_queue, MessageQueue
from shared.logging import setup_logging, get_logger

# Setup logging
setup_logging(service_name="webhook-service")
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="CodeReview AI - Webhook Service",
    description="Handles GitHub webhook events",
    version="1.0.0"
)

# Get webhook secret
GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")


def verify_signature(payload: bytes, signature: str) -> bool:
    """
    Verify GitHub webhook signature

    Args:
        payload: Request payload
        signature: X-Hub-Signature-256 header value

    Returns:
        True if signature is valid
    """
    if not GITHUB_WEBHOOK_SECRET:
        logger.warning("GITHUB_WEBHOOK_SECRET not set, skipping signature verification")
        return True

    if not signature:
        return False

    # Remove 'sha256=' prefix
    if signature.startswith("sha256="):
        signature = signature[7:]

    # Calculate expected signature
    expected_signature = hmac.new(
        GITHUB_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected_signature, signature)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "webhook-service"}


@app.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """Readiness check endpoint"""
    try:
        # Check database connection
        db.execute("SELECT 1")

        # Check message queue connection
        queue = get_message_queue()

        return {"status": "ready", "service": "webhook-service"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")


@app.post("/webhooks/github")
async def handle_github_webhook(
    request: Request,
    x_github_event: Optional[str] = Header(None),
    x_hub_signature_256: Optional[str] = Header(None),
    x_github_delivery: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Handle GitHub webhook events

    Args:
        request: FastAPI request
        x_github_event: Event type header
        x_hub_signature_256: Signature header
        x_github_delivery: Delivery ID header
        db: Database session
    """
    # Get payload
    payload = await request.body()

    # Verify signature
    if not verify_signature(payload, x_hub_signature_256 or ""):
        logger.warning(f"Invalid webhook signature for delivery {x_github_delivery}")
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Parse JSON payload
    try:
        event_data = await request.json()
    except Exception as e:
        logger.error(f"Failed to parse webhook payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    logger.info(
        f"Received GitHub webhook",
        extra={
            "event_type": x_github_event,
            "delivery_id": x_github_delivery,
            "action": event_data.get("action")
        }
    )

    # Route event to appropriate handler
    try:
        if x_github_event == "pull_request":
            await handle_pull_request_event(event_data, db)
        elif x_github_event == "pull_request_review":
            await handle_pull_request_review_event(event_data, db)
        elif x_github_event == "push":
            await handle_push_event(event_data, db)
        elif x_github_event == "installation":
            await handle_installation_event(event_data, db)
        elif x_github_event == "installation_repositories":
            await handle_installation_repositories_event(event_data, db)
        else:
            logger.debug(f"Ignoring event type: {x_github_event}")

        return {"status": "accepted", "delivery_id": x_github_delivery}
    except Exception as e:
        logger.error(f"Error handling webhook: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


async def handle_pull_request_event(event_data: Dict[str, Any], db: Session):
    """
    Handle pull_request webhook event

    Args:
        event_data: Event payload
        db: Database session
    """
    action = event_data.get("action")
    pr_data = event_data.get("pull_request", {})
    repo_data = event_data.get("repository", {})
    installation_id = event_data.get("installation", {}).get("id")

    # Get or create repository
    repository = db.query(Repository).filter(
        Repository.github_id == repo_data.get("id")
    ).first()

    if not repository:
        repository = Repository(
            github_id=repo_data.get("id"),
            name=repo_data.get("name"),
            full_name=repo_data.get("full_name"),
            owner=repo_data.get("owner", {}).get("login"),
            installation_id=installation_id,
            default_branch=repo_data.get("default_branch", "main")
        )
        db.add(repository)
        db.commit()
        logger.info(f"Created repository: {repository.full_name}")

    # Get or create pull request
    pull_request = db.query(PullRequest).filter(
        PullRequest.github_id == pr_data.get("id")
    ).first()

    if not pull_request:
        pull_request = PullRequest(
            github_id=pr_data.get("id"),
            repository_id=repository.id,
            pr_number=pr_data.get("number"),
            title=pr_data.get("title"),
            description=pr_data.get("body"),
            author=pr_data.get("user", {}).get("login"),
            base_branch=pr_data.get("base", {}).get("ref"),
            head_branch=pr_data.get("head", {}).get("ref"),
            base_sha=pr_data.get("base", {}).get("sha"),
            head_sha=pr_data.get("head", {}).get("sha"),
            state=pr_data.get("state"),
            is_draft=pr_data.get("draft", False),
            files_changed=pr_data.get("changed_files", 0),
            additions=pr_data.get("additions", 0),
            deletions=pr_data.get("deletions", 0)
        )
        db.add(pull_request)
    else:
        # Update existing PR
        pull_request.title = pr_data.get("title")
        pull_request.description = pr_data.get("body")
        pull_request.state = pr_data.get("state")
        pull_request.is_draft = pr_data.get("draft", False)
        pull_request.head_sha = pr_data.get("head", {}).get("sha")
        pull_request.files_changed = pr_data.get("changed_files", 0)
        pull_request.additions = pr_data.get("additions", 0)
        pull_request.deletions = pr_data.get("deletions", 0)

    db.commit()

    # Publish event to message queue based on action
    queue = get_message_queue()

    if action in ["opened", "reopened", "synchronize"]:
        # Trigger analysis
        message = {
            "pull_request_id": pull_request.id,
            "repository_id": repository.id,
            "pr_number": pull_request.pr_number,
            "head_sha": pull_request.head_sha,
            "installation_id": installation_id,
            "action": action
        }

        routing_key = f"pr.{action}"
        queue.publish("pr.events", routing_key, message)

        logger.info(
            f"Published PR event to queue",
            extra={
                "action": action,
                "pr_number": pull_request.pr_number,
                "repository": repository.full_name
            }
        )


async def handle_pull_request_review_event(event_data: Dict[str, Any], db: Session):
    """Handle pull_request_review event"""
    logger.debug("Handling pull_request_review event")
    # TODO: Implement review event handling


async def handle_push_event(event_data: Dict[str, Any], db: Session):
    """Handle push event"""
    logger.debug("Handling push event")
    # TODO: Implement push event handling


async def handle_installation_event(event_data: Dict[str, Any], db: Session):
    """Handle installation event"""
    action = event_data.get("action")
    installation_id = event_data.get("installation", {}).get("id")

    logger.info(
        f"GitHub App installation {action}",
        extra={"installation_id": installation_id, "action": action}
    )

    if action == "created":
        # Add repositories
        repositories = event_data.get("repositories", [])
        for repo_data in repositories:
            repository = Repository(
                github_id=repo_data.get("id"),
                name=repo_data.get("name"),
                full_name=repo_data.get("full_name"),
                owner=event_data.get("installation", {}).get("account", {}).get("login"),
                installation_id=installation_id
            )
            db.add(repository)

        db.commit()
        logger.info(f"Added {len(repositories)} repositories")


async def handle_installation_repositories_event(event_data: Dict[str, Any], db: Session):
    """Handle installation_repositories event"""
    action = event_data.get("action")
    installation_id = event_data.get("installation", {}).get("id")

    if action == "added":
        repositories_added = event_data.get("repositories_added", [])
        for repo_data in repositories_added:
            repository = Repository(
                github_id=repo_data.get("id"),
                name=repo_data.get("name"),
                full_name=repo_data.get("full_name"),
                owner=event_data.get("installation", {}).get("account", {}).get("login"),
                installation_id=installation_id
            )
            db.add(repository)

        db.commit()
        logger.info(f"Added {len(repositories_added)} repositories")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
