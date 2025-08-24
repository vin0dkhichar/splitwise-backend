from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.group_service import GroupService
from app.repositories.group_repository import GroupRepository
from app.schemas.group_schema import GroupCreate, GroupOut
from app.routes.auth_routes import get_current_user

class GroupRoutes:
    def __init__(self):
        self.router = APIRouter(prefix="/groups", tags=["groups"])
        self.service = GroupService(GroupRepository())

        self.router.add_api_route(
            "/",
            self.create_group,
            response_model=GroupOut,
            status_code=status.HTTP_201_CREATED,
            methods=["POST"]
        )

        self.router.add_api_route(
            "/{group_id}",
            self.get_group,
            response_model=GroupOut,
            methods=["GET"]
        )

        self.router.add_api_route(
            "/",
            self.get_all_groups,
            response_model=list[GroupOut],
            methods=["GET"]
        )

        self.router.add_api_route(
            "/{group_id}",
            self.update_group,
            response_model=GroupOut,
            methods=["PUT"]
        )

        # self.router.add_api_route(
        #     "/{group_id}",
        #     self.delete_group,
        #     status_code=status.HTTP_204_NO_CONTENT,
        #     methods=["DELETE"]
        # )

        self.router.add_api_route(
            "/{group_id}/members",
            self.add_member,
            status_code=status.HTTP_201_CREATED,
            methods=["POST"]
        )

        self.router.add_api_route(
            "/{group_id}/members",
            self.get_members,
            status_code=status.HTTP_200_OK,
            methods=["GET"]
        )

        self.router.add_api_route(
            "/{group_id}/members/{user_id}",
            self.remove_member,
            status_code=status.HTTP_204_NO_CONTENT,
            methods=["DELETE"]
        )

    def create_group(self, payload: GroupCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
        return self.service.create_group(db, payload)
    
    def get_group(self, group_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
        group = self.service.get_group_by_id(db, group_id)
        if not group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
        return group
    
    def get_all_groups(self, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
        return self.service.get_all_groups(db)
    
    def update_group(self, group_id: int, payload: GroupCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
        updated_group = self.service.update_group(db, group_id, payload)
        if not updated_group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
        return updated_group

    def delete_group(self, group_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
        deleted = self.service.delete_group(db, group_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    def add_member(self, group_id: int, user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
        try:
            return self.service.add_member(db, group_id, user_id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    def get_members(self, group_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
        try:
            return self.service.get_all_members(db, group_id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        
    def remove_member(self, group_id: int, user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
        try:
            removed = self.service.remove_member(db, group_id, user_id)
            if not removed:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found in group")
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))