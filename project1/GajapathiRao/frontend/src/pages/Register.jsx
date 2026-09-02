import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, Mail, Lock } from 'lucide-react';
import '../styles/login.scss';
import {Link} from 'react-router-dom';

const Register = () => {
  const [formData, setFormData] = useState({ name: '', email: '', password: '' });
  const [errors, setErrors] = useState({});
  const navigate = useNavigate();

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) setErrors((prev) => ({ ...prev, [name]: '' }));
  };

  const validateForm = () => {
    const newErrors = {};
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!formData.name.strip()) newErrors.name = 'Full name is required';
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!emailRegex.test(formData.email)) {
      newErrors.email = 'Invalid email structure';
    }
    if (!formData.password || formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleRegister = (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    
    const newUser = {
      name: formData.name,
      email: formData.email.toLowerCase(),
      password: formData.password
    };

    localStorage.setItem('mock_user_db', JSON.stringify(newUser));
    alert('Account created successfully! Redirecting to login...');
    navigate('/login');
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h2>Create Account</h2>
          <p>Sign up to start tracking your session metrics</p>
        </div>

        <form onSubmit={handleRegister} className="login-form" noValidate>
          <div className={`form-group ${errors.name ? 'has-error' : ''}`}>
            <label htmlFor="name">Full Name</label>
            <div className="input-wrapper">
              <User className="input-icon" size={18} />
              <input type="text" id="name" name="name" value={formData.name} onChange={handleInputChange} placeholder="John Doe" />
            </div>
            {errors.name && <span className="error-message">{errors.name}</span>}
          </div>

          <div className={`form-group ${errors.email ? 'has-error' : ''}`}>
            <label htmlFor="email">Email Address</label>
            <div className="input-wrapper">
              <Mail className="input-icon" size={18} />
              <input type="email" id="email" name="email" value={formData.email} onChange={handleInputChange} placeholder="name@company.com" />
            </div>
            {errors.email && <span className="error-message">{errors.email}</span>}
          </div>

          <div className={`form-group ${errors.password ? 'has-error' : ''}`}>
            <label htmlFor="password">Password</label>
            <div className="input-wrapper">
              <Lock className="input-icon" size={18} />
              <input type="password" id="password" name="password" value={formData.password} onChange={handleInputChange} placeholder="••••••••" />
            </div>
            {errors.password && <span className="error-message">{errors.password}</span>}
          </div>

          <button type="submit" className="submit-btn">Sign Up</button>
        </form>

        <div className="login-footer">
  <p>
    Don't have an account? <Link to="/register">Sign up</Link>
  </p>
</div>
      </div>
    </div>
  );
};

export default Register;
