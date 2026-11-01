"""Knowledge Base & Business Policies API router."""

from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.api.deps import get_current_user, require_role
from backend.app.core.database import get_db
from backend.app.models.knowledge import KnowledgeArticle
from backend.app.models.user import User

router = APIRouter(prefix="/api/knowledge", tags=["Knowledge Base"])


class ArticleCreateRequest(BaseModel):
    category: str
    title: str
    content: str
    language: str = "uz"


class ArticleUpdateRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_active: Optional[bool] = None


@router.get("")
async def list_articles(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    category: Optional[str] = None,
    language: Optional[str] = None,
):
    """List business knowledge articles and FAQs."""
    stmt = (
        select(KnowledgeArticle)
        .where(KnowledgeArticle.business_id == current_user.business_id)
        .order_by(KnowledgeArticle.category.asc(), KnowledgeArticle.language.asc())
    )
    if category:
        stmt = stmt.where(KnowledgeArticle.category == category)
    if language:
        stmt = stmt.where(KnowledgeArticle.language == language)

    res = await db.execute(stmt)
    articles = res.scalars().all()

    return {
        "count": len(articles),
        "items": [
            {
                "id": a.id,
                "category": a.category,
                "title": a.title,
                "content": a.content,
                "language": a.language,
                "version": a.version,
                "is_active": a.is_active,
                "updated_at": a.updated_at.isoformat(),
            }
            for a in articles
        ],
    }


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_article(
    req: ArticleCreateRequest,
    current_user: Annotated[User, Depends(require_role(["owner", "admin"]))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create new knowledge base article."""
    article = KnowledgeArticle(
        business_id=current_user.business_id,
        category=req.category,
        title=req.title,
        content=req.content,
        language=req.language,
        version=1,
        is_active=True,
    )
    db.add(article)
    await db.commit()
    return {"status": "created", "article_id": article.id}


@router.put("/{article_id}")
async def update_article(
    article_id: int,
    req: ArticleUpdateRequest,
    current_user: Annotated[User, Depends(require_role(["owner", "admin"]))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update knowledge article with automatic version bumping."""
    res = await db.execute(
        select(KnowledgeArticle).where(
            KnowledgeArticle.id == article_id,
            KnowledgeArticle.business_id == current_user.business_id,
        )
    )
    article = res.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found.")

    if req.title is not None:
        article.title = req.title
    if req.content is not None:
        article.content = req.content
        article.version += 1
    if req.is_active is not None:
        article.is_active = req.is_active

    await db.commit()
    return {"status": "updated", "article_id": article.id, "version": article.version}
