import React from 'react';
import { Navigate } from 'react-router-dom'; // Assumes you use react-router-dom

const ProtectedRoute = ({ children }) => {
  
  const isAuthenticated = localStorage.getItem('auth_token');

  if (!isAuthenticated) {
    
    return <Navigate to="/login" replace />;
  }


  return children;
};

export default ProtectedRoute;
