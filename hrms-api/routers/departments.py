"""
Department Management Router with SQLAlchemy
CRUD operations for departments
"""
from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.schemas import Department, DepartmentCreate, DepartmentUpdate
from models.database_models import DepartmentModel, EmployeeModel
from database import get_db

router = APIRouter()


def db_department_to_schema(db_dept: DepartmentModel, employee_count: int = None) -> Department:
    """Convert database model to Pydantic schema"""
    if employee_count is None:
        employee_count = len(db_dept.employees) if db_dept.employees else 0
    
    return Department(
        id=db_dept.id,
        name=db_dept.name,
        description=db_dept.description,
        manager_id=db_dept.manager_id,
        employee_count=employee_count
    )


@router.get("/", response_model=List[Department], summary="Get all departments")
async def get_departments(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    Retrieve all departments with pagination
    
    - **skip**: Pagination offset
    - **limit**: Maximum number of results
    """
    departments = db.query(DepartmentModel).offset(skip).limit(limit).all()
    
    result = []
    for dept in departments:
        emp_count = db.query(func.count(EmployeeModel.id)).filter(EmployeeModel.department_id == dept.id).scalar()
        result.append(db_department_to_schema(dept, emp_count))
    
    return result


@router.get("/{department_id}", response_model=Department, summary="Get department by ID")
async def get_department(department_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific department by ID
    
    - **department_id**: The ID of the department to retrieve
    """
    department = db.query(DepartmentModel).filter(DepartmentModel.id == department_id).first()
    
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department with ID {department_id} not found"
        )
    
    emp_count = db.query(func.count(EmployeeModel.id)).filter(EmployeeModel.department_id == department_id).scalar()
    
    return db_department_to_schema(department, emp_count)


@router.post("/", response_model=Department, status_code=status.HTTP_201_CREATED, summary="Create new department")
async def create_department(department: DepartmentCreate, db: Session = Depends(get_db)):
    """
    Create a new department
    
    - **name**: Department name (must be unique)
    - **description**: Department description
    - **manager_id**: Optional employee ID of the department manager
    """
    # Check name uniqueness
    existing = db.query(DepartmentModel).filter(
        func.lower(DepartmentModel.name) == department.name.lower()
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Department with name '{department.name}' already exists"
        )
    
    # Validate manager exists if provided
    if department.manager_id is not None:
        manager = db.query(EmployeeModel).filter(EmployeeModel.id == department.manager_id).first()
        if not manager:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Employee with ID {department.manager_id} does not exist"
            )
    
    # Create new department
    db_department = DepartmentModel(
        name=department.name,
        description=department.description,
        manager_id=department.manager_id
    )
    
    db.add(db_department)
    db.commit()
    db.refresh(db_department)
    
    return db_department_to_schema(db_department, 0)


@router.put("/{department_id}", response_model=Department, summary="Update department")
async def update_department(department_id: int, department_update: DepartmentUpdate, db: Session = Depends(get_db)):
    """
    Update an existing department
    
    - **department_id**: The ID of the department to update
    - All fields are optional; only provided fields will be updated
    """
    db_department = db.query(DepartmentModel).filter(DepartmentModel.id == department_id).first()
    
    if not db_department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department with ID {department_id} not found"
        )
    
    update_data = department_update.model_dump(exclude_unset=True)
    
    # Check name uniqueness if being updated
    if "name" in update_data and update_data["name"] is not None:
        existing = db.query(DepartmentModel).filter(
            func.lower(DepartmentModel.name) == update_data["name"].lower(),
            DepartmentModel.id != department_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Department with name '{update_data['name']}' already exists"
            )
    
    # Validate manager exists if being updated
    if "manager_id" in update_data and update_data["manager_id"] is not None:
        manager = db.query(EmployeeModel).filter(EmployeeModel.id == update_data["manager_id"]).first()
        if not manager:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Employee with ID {update_data['manager_id']} does not exist"
            )
    
    # Update department
    for key, value in update_data.items():
        setattr(db_department, key, value)
    
    db.commit()
    db.refresh(db_department)
    
    emp_count = db.query(func.count(EmployeeModel.id)).filter(EmployeeModel.department_id == department_id).scalar()
    
    return db_department_to_schema(db_department, emp_count)


@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete department")
async def delete_department(department_id: int, db: Session = Depends(get_db)):
    """
    Delete a department
    
    - **department_id**: The ID of the department to delete
    
    Note: Cannot delete a department with active employees
    """
    db_department = db.query(DepartmentModel).filter(DepartmentModel.id == department_id).first()
    
    if not db_department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department with ID {department_id} not found"
        )
    
    # Check if department has employees
    employee_count = db.query(func.count(EmployeeModel.id)).filter(EmployeeModel.department_id == department_id).scalar()
    
    if employee_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete department with active employees. Please reassign or remove employees first."
        )
    
    db.delete(db_department)
    db.commit()
    
    return None


@router.get("/{department_id}/stats", summary="Get department statistics")
async def get_department_stats(department_id: int, db: Session = Depends(get_db)):
    """
    Get statistics for a specific department
    
    - **department_id**: The department ID
    """
    department = db.query(DepartmentModel).filter(DepartmentModel.id == department_id).first()
    
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department with ID {department_id} not found"
        )
    
    employees = db.query(EmployeeModel).filter(EmployeeModel.department_id == department_id).all()
    
    total_salary = sum(emp.salary for emp in employees)
    avg_salary = total_salary / len(employees) if employees else 0
    active_count = sum(1 for emp in employees if emp.status.value == "active")
    
    stats = {
        "department_id": department_id,
        "department_name": department.name,
        "total_employees": len(employees),
        "active_employees": active_count,
        "total_salary_expense": total_salary,
        "average_salary": round(avg_salary, 2),
        "manager_id": department.manager_id
    }
    
    return stats
