from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.group_service import GroupService
from app.repositories.group_repository import GroupRepository
from app.schemas.group_schema import GroupCreate, GroupOut
from app.routes.auth_routes import get_current_user

router = APIRouter(prefix="/groups", tags=["groups"])
service = GroupService(GroupRepository())

@router.post("/", response_model=GroupOut, status_code=status.HTTP_201_CREATED)
def create_group(payload: GroupCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # only authenticated users can create groups
    return service.create_group(db, payload)

@router.post("/{group_id}/members", status_code=status.HTTP_201_CREATED)
def add_member(group_id: int, user_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # optionally check if current_user is a group admin
    try:
        return service.add_member(db, group_id, user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
