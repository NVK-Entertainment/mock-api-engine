# Repositories
from src.repositories.project_repository import ProjectRepository
# Schemas
from src.schemas.project_schema import (
    ProjectCreate, 
    ProjectUpdate
    )
# Typing
from sqlalchemy.orm import Session
from fastapi import (
    HTTPException, 
    status
    )
# Models
from src.models.project import Project
# Exceptions
from sqlalchemy.exc import IntegrityError


class ProjectService:
    def __init__(self, session: Session, project_repo: ProjectRepository):
        self.session = session
        self.project_repo = project_repo

    # Get concrete project by it's ID
    def get_project_by_id(self, id: int) -> Project:
        """Returns concrete Project object by it's ID.

        Get concrete Project object by given ID

        Parameters:
        id (int): Project's id
    
        Returns:
        Project: Found by ID Project object
        """
        # Project object
        project = self.project_repo.get_by_id(id)
        # Existance check
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project with that ID not found",
            )
        
        return project

    # Get all project (for future(maybe))
    def get_all_projects(self) -> list[Project]:
        """Returns list of all Projects objects in database.

        Get all Project objects in database
    
        Returns:
        list[Project]: Project objects
        """
        # List of Project objects
        projects = self.project_repo.get_all()

        # Existance check
        if not projects:
            return []

        return projects

    # Create new project
    def create_project(
        self,
        project_data: ProjectCreate,
    ) -> Project:
        """Creates Project object with given data.

        Parameters:
        project_data (ProjectCreate): New project data
    
        Returns:
        Project: Created Project object
        """
        try:
            # New project object
            new_project = self.project_repo.create(project_data)

            # Session commit and refresh new project's data
            self.session.commit()
            self.session.refresh(new_project)

            return new_project
        except IntegrityError:
            # Rolling back failed transaction
            self.session.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Project with this name already exists"
            )

    # Update concrete project
    def update_project(
        self,
        id: int,
        new_data: ProjectUpdate,
    ) -> Project:
        """Update concrete Project object by it's ID.

        Update concrete Project object by it's ID with given data
        And returns it updated object

        Parameters:
        id (int): Project's id
        new_data (ProjectUpdate): Updated project's new data
    
        Returns:
        Project: Updated Project object
        """
        try:
            # Project object to change
            project = self.get_project_by_id(id)
            changed_project = self.project_repo.update(
                id=project.id, 
                project_data=new_data
            )

            # Session commit and refresh changed project's data
            self.session.commit()
            self.session.refresh(changed_project)

            return changed_project
        except IntegrityError:
            # Rolling back failed session transaction
            self.session.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Project with this name already exists"
            )

    # Delete concrete project by it's id
    def delete_project(self, id: int) -> None:
        """Delete concrete Project object by it's ID.

        Parameters:
        id (int): Project's (object to delete) id
    
        Returns:
        None
        """

        # Project object to delete
        project = self.get_project_by_id(id)
        self.project_repo.delete(project)

        self.session.commit()