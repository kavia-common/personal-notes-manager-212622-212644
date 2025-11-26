from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

from src.core.config import get_settings, Settings
from src.core.database import Base, engine, get_db
from src.core.security import create_access_token
from src.models.user import User
from src.schemas.auth import Token
from src.schemas.user import UserCreate, UserOut
from src.schemas.note import NoteCreate, NoteUpdate, NoteOut
from src.services.user_service import (
    authenticate_user,
    get_current_user,
    get_user_by_username,
    create_user as service_create_user,
)
from src.services.note_service import (
    create_note,
    list_notes,
    get_note,
    update_note,
    delete_note,
)

# Initialize FastAPI with metadata and tags for OpenAPI
app = FastAPI(
    title="Notes API",
    description="FastAPI backend for personal notes with JWT auth and MySQL storage.",
    version="1.0.0",
    openapi_tags=[
        {"name": "health", "description": "Service health and metadata"},
        {"name": "auth", "description": "Authentication endpoints"},
        {"name": "users", "description": "User management"},
        {"name": "notes", "description": "CRUD for notes"},
    ],
)

# Create tables (for demo/dev convenience). In production, use migrations (Alembic).
Base.metadata.create_all(bind=engine)

# CORS
settings: Settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN] if settings.FRONTEND_ORIGIN else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# PUBLIC_INTERFACE
@app.get("/", tags=["health"], summary="Health Check")
def health_check():
    """
    Health Check endpoint.

    Returns:
        JSON indicating service is healthy.
    """
    return {"message": "Healthy"}


# PUBLIC_INTERFACE
@app.post("/auth/register", response_model=UserOut, tags=["auth"], summary="Register a new user")
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account.

    Args:
        payload: UserCreate containing username and password.
        db: SQLAlchemy session.

    Returns:
        UserOut: Newly created user (without password).
    """
    existing = get_user_by_username(db, payload.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    user = service_create_user(db, payload.username, payload.password)
    return UserOut.from_orm(user)


# PUBLIC_INTERFACE
@app.post("/auth/login", response_model=Token, tags=["auth"], summary="Login to obtain JWT")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login to get an access token.

    Args:
        form_data: OAuth2PasswordRequestForm (username, password).
        db: SQLAlchemy session.

    Returns:
        Token: Bearer token and token type.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")


# PUBLIC_INTERFACE
@app.get("/users/me", response_model=UserOut, tags=["users"], summary="Get current user")
def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get the current authenticated user.

    Args:
        current_user: Injected from JWT.

    Returns:
        UserOut: Current user details.
    """
    return UserOut.from_orm(current_user)


# NOTES ROUTES

# PUBLIC_INTERFACE
@app.post("/notes", response_model=NoteOut, tags=["notes"], summary="Create a note")
def api_create_note(
    payload: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new note for the current user.

    Args:
        payload: NoteCreate with title and content.
        db: SQLAlchemy session.
        current_user: Authenticated user.

    Returns:
        NoteOut: Created note info.
    """
    note = create_note(db, owner_id=current_user.id, data=payload)
    return NoteOut.from_orm(note)


# PUBLIC_INTERFACE
@app.get("/notes", response_model=List[NoteOut], tags=["notes"], summary="List notes")
def api_list_notes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all notes of the current user.

    Args:
        db: SQLAlchemy session.
        current_user: Authenticated user.

    Returns:
        List[NoteOut]: Notes owned by the user.
    """
    notes = list_notes(db, owner_id=current_user.id)
    return [NoteOut.from_orm(n) for n in notes]


# PUBLIC_INTERFACE
@app.get("/notes/{note_id}", response_model=NoteOut, tags=["notes"], summary="Get a note")
def api_get_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a single note by ID, if owned by current user.

    Args:
        note_id: ID of the note.
        db: SQLAlchemy session.
        current_user: Authenticated user.

    Returns:
        NoteOut
    """
    note = get_note(db, note_id=note_id, owner_id=current_user.id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return NoteOut.from_orm(note)


# PUBLIC_INTERFACE
@app.put("/notes/{note_id}", response_model=NoteOut, tags=["notes"], summary="Update a note")
def api_update_note(
    note_id: int,
    payload: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a note's title or content.

    Args:
        note_id: ID of the note.
        payload: NoteUpdate with optional title/content.
        db: SQLAlchemy session.
        current_user: Authenticated user.

    Returns:
        NoteOut
    """
    note = update_note(db, note_id=note_id, owner_id=current_user.id, data=payload)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return NoteOut.from_orm(note)


# PUBLIC_INTERFACE
@app.delete("/notes/{note_id}", status_code=204, tags=["notes"], summary="Delete a note")
def api_delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a note owned by the current user.

    Args:
        note_id: ID of the note.
        db: SQLAlchemy session.
        current_user: Authenticated user.

    Returns:
        204 No Content on success.
    """
    deleted = delete_note(db, note_id=note_id, owner_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Note not found")
    return None
