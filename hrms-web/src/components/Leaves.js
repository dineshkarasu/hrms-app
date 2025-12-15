import React, { useState, useEffect } from 'react';
import { leavesAPI, employeesAPI } from '../services/api';

function Leaves() {
  const [leaves, setLeaves] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [showApprovalModal, setShowApprovalModal] = useState(false);
  const [editingLeave, setEditingLeave] = useState(null);
  const [approvingLeave, setApprovingLeave] = useState(null);
  const [formData, setFormData] = useState({
    employee_id: '',
    leave_type: 'vacation',
    start_date: '',
    end_date: '',
    reason: ''
  });
  const [approvalData, setApprovalData] = useState({
    approved: true,
    approved_by: '',
    comments: ''
  });

  useEffect(() => {
    fetchLeaves();
    fetchEmployees();
  }, []);

  const fetchLeaves = async () => {
    try {
      setLoading(true);
      const response = await leavesAPI.getAll();
      setLeaves(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch leave requests: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchEmployees = async () => {
    try {
      const response = await employeesAPI.getAll();
      setEmployees(response.data);
    } catch (err) {
      console.error('Failed to fetch employees:', err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        ...formData,
        employee_id: parseInt(formData.employee_id)
      };

      if (editingLeave) {
        await leavesAPI.update(editingLeave.id, payload);
      } else {
        await leavesAPI.create(payload);
      }
      setShowModal(false);
      setEditingLeave(null);
      resetForm();
      fetchLeaves();
    } catch (err) {
      setError('Failed to save leave request: ' + err.message);
    }
  };

  const handleApprovalSubmit = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        ...approvalData,
        approved_by: parseInt(approvalData.approved_by)
      };
      await leavesAPI.approve(approvingLeave.id, payload);
      setShowApprovalModal(false);
      setApprovingLeave(null);
      setApprovalData({ approved: true, approved_by: '', comments: '' });
      fetchLeaves();
    } catch (err) {
      setError('Failed to process approval: ' + err.message);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to cancel this leave request?')) {
      try {
        await leavesAPI.delete(id);
        fetchLeaves();
      } catch (err) {
        setError('Failed to cancel leave request: ' + err.message);
      }
    }
  };

  const handleEdit = (leave) => {
    setEditingLeave(leave);
    setFormData({
      employee_id: leave.employee_id,
      leave_type: leave.leave_type,
      start_date: leave.start_date,
      end_date: leave.end_date,
      reason: leave.reason
    });
    setShowModal(true);
  };

  const handleApproval = (leave) => {
    setApprovingLeave(leave);
    setApprovalData({ approved: true, approved_by: '', comments: '' });
    setShowApprovalModal(true);
  };

  const resetForm = () => {
    setFormData({
      employee_id: '',
      leave_type: 'vacation',
      start_date: '',
      end_date: '',
      reason: ''
    });
  };

  const getEmployeeName = (empId) => {
    const emp = employees.find(e => e.id === empId);
    return emp ? `${emp.first_name} ${emp.last_name}` : 'Unknown';
  };

  const getStatusBadge = (status) => {
    const badges = {
      pending: 'badge-warning',
      approved: 'badge-success',
      rejected: 'badge-danger',
      cancelled: 'badge-secondary'
    };
    return badges[status] || 'badge-secondary';
  };

  if (loading) return <div className="loading">Loading leave requests...</div>;

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>Leave Requests</h1>
        <button className="btn btn-primary" onClick={() => { resetForm(); setEditingLeave(null); setShowModal(true); }}>
          + Request Leave
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Employee</th>
              <th>Leave Type</th>
              <th>Start Date</th>
              <th>End Date</th>
              <th>Reason</th>
              <th>Status</th>
              <th>Approved By</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {leaves.map(leave => (
              <tr key={leave.id}>
                <td>{leave.id}</td>
                <td>{getEmployeeName(leave.employee_id)}</td>
                <td>
                  <span className="badge badge-info">{leave.leave_type}</span>
                </td>
                <td>{leave.start_date}</td>
                <td>{leave.end_date}</td>
                <td>{leave.reason}</td>
                <td>
                  <span className={`badge ${getStatusBadge(leave.status)}`}>
                    {leave.status}
                  </span>
                </td>
                <td>{leave.approved_by ? getEmployeeName(leave.approved_by) : 'N/A'}</td>
                <td>
                  {leave.status === 'pending' && (
                    <>
                      <button 
                        className="btn btn-success" 
                        onClick={() => handleApproval(leave)} 
                        style={{ marginRight: '8px' }}
                      >
                        Approve/Reject
                      </button>
                      <button className="btn btn-secondary" onClick={() => handleEdit(leave)} style={{ marginRight: '8px' }}>
                        Edit
                      </button>
                    </>
                  )}
                  <button className="btn btn-danger" onClick={() => handleDelete(leave.id)}>
                    Cancel
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Create/Edit Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editingLeave ? 'Edit Leave Request' : 'Request Leave'}</h2>
              <button className="modal-close" onClick={() => setShowModal(false)}>&times;</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Employee *</label>
                <select
                  required
                  value={formData.employee_id}
                  onChange={(e) => setFormData({ ...formData, employee_id: e.target.value })}
                >
                  <option value="">Select Employee</option>
                  {employees.map(emp => (
                    <option key={emp.id} value={emp.id}>
                      {emp.first_name} {emp.last_name} - {emp.position}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Leave Type *</label>
                <select
                  required
                  value={formData.leave_type}
                  onChange={(e) => setFormData({ ...formData, leave_type: e.target.value })}
                >
                  <option value="vacation">Vacation</option>
                  <option value="sick">Sick Leave</option>
                  <option value="personal">Personal</option>
                  <option value="unpaid">Unpaid</option>
                  <option value="maternity">Maternity</option>
                  <option value="paternity">Paternity</option>
                </select>
              </div>
              <div className="form-group">
                <label>Start Date *</label>
                <input
                  type="date"
                  required
                  value={formData.start_date}
                  onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>End Date *</label>
                <input
                  type="date"
                  required
                  value={formData.end_date}
                  onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>Reason *</label>
                <textarea
                  required
                  rows="3"
                  value={formData.reason}
                  onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
                />
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  {editingLeave ? 'Update' : 'Submit Request'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Approval Modal */}
      {showApprovalModal && (
        <div className="modal-overlay" onClick={() => setShowApprovalModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Approve/Reject Leave Request</h2>
              <button className="modal-close" onClick={() => setShowApprovalModal(false)}>&times;</button>
            </div>
            <form onSubmit={handleApprovalSubmit}>
              <div className="card" style={{ marginBottom: '20px', backgroundColor: '#f8fafc' }}>
                <p><strong>Employee:</strong> {getEmployeeName(approvingLeave.employee_id)}</p>
                <p><strong>Leave Type:</strong> {approvingLeave.leave_type}</p>
                <p><strong>Duration:</strong> {approvingLeave.start_date} to {approvingLeave.end_date}</p>
                <p><strong>Reason:</strong> {approvingLeave.reason}</p>
              </div>
              <div className="form-group">
                <label>Decision *</label>
                <select
                  required
                  value={approvalData.approved}
                  onChange={(e) => setApprovalData({ ...approvalData, approved: e.target.value === 'true' })}
                >
                  <option value="true">Approve</option>
                  <option value="false">Reject</option>
                </select>
              </div>
              <div className="form-group">
                <label>Approved By (Employee ID) *</label>
                <select
                  required
                  value={approvalData.approved_by}
                  onChange={(e) => setApprovalData({ ...approvalData, approved_by: e.target.value })}
                >
                  <option value="">Select Approver</option>
                  {employees.map(emp => (
                    <option key={emp.id} value={emp.id}>
                      {emp.first_name} {emp.last_name} - {emp.position}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Comments (optional)</label>
                <textarea
                  rows="3"
                  value={approvalData.comments}
                  onChange={(e) => setApprovalData({ ...approvalData, comments: e.target.value })}
                  placeholder="Add any comments..."
                />
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowApprovalModal(false)}>
                  Cancel
                </button>
                <button type="submit" className={`btn ${approvalData.approved ? 'btn-success' : 'btn-danger'}`}>
                  {approvalData.approved ? 'Approve' : 'Reject'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default Leaves;
