"""
SQLAlchemy Database Models for HRMS
"""
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import date
import enum

Base = declarative_base()


class EmployeeStatusEnum(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"


class LeaveTypeEnum(str, enum.Enum):
    SICK = "sick"
    VACATION = "vacation"
    PERSONAL = "personal"
    UNPAID = "unpaid"
    MATERNITY = "maternity"
    PATERNITY = "paternity"


class LeaveStatusEnum(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class DepartmentModel(Base):
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(500), nullable=False)
    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    
    # Relationships
    employees = relationship("EmployeeModel", back_populates="department", foreign_keys="EmployeeModel.department_id")
    manager = relationship("EmployeeModel", foreign_keys=[manager_id], post_update=True)


class EmployeeModel(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    phone = Column(String(20), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    position = Column(String(100), nullable=False)
    hire_date = Column(Date, nullable=False)
    salary = Column(Float, nullable=False)
    status = Column(SQLEnum(EmployeeStatusEnum), default=EmployeeStatusEnum.ACTIVE, nullable=False)
    
    # Relationships
    department = relationship("DepartmentModel", back_populates="employees", foreign_keys=[department_id])
    leave_requests = relationship("LeaveRequestModel", back_populates="employee", foreign_keys="LeaveRequestModel.employee_id")


class LeaveRequestModel(Base):
    __tablename__ = "leave_requests"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    leave_type = Column(SQLEnum(LeaveTypeEnum), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    reason = Column(String(500), nullable=False)
    status = Column(SQLEnum(LeaveStatusEnum), default=LeaveStatusEnum.PENDING, nullable=False)
    approved_by = Column(Integer, ForeignKey("employees.id"), nullable=True)
    created_at = Column(Date, default=date.today, nullable=False)
    
    # Relationships
    employee = relationship("EmployeeModel", back_populates="leave_requests", foreign_keys=[employee_id])
    approver = relationship("EmployeeModel", foreign_keys=[approved_by])
