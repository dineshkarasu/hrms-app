"""
Leave Management Router with SQLAlchemy
CRUD operations for leave requests
"""
from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from models.schemas import (
    LeaveRequest, LeaveRequestCreate, LeaveRequestUpdate,
    LeaveApproval, LeaveStatus, LeaveType
)
from models.database_models import LeaveRequestModel, EmployeeModel, LeaveTypeEnum, LeaveStatusEnum
from database import get_db

router = APIRouter()


def db_leave_to_schema(db_leave: LeaveRequestModel) -> LeaveRequest:
    """Convert database model to Pydantic schema"""
    return LeaveRequest(
        id=db_leave.id,
        employee_id=db_leave.employee_id,
        leave_type=LeaveType(db_leave.leave_type.value),
        start_date=db_leave.start_date,
        end_date=db_leave.end_date,
        reason=db_leave.reason,
        status=LeaveStatus(db_leave.status.value),
        approved_by=db_leave.approved_by,
        created_at=db_leave.created_at
    )


@router.get("/", response_model=List[LeaveRequest], summary="Get all leave requests")
async def get_leave_requests(
    employee_id: Optional[int] = Query(None, description="Filter by employee ID"),
    status_filter: Optional[LeaveStatus] = Query(None, alias="status", description="Filter by leave status"),
    leave_type: Optional[LeaveType] = Query(None, description="Filter by leave type"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    Retrieve all leave requests with optional filtering
    
    - **employee_id**: Filter by specific employee
    - **status**: Filter by leave status (pending, approved, rejected, cancelled)
    - **leave_type**: Filter by leave type (sick, vacation, personal, etc.)
    - **skip**: Pagination offset
    - **limit**: Maximum number of results
    """
    query = db.query(LeaveRequestModel)
    
    # Apply filters
    if employee_id is not None:
        query = query.filter(LeaveRequestModel.employee_id == employee_id)
    
    if status_filter is not None:
        query = query.filter(LeaveRequestModel.status == LeaveStatusEnum(status_filter.value))
    
    if leave_type is not None:
        query = query.filter(LeaveRequestModel.leave_type == LeaveTypeEnum(leave_type.value))
    
    # Apply pagination
    leave_requests = query.offset(skip).limit(limit).all()
    
    return [db_leave_to_schema(lr) for lr in leave_requests]


@router.get("/{leave_id}", response_model=LeaveRequest, summary="Get leave request by ID")
async def get_leave_request(leave_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific leave request by ID
    
    - **leave_id**: The ID of the leave request to retrieve
    """
    leave_request = db.query(LeaveRequestModel).filter(LeaveRequestModel.id == leave_id).first()
    
    if not leave_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Leave request with ID {leave_id} not found"
        )
    
    return db_leave_to_schema(leave_request)


@router.post("/", response_model=LeaveRequest, status_code=status.HTTP_201_CREATED, summary="Create leave request")
async def create_leave_request(leave_request: LeaveRequestCreate, db: Session = Depends(get_db)):
    """
    Create a new leave request
    
    - **employee_id**: Employee requesting leave (must exist)
    - **leave_type**: Type of leave (sick, vacation, personal, etc.)
    - **start_date**: Leave start date
    - **end_date**: Leave end date (must be >= start_date)
    - **reason**: Reason for requesting leave
    """
    # Validate employee exists
    employee = db.query(EmployeeModel).filter(EmployeeModel.id == leave_request.employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Employee with ID {leave_request.employee_id} does not exist"
        )
    
    # Validate dates
    if leave_request.end_date < leave_request.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be greater than or equal to start date"
        )
    
    # Check for overlapping leave requests
    overlapping = db.query(LeaveRequestModel).filter(
        LeaveRequestModel.employee_id == leave_request.employee_id,
        LeaveRequestModel.status.in_([LeaveStatusEnum.PENDING, LeaveStatusEnum.APPROVED]),
        ~(
            (LeaveRequestModel.end_date < leave_request.start_date) |
            (LeaveRequestModel.start_date > leave_request.end_date)
        )
    ).first()
    
    if overlapping:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Leave request overlaps with existing leave request (ID: {overlapping.id})"
        )
    
    # Create new leave request
    db_leave = LeaveRequestModel(
        employee_id=leave_request.employee_id,
        leave_type=LeaveTypeEnum(leave_request.leave_type.value),
        start_date=leave_request.start_date,
        end_date=leave_request.end_date,
        reason=leave_request.reason,
        status=LeaveStatusEnum.PENDING,
        approved_by=None,
        created_at=date.today()
    )
    
    db.add(db_leave)
    db.commit()
    db.refresh(db_leave)
    
    return db_leave_to_schema(db_leave)


@router.put("/{leave_id}", response_model=LeaveRequest, summary="Update leave request")
async def update_leave_request(leave_id: int, leave_update: LeaveRequestUpdate, db: Session = Depends(get_db)):
    """
    Update a pending leave request
    
    - **leave_id**: The ID of the leave request to update
    - Only pending leave requests can be updated
    - All fields are optional; only provided fields will be updated
    """
    db_leave = db.query(LeaveRequestModel).filter(LeaveRequestModel.id == leave_id).first()
    
    if not db_leave:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Leave request with ID {leave_id} not found"
        )
    
    # Only allow updates to pending requests
    if db_leave.status != LeaveStatusEnum.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot update leave request with status '{db_leave.status.value}'. Only pending requests can be updated."
        )
    
    update_data = leave_update.model_dump(exclude_unset=True)
    
    # Validate dates if being updated
    start_date = update_data.get("start_date", db_leave.start_date)
    end_date = update_data.get("end_date", db_leave.end_date)
    
    if end_date < start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be greater than or equal to start date"
        )
    
    # Convert leave_type enum if present
    if "leave_type" in update_data and update_data["leave_type"] is not None:
        update_data["leave_type"] = LeaveTypeEnum(update_data["leave_type"].value)
    
    # Update leave request
    for key, value in update_data.items():
        setattr(db_leave, key, value)
    
    db.commit()
    db.refresh(db_leave)
    
    return db_leave_to_schema(db_leave)


@router.delete("/{leave_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete/Cancel leave request")
async def delete_leave_request(leave_id: int, db: Session = Depends(get_db)):
    """
    Cancel a leave request
    
    - **leave_id**: The ID of the leave request to cancel
    - Only pending requests can be deleted
    """
    db_leave = db.query(LeaveRequestModel).filter(LeaveRequestModel.id == leave_id).first()
    
    if not db_leave:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Leave request with ID {leave_id} not found"
        )
    
    # Only allow deletion of pending requests
    if db_leave.status != LeaveStatusEnum.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete leave request with status '{db_leave.status.value}'. Only pending requests can be deleted."
        )
    
    # Mark as cancelled instead of deleting
    db_leave.status = LeaveStatusEnum.CANCELLED
    db.commit()
    
    return None


@router.post("/{leave_id}/approve", response_model=LeaveRequest, summary="Approve or reject leave request")
async def approve_leave_request(leave_id: int, approval: LeaveApproval, db: Session = Depends(get_db)):
    """
    Approve or reject a leave request
    
    - **leave_id**: The ID of the leave request
    - **approved**: True to approve, False to reject
    - **approved_by**: Employee ID of the approver (must exist)
    - **comments**: Optional comments for the approval/rejection
    """
    db_leave = db.query(LeaveRequestModel).filter(LeaveRequestModel.id == leave_id).first()
    
    if not db_leave:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Leave request with ID {leave_id} not found"
        )
    
    # Only allow approval of pending requests
    if db_leave.status != LeaveStatusEnum.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot approve leave request with status '{db_leave.status.value}'. Only pending requests can be approved."
        )
    
    # Validate approver exists
    approver = db.query(EmployeeModel).filter(EmployeeModel.id == approval.approved_by).first()
    if not approver:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Approver employee with ID {approval.approved_by} does not exist"
        )
    
    # Update leave request status
    db_leave.status = LeaveStatusEnum.APPROVED if approval.approved else LeaveStatusEnum.REJECTED
    db_leave.approved_by = approval.approved_by
    
    db.commit()
    db.refresh(db_leave)
    
    return db_leave_to_schema(db_leave)


@router.get("/employee/{employee_id}/summary", summary="Get employee leave summary")
async def get_employee_leave_summary(employee_id: int, db: Session = Depends(get_db)):
    """
    Get leave summary for a specific employee
    
    - **employee_id**: The employee ID
    """
    employee = db.query(EmployeeModel).filter(EmployeeModel.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found"
        )
    
    employee_leaves = db.query(LeaveRequestModel).filter(LeaveRequestModel.employee_id == employee_id).all()
    
    summary = {
        "employee_id": employee_id,
        "total_requests": len(employee_leaves),
        "pending": sum(1 for lr in employee_leaves if lr.status == LeaveStatusEnum.PENDING),
        "approved": sum(1 for lr in employee_leaves if lr.status == LeaveStatusEnum.APPROVED),
        "rejected": sum(1 for lr in employee_leaves if lr.status == LeaveStatusEnum.REJECTED),
        "cancelled": sum(1 for lr in employee_leaves if lr.status == LeaveStatusEnum.CANCELLED),
        "by_type": {
            "sick": sum(1 for lr in employee_leaves if lr.leave_type == LeaveTypeEnum.SICK),
            "vacation": sum(1 for lr in employee_leaves if lr.leave_type == LeaveTypeEnum.VACATION),
            "personal": sum(1 for lr in employee_leaves if lr.leave_type == LeaveTypeEnum.PERSONAL),
            "unpaid": sum(1 for lr in employee_leaves if lr.leave_type == LeaveTypeEnum.UNPAID),
            "maternity": sum(1 for lr in employee_leaves if lr.leave_type == LeaveTypeEnum.MATERNITY),
            "paternity": sum(1 for lr in employee_leaves if lr.leave_type == LeaveTypeEnum.PATERNITY),
        }
    }
    
    return summary
