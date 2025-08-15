from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.group_service import GroupService
from app.repositories.group_repository import GroupRepository
from app.schemas.group_schema import GroupCreate, GroupOut
from app.routes.auth_routes import get_current_user

class GroupRoutes:
    router = APIRouter(prefix="/groups", tags=["groups"])
    service = GroupService(GroupRepository())

    @router.post("/", response_model=GroupOut, status_code=status.HTTP_201_CREATED)
    def create_group(payload: GroupCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
        return GroupRoutes.service.create_group(db, payload)
    
    @router.get("/{group_id}", response_model=GroupOut)
    def get_group(group_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
        group = GroupRoutes.service.get_group_by_id(db, group_id)
        if not group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
        return group
    
    @router.get("/", response_model=list[GroupOut])
    def get_all_groups(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
        return GroupRoutes.service.get_all_groups(db)
    
    @router.put("/{group_id}", response_model=GroupOut)
    def update_group(group_id: int, payload: GroupCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
        updated_group = GroupRoutes.service.update_group(db, group_id, payload)
        if not updated_group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
        return updated_group

    @router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_group(group_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
        deleted = GroupRoutes.service.delete_group(db, group_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    @router.post("/{group_id}/members", status_code=status.HTTP_201_CREATED)
    def add_member(group_id: int, user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
        try:
            return GroupRoutes.service.add_member(db, group_id, user_id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @router.get("/{group_id}/members", status_code=status.HTTP_200_OK)
    def get_members(group_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
        try:
            return GroupRoutes.service.get_all_members(db, group_id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        
    @router.delete("/{group_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
    def remove_member(group_id: int, user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
        try:
            removed = GroupRoutes.service.remove_member(db, group_id, user_id)
            if not removed:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found in group")
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
