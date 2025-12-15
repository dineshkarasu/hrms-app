"""
Seed initial data into the database
"""
from datetime import date
from database import SessionLocal, init_db
from models.database_models import DepartmentModel, EmployeeModel, LeaveRequestModel
from models.database_models import EmployeeStatusEnum, LeaveTypeEnum, LeaveStatusEnum


def seed_database():
    """Seed the database with initial data"""
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_departments = db.query(DepartmentModel).first()
        if existing_departments:
            print("⚠️  Database already contains data. Skipping seed.")
            return
        
        print("🌱 Seeding database with initial data...")
        
        # Create Departments
        departments = [
            DepartmentModel(
                id=1,
                name="Engineering",
                description="Software development and engineering team",
                manager_id=None  # Will update after creating employees
            ),
            DepartmentModel(
                id=2,
                name="Human Resources",
                description="HR and talent management",
                manager_id=None
            ),
            DepartmentModel(
                id=3,
                name="Sales",
                description="Sales and business development",
                manager_id=None
            ),
            DepartmentModel(
                id=4,
                name="Marketing",
                description="Marketing and communications",
                manager_id=None
            ),
        ]
        
        for dept in departments:
            db.add(dept)
        db.commit()
        print("✅ Departments created")
        
        # Create Employees
        employees = [
            EmployeeModel(
                id=1,
                first_name="John",
                last_name="Doe",
                email="john.doe@company.com",
                phone="+12345678901",
                department_id=1,
                position="Senior Software Engineer",
                hire_date=date(2022, 1, 15),
                salary=95000.00,
                status=EmployeeStatusEnum.ACTIVE
            ),
            EmployeeModel(
                id=2,
                first_name="Jane",
                last_name="Smith",
                email="jane.smith@company.com",
                phone="+12345678902",
                department_id=2,
                position="HR Manager",
                hire_date=date(2021, 3, 20),
                salary=85000.00,
                status=EmployeeStatusEnum.ACTIVE
            ),
            EmployeeModel(
                id=3,
                first_name="Mike",
                last_name="Johnson",
                email="mike.johnson@company.com",
                phone="+12345678903",
                department_id=1,
                position="Software Engineer",
                hire_date=date(2023, 6, 10),
                salary=75000.00,
                status=EmployeeStatusEnum.ACTIVE
            ),
            EmployeeModel(
                id=4,
                first_name="Sarah",
                last_name="Williams",
                email="sarah.williams@company.com",
                phone="+12345678904",
                department_id=3,
                position="Sales Representative",
                hire_date=date(2023, 2, 1),
                salary=65000.00,
                status=EmployeeStatusEnum.ACTIVE
            ),
            EmployeeModel(
                id=5,
                first_name="David",
                last_name="Brown",
                email="david.brown@company.com",
                phone="+12345678905",
                department_id=4,
                position="Marketing Specialist",
                hire_date=date(2023, 9, 15),
                salary=70000.00,
                status=EmployeeStatusEnum.ACTIVE
            ),
        ]
        
        for emp in employees:
            db.add(emp)
        db.commit()
        print("✅ Employees created")
        
        # Update department managers
        dept_eng = db.query(DepartmentModel).filter(DepartmentModel.id == 1).first()
        dept_eng.manager_id = 1
        
        dept_hr = db.query(DepartmentModel).filter(DepartmentModel.id == 2).first()
        dept_hr.manager_id = 2
        
        db.commit()
        print("✅ Department managers assigned")
        
        # Create Leave Requests
        leave_requests = [
            LeaveRequestModel(
                id=1,
                employee_id=3,
                leave_type=LeaveTypeEnum.VACATION,
                start_date=date(2024, 12, 20),
                end_date=date(2024, 12, 31),
                reason="Year-end vacation with family",
                status=LeaveStatusEnum.PENDING,
                approved_by=None,
                created_at=date(2024, 12, 1)
            ),
            LeaveRequestModel(
                id=2,
                employee_id=4,
                leave_type=LeaveTypeEnum.SICK,
                start_date=date(2024, 11, 5),
                end_date=date(2024, 11, 7),
                reason="Medical appointment and recovery",
                status=LeaveStatusEnum.APPROVED,
                approved_by=2,
                created_at=date(2024, 11, 1)
            ),
            LeaveRequestModel(
                id=3,
                employee_id=5,
                leave_type=LeaveTypeEnum.PERSONAL,
                start_date=date(2024, 11, 15),
                end_date=date(2024, 11, 16),
                reason="Personal matters",
                status=LeaveStatusEnum.REJECTED,
                approved_by=2,
                created_at=date(2024, 11, 10)
            ),
        ]
        
        for leave in leave_requests:
            db.add(leave)
        db.commit()
        print("✅ Leave requests created")
        
        print("🎉 Database seeding completed successfully!")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # Initialize database tables
    init_db()
    # Seed initial data
    seed_database()
