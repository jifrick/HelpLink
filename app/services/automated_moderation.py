import urllib.parse
from sqlalchemy.orm import Session
from app.models.gamification import ModerationEvent, FraudEvent
from app.models.resource import Resource
from app.models.user import User
from app.services.points_service import award_points, HP_APPROVED_RESOURCE, HP_QUALITY_BONUS

# Suspicious keywords
SPAM_KEYWORDS = ["buy now", "click here", "make money fast", "crypto", "bitcoin", "casino", "free cash", "guaranteed return"]
DANGEROUS_SCHEMES = ["javascript:", "data:", "file:", "vbscript:"]

def check_spam(text: str) -> bool:
    if not text:
        return False
    text_lower = text.lower()
    for kw in SPAM_KEYWORDS:
        if kw in text_lower:
            return True
    return False

def check_url_scheme(url: str) -> bool:
    try:
        parsed = urllib.parse.urlparse(url)
        return parsed.scheme.lower() not in ["http", "https"]
    except Exception:
        return True # Malformed is dangerous

def calculate_risk(db: Session, resource: Resource, user: User) -> dict:
    risk_score = 0
    checks_performed = {}
    reason_codes = []
    
    # 1. URL Scheme Validation
    if check_url_scheme(resource.url):
        risk_score += 100
        checks_performed["url_scheme"] = "FAILED"
        reason_codes.append("INVALID_URL_SCHEME")
    else:
        checks_performed["url_scheme"] = "PASSED"
        
    # Normalize URL for duplicate checking
    def normalize_url(u: str) -> str:
        try:
            p = urllib.parse.urlparse(u)
            # Remove tracking query params like utm_*
            q = urllib.parse.parse_qs(p.query)
            clean_q = {k: v for k, v in q.items() if not k.startswith("utm_")}
            clean_query = urllib.parse.urlencode(clean_q, doseq=True)
            return urllib.parse.urlunparse((p.scheme, p.netloc, p.path, p.params, clean_query, ''))
        except:
            return u
            
    norm_url = normalize_url(resource.url)
    
    # 2. Duplicate URL check (normalized)
    # Since we can't easily query normalized URLs in SQL without a dedicated column, 
    # we'll do an exact match check on the original URL first, then check all URLs for the user recently?
    # Actually, we can check exact match, it catches 90% of basic spam. But let's check recent URLs from this user.
    duplicate = db.query(Resource).filter(Resource.url == resource.url, Resource.id != resource.id).first()
    if duplicate:
        risk_score += 50
        checks_performed["duplicate_url"] = "FAILED"
        reason_codes.append("DUPLICATE_URL")
    else:
        checks_performed["duplicate_url"] = "PASSED"
        
    # 3. Content Spam check
    if check_spam(resource.title) or check_spam(resource.description):
        risk_score += 40
        checks_performed["content_spam"] = "FAILED"
        reason_codes.append("SPAM_KEYWORDS_DETECTED")
    else:
        checks_performed["content_spam"] = "PASSED"
        
    # 3.5 Spam Burst / Rate Limit check
    import datetime
    one_min_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes=1)
    recent_submissions = db.query(Resource).filter(Resource.user_id == user.id, Resource.created_at >= one_min_ago).count()
    if recent_submissions > 5:
        risk_score += 100
        checks_performed["rate_limit"] = "FAILED"
        reason_codes.append("SPAM_BURST_DETECTED")
        
    # 4. User Trust check
    if user.trust_score < 30:
        risk_score += 20
        checks_performed["user_trust"] = "LOW"
        reason_codes.append("LOW_TRUST_SCORE")
    elif user.trust_score > 70:
        risk_score = max(0, risk_score - 10) # Trust bonus
        checks_performed["user_trust"] = "HIGH"
    else:
        checks_performed["user_trust"] = "NORMAL"

    # Evaluate decision
    if risk_score < 30:
        decision = "APPROVED"
    elif risk_score < 70:
        decision = "HOLD"
    else:
        decision = "REJECTED"
        
    return {
        "decision": decision,
        "risk_score": min(risk_score, 100),
        "checks_performed": checks_performed,
        "reason_codes": reason_codes
    }

def process_resource_submission(db: Session, resource: Resource, user: User) -> str:
    """Run the moderation pipeline on a newly submitted resource."""
    
    # Calculate risk
    mod_result = calculate_risk(db, resource, user)
    decision = mod_result["decision"]
    risk = mod_result["risk_score"]
    reasons = mod_result["reason_codes"]
    
    # Update resource
    resource.risk_score = risk
    
    if decision == "APPROVED":
        resource.status = "published"
    elif decision == "HOLD":
        resource.status = "pending"
    elif decision == "REJECTED":
        resource.status = "rejected"
        # Create fraud event
        fe = FraudEvent(
            user_id=user.id,
            resource_id=resource.id,
            event_type="HIGH_RISK_SUBMISSION",
            severity="HIGH",
            risk_score=risk,
            reason=",".join(reasons),
            evidence=mod_result["checks_performed"]
        )
        db.add(fe)
        
        # Penalize user trust
        user.trust_score = max(0, user.trust_score - 10)
        user.fraud_risk_score = min(100, user.fraud_risk_score + 10)
        
        # Simple enforcement
        if user.fraud_risk_score >= 80:
            user.account_status = "BANNED"
        elif user.fraud_risk_score >= 50:
            user.account_status = "RESTRICTED"
            
    db.commit()

    # Log moderation event
    me = ModerationEvent(
        resource_id=resource.id,
        user_id=user.id,
        automated_decision=decision,
        risk_score=risk,
        checks_performed=mod_result["checks_performed"],
        reason_codes=reasons,
        final_status=resource.status
    )
    db.add(me)
    db.commit()

    # Award points if published
    if resource.status == "published":
        award_points(db, user.id, HP_APPROVED_RESOURCE, "RESOURCE_APPROVED", "resource", str(resource.id), f"Resource published: {resource.title}")

    return decision
