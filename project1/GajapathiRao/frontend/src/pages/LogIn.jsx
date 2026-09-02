import React, { useState, useEffect } from 'react';
import { Eye, EyeOff, Lock, Mail } from 'lucide-react';
import '../styles/login.scss';
import { Link } from 'react-router-dom'; 

const Login = () => {
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [errors, setErrors] = useState({});
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [apiError, setApiError] = useState('');

  useEffect(() => {
    const existingUser = localStorage.getItem('mock_user_db');
    if (!existingUser) {
      const defaultUser = {
        email: 'user@example.com',
        password: 'password123', 
        name: 'Gajapathi Rao'
      };
      localStorage.setItem('mock_user_db', JSON.stringify(defaultUser));
    }
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setApiError(''); 
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!formData.email) {
      newErrors.email = 'Email address is required';
    } else if (!emailRegex.test(formData.email)) {
      newErrors.email = 'Please enter a valid email';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    setIsLoading(true);
    setApiError('');

  
    setTimeout(() => {
    
      const storedUserRaw = localStorage.getItem('mock_user_db');
      const storedUser = storedUserRaw ? JSON.parse(storedUserRaw) : null;

      if (!storedUser) {
        setApiError('No registered users found in local database.');
        setIsLoading(false);
        return;
      }

     
      if (
        formData.email.toLowerCase() === storedUser.email.toLowerCase() &&
        formData.password === storedUser.password
      ) {
        
        const fakeToken = `mock_jwt_token_${btoa(formData.email)}`;
        
        localStorage.setItem('auth_token', fakeToken);
        localStorage.setItem('current_user', JSON.stringify({
          email: storedUser.email,
          name: storedUser.name,
          loginTime: new Date().toISOString()
        }));

        alert(`Welcome back, ${storedUser.name}! Login Simulated.`);
        window.location.reload(); 
      } else {
       
        setApiError('Invalid email address or password.');
      }
      
      setIsLoading(false);
    }, 1000);
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h2>Welcome Back</h2>
          {/* <p>Sign in with <strong>user@example.com</strong> / <strong>password123</strong></p> */}
        </div>

        <form onSubmit={handleSubmit} className="login-form" noValidate>
          {apiError && <div className="api-error-alert">{apiError}</div>}

          <div className={`form-group ${errors.email ? 'has-error' : ''}`}>
            <label htmlFor="email">Email Address</label>
            <div className="input-wrapper">
              <Mail className="input-icon" size={18} />
              <input
                type="email"
                id="email"
                name="email"
                placeholder="name@company.com"
                value={formData.email}
                onChange={handleInputChange}
                disabled={isLoading}
              />
            </div>
            {errors.email && <span className="error-message">{errors.email}</span>}
          </div>

          <div className={`form-group ${errors.password ? 'has-error' : ''}`}>
            <div className="label-row">
              <label htmlFor="password">Password</label>
              {/* <a href="#forgot" className="forgot-link">Forgot password?</a> */}
            </div>
            <div className="input-wrapper">
              <Lock className="input-icon" size={18} />
              <input
                type={showPassword ? 'text' : 'password'}
                id="password"
                name="password"
                placeholder="••••••••"
                value={formData.password}
                onChange={handleInputChange}
                disabled={isLoading}
              />
              <button
                type="button"
                className="toggle-password"
                onClick={() => setShowPassword(!showPassword)}
                tabIndex="-1"
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
            {errors.password && <span className="error-message">{errors.password}</span>}
          </div>

          <button type="submit" className="submit-btn" disabled={isLoading}>
            {isLoading ? <div className="spinner"></div> : 'Log In'}
          </button>
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

export default Login;
