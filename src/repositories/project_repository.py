# Annotations
from sqlalchemy.ext.asyncio import AsyncSession
# SQL
from sqlalchemy import select
from sqlalchemy.orm import selectinload
# Models
from src.models.project import Project
# Schemas
from src.schemas.project_schema import ProjectCreate, ProjectUpdate


class ProjectRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # Get concrete project by it's id
    async def get_by_id(self, id: int) -> Project:
        # SQL statement
        stmt = (
            select(Project)
            .options(selectinload(Project.handles))
            .where(Project.id == id)
        )
        result = await self.session.execute(stmt)
        
        # project object
        project = result.scalars().one_or_none()
        
        return project
    
    # Get concrete project by it's name
    async def get_by_name(self, name: int | None) -> Project:
        stmt = (
            select(Project)
            .options(selectinload(Project.handles))
            .where(Project.name==name)
        )
        result = await self.session.execute(stmt)
        
        # Project object
        project = result.scalars().first()
        
        return project

    # Get all projects (for future (maybe))
    async def get_all(self) -> list[Project]:
        stmt = (
            select(Project)
            .options(selectinload(Project.handles))
        )
        result = await self.session.execute(stmt)

        # List of Project objects
        project = result.scalars().all()

        return project

    # Add project to database
    async def create(self, project_data: ProjectCreate) -> Project:
        # New project object
        new_project = Project(name=project_data.name)
        # Addition to local session list
        self.session.add(new_project)
        return new_project

    # Update concrete project by it's id
    async def update(self, id: int, project_data: ProjectUpdate) -> Project | None:
        project = await self.get_by_id(id)
        
        if project is None:
            return None
        
        update_data = project_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(project, field, value,)
            
        return project

    # Delete concrete project
    async def delete(self, project: Project) -> None:        
        await self.session.delete(project)
