from typing import List, Optional
from sqlalchemy.orm import Session

from src.models.note import Note
from src.schemas.note import NoteCreate, NoteUpdate


def create_note(db: Session, owner_id: int, data: NoteCreate) -> Note:
    """
    Create a note for the given owner.
    """
    note = Note(title=data.title, content=data.content, owner_id=owner_id)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def list_notes(db: Session, owner_id: int) -> List[Note]:
    """
    List all notes for the owner.
    """
    return db.query(Note).filter(Note.owner_id == owner_id).order_by(Note.id.desc()).all()


def get_note(db: Session, note_id: int, owner_id: int) -> Optional[Note]:
    """
    Get a note by id for the given owner.
    """
    return db.query(Note).filter(Note.id == note_id, Note.owner_id == owner_id).first()


def update_note(db: Session, note_id: int, owner_id: int, data: NoteUpdate) -> Optional[Note]:
    """
    Update a note fields if owned by user.
    """
    note = get_note(db, note_id, owner_id)
    if not note:
        return None
    if data.title is not None:
        note.title = data.title
    if data.content is not None:
        note.content = data.content
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def delete_note(db: Session, note_id: int, owner_id: int) -> bool:
    """
    Delete a note if owned by user.
    """
    note = get_note(db, note_id, owner_id)
    if not note:
        return False
    db.delete(note)
    db.commit()
    return True
