"""
Pydantic models for HRMS application
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date
from enum import Enum


class EmployeeStatus(str, Enum):
    """Employee status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"


class EmployeeBase(BaseModel):
    """Base employee model"""
    first_name: str = Field(..., min_length=1, max_length=50, description="Employee first name")
    last_name: str = Field(..., min_length=1, max_length=50, description="Employee last name")
    email: EmailStr = Field(..., description="Employee email address")
    phone: str = Field(..., pattern=r'^\+?1?\d{9,15}$', description="Employee phone number")
    department_id: int = Field(..., gt=0, description="Department ID")
    position: str = Field(..., min_length=1, max_length=100, description="Job position")
    hire_date: date = Field(..., description="Date of hiring")
    salary: float = Field(..., gt=0, description="Employee salary")
    status: EmployeeStatus = Field(default=EmployeeStatus.ACTIVE, description="Employee status")


class EmployeeCreate(EmployeeBase):
    """Model for creating a new employee"""
    pass


class EmployeeUpdate(BaseModel):
    """Model for updating an employee"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern=r'^\+?1?\d{9,15}$')
    department_id: Optional[int] = Field(None, gt=0)
    position: Optional[str] = Field(None, min_length=1, max_length=100)
    salary: Optional[float] = Field(None, gt=0)
    status: Optional[EmployeeStatus] = None


class Employee(EmployeeBase):
    """Complete employee model with ID"""
    id: int = Field(..., description="Employee ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@company.com",
                "phone": "+1234567890",
                "department_id": 1,
                "position": "Software Engineer",
                "hire_date": "2024-01-15",
                "salary": 75000.00,
                "status": "active"
            }
        }


class DepartmentBase(BaseModel):
    """Base department model"""
    name: str = Field(..., min_length=1, max_length=100, description="Department name")
    description: str = Field(..., min_length=1, max_length=500, description="Department description")
    manager_id: Optional[int] = Field(None, description="Department manager employee ID")


class DepartmentCreate(DepartmentBase):
    """Model for creating a new department"""
    pass


class DepartmentUpdate(BaseModel):
    """Model for updating a department"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    manager_id: Optional[int] = None


class Department(DepartmentBase):
    """Complete department model with ID"""
    id: int = Field(..., description="Department ID")
    employee_count: int = Field(default=0, description="Number of employees in department")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Engineering",
                "description": "Software development and engineering team",
                "manager_id": 5,
                "employee_count": 15
            }
        }


class LeaveType(str, Enum):
    """Leave type enumeration"""
    SICK = "sick"
    VACATION = "vacation"
    PERSONAL = "personal"
    UNPAID = "unpaid"
    MATERNITY = "maternity"
    PATERNITY = "paternity"


class LeaveStatus(str, Enum):
    """Leave request status enumeration"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class LeaveRequestBase(BaseModel):
    """Base leave request model"""
    employee_id: int = Field(..., gt=0, description="Employee ID")
    leave_type: LeaveType = Field(..., description="Type of leave")
    start_date: date = Field(..., description="Leave start date")
    end_date: date = Field(..., description="Leave end date")
    reason: str = Field(..., min_length=1, max_length=500, description="Reason for leave")


class LeaveRequestCreate(LeaveRequestBase):
    """Model for creating a new leave request"""
    pass


class LeaveRequestUpdate(BaseModel):
    """Model for updating a leave request"""
    leave_type: Optional[LeaveType] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    reason: Optional[str] = Field(None, min_length=1, max_length=500)


class LeaveRequest(LeaveRequestBase):
    """Complete leave request model with ID and status"""
    id: int = Field(..., description="Leave request ID")
    status: LeaveStatus = Field(default=LeaveStatus.PENDING, description="Leave request status")
    approved_by: Optional[int] = Field(None, description="Approver employee ID")
    created_at: date = Field(..., description="Request creation date")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "employee_id": 3,
                "leave_type": "vacation",
                "start_date": "2024-12-20",
                "end_date": "2024-12-31",
                "reason": "Year-end vacation",
                "status": "pending",
                "approved_by": None,
                "created_at": "2024-12-01"
            }
        }


class LeaveApproval(BaseModel):
    """Model for approving/rejecting leave requests"""
    approved: bool = Field(..., description="True to approve, False to reject")
    approved_by: int = Field(..., gt=0, description="Approver employee ID")
    comments: Optional[str] = Field(None, max_length=500, description="Approval/rejection comments")
