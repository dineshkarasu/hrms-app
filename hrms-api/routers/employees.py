"""
Employee Management Router with SQLAlchemy
CRUD operations for employees
"""
from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.schemas import Employee, EmployeeCreate, EmployeeUpdate, EmployeeStatus
from models.database_models import EmployeeModel, DepartmentModel, EmployeeStatusEnum
from database import get_db

router = APIRouter()


def db_employee_to_schema(db_employee: EmployeeModel) -> Employee:
    """Convert database model to Pydantic schema"""
    return Employee(
        id=db_employee.id,
        first_name=db_employee.first_name,
        last_name=db_employee.last_name,
        email=db_employee.email,
        phone=db_employee.phone,
        department_id=db_employee.department_id,
        position=db_employee.position,
        hire_date=db_employee.hire_date,
        salary=db_employee.salary,
        status=EmployeeStatus(db_employee.status.value)
    )


@router.get("/", response_model=List[Employee], summary="Get all employees")
async def get_employees(
    department_id: Optional[int] = Query(None, description="Filter by department ID"),
    status_filter: Optional[EmployeeStatus] = Query(None, alias="status", description="Filter by employee status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    Retrieve all employees with optional filtering
    
    - **department_id**: Filter employees by department
    - **status**: Filter employees by status (active, inactive, on_leave)
    - **skip**: Pagination offset
    - **limit**: Maximum number of results
    """
    query = db.query(EmployeeModel)
    
    # Apply filters
    if department_id is not None:
        query = query.filter(EmployeeModel.department_id == department_id)
    
    if status_filter is not None:
        query = query.filter(EmployeeModel.status == EmployeeStatusEnum(status_filter.value))
    
    # Apply pagination
    employees = query.offset(skip).limit(limit).all()
    
    return [db_employee_to_schema(emp) for emp in employees]


@router.get("/{employee_id}", response_model=Employee, summary="Get employee by ID")
async def get_employee(employee_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific employee by ID
    
    - **employee_id**: The ID of the employee to retrieve
    """
    employee = db.query(EmployeeModel).filter(EmployeeModel.id == employee_id).first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found"
        )
    
    return db_employee_to_schema(employee)


@router.post("/", response_model=Employee, status_code=status.HTTP_201_CREATED, summary="Create new employee")
async def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    """
    Create a new employee
    
    - **first_name**: Employee's first name
    - **last_name**: Employee's last name
    - **email**: Employee's email address (must be unique)
    - **phone**: Employee's phone number
    - **department_id**: Department ID (must exist)
    - **position**: Job position
    - **hire_date**: Date of hiring
    - **salary**: Employee's salary
    - **status**: Employment status (default: active)
    """
    # Validate department exists
    department = db.query(DepartmentModel).filter(DepartmentModel.id == employee.department_id).first()
    if not department:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Department with ID {employee.department_id} does not exist"
        )
    
    # Check email uniqueness
    existing_employee = db.query(EmployeeModel).filter(EmployeeModel.email == employee.email).first()
    if existing_employee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email {employee.email} is already registered"
        )
    
    # Create new employee
    db_employee = EmployeeModel(
        first_name=employee.first_name,
        last_name=employee.last_name,
        email=employee.email,
        phone=employee.phone,
        department_id=employee.department_id,
        position=employee.position,
        hire_date=employee.hire_date,
        salary=employee.salary,
        status=EmployeeStatusEnum(employee.status.value)
    )
    
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    
    return db_employee_to_schema(db_employee)


@router.put("/{employee_id}", response_model=Employee, summary="Update employee")
async def update_employee(employee_id: int, employee_update: EmployeeUpdate, db: Session = Depends(get_db)):
    """
    Update an existing employee
    
    - **employee_id**: The ID of the employee to update
    - All fields are optional; only provided fields will be updated
    """
    db_employee = db.query(EmployeeModel).filter(EmployeeModel.id == employee_id).first()
    
    if not db_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found"
        )
    
    update_data = employee_update.model_dump(exclude_unset=True)
    
    # Validate department if being updated
    if "department_id" in update_data and update_data["department_id"] is not None:
        department = db.query(DepartmentModel).filter(DepartmentModel.id == update_data["department_id"]).first()
        if not department:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Department with ID {update_data['department_id']} does not exist"
            )
    
    # Check email uniqueness if being updated
    if "email" in update_data and update_data["email"] is not None:
        existing = db.query(EmployeeModel).filter(
            EmployeeModel.email == update_data["email"],
            EmployeeModel.id != employee_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email {update_data['email']} is already registered"
            )
    
    # Convert status enum if present
    if "status" in update_data and update_data["status"] is not None:
        update_data["status"] = EmployeeStatusEnum(update_data["status"].value)
    
    # Update employee
    for key, value in update_data.items():
        setattr(db_employee, key, value)
    
    db.commit()
    db.refresh(db_employee)
    
    return db_employee_to_schema(db_employee)


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete employee")
async def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    """
    Delete an employee
    
    - **employee_id**: The ID of the employee to delete
    """
    db_employee = db.query(EmployeeModel).filter(EmployeeModel.id == employee_id).first()
    
    if not db_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found"
        )
    
    db.delete(db_employee)
    db.commit()
    
    return None


@router.get("/department/{department_id}/employees", response_model=List[Employee], summary="Get employees by department")
async def get_employees_by_department(department_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all employees in a specific department
    
    - **department_id**: The department ID
    """
    department = db.query(DepartmentModel).filter(DepartmentModel.id == department_id).first()
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department with ID {department_id} not found"
        )
    
    employees = db.query(EmployeeModel).filter(EmployeeModel.department_id == department_id).all()
    
    return [db_employee_to_schema(emp) for emp in employees]
