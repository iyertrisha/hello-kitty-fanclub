import React, { useState } from 'react';
import './CooperativeCard.css';

const CooperativeCard = ({
  cooperative,
  onEdit,
  onViewDetails,
  onAddMembers,
  onDelete,
}) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="cooperative-card">
      <div className="cooperative-card-header">
        <div className="cooperative-card-info">
          <h3 className="cooperative-card-name">{cooperative.name}</h3>
          <p className="cooperative-card-meta">
            {cooperative.members?.length || 0} members • Revenue Split:{' '}
            {cooperative.revenue_split || 0}%
          </p>
        </div>
        <div className="cooperative-card-actions">
          <button
            className="cooperative-card-button"
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? '▼' : '▶'} {expanded ? 'Hide' : 'Show'} Members
          </button>
          {onViewDetails && (
            <button
              className="cooperative-card-button primary"
              onClick={() => onViewDetails(cooperative.id)}
            >
              View Details
            </button>
          )}
          {onEdit && (
            <button
              className="cooperative-card-button"
              onClick={() => onEdit(cooperative.id)}
            >
              Edit
            </button>
          )}
          {onDelete && (
            <button
              className="cooperative-card-button delete"
              onClick={() => onDelete(cooperative.id)}
            >
              Delete
            </button>
          )}
        </div>
      </div>

      {cooperative.description && (
        <p className="cooperative-card-description">{cooperative.description}</p>
      )}

      {expanded && (
        <div className="cooperative-card-members">
          <h4 className="cooperative-card-members-title">Members</h4>
          {cooperative.members && cooperative.members.length > 0 ? (
            <ul className="cooperative-card-members-list">
              {cooperative.members.map((member) => (
                <li key={member.id} className="cooperative-card-member">
                  <span className="member-name">
                    {member.name || `Shopkeeper ${member.id}`}
                  </span>
                  <span className="member-info">{member.address || 'No address'}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="cooperative-card-no-members">No members yet</p>
          )}
          {onAddMembers && (
            <button
              className="cooperative-card-add-members"
              onClick={() => onAddMembers(cooperative.id)}
            >
              + Add Members
            </button>
          )}
        </div>
      )}

      {cooperative.bulk_orders && cooperative.bulk_orders.length > 0 && (
        <div className="cooperative-card-orders">
          <h4 className="cooperative-card-orders-title">Recent Bulk Orders</h4>
          <div className="cooperative-card-orders-list">
            {cooperative.bulk_orders.slice(0, 3).map((order) => (
              <div key={order.id} className="cooperative-card-order">
                <span>Order #{order.id}</span>
                <span>₹{order.total_amount?.toFixed(2)}</span>
                <span className="order-status">{order.status}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default CooperativeCard;

