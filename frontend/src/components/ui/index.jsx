import React from 'react';

export const Button = ({ 
  variant = 'primary', 
  size = 'md', 
  className = '', 
  children, 
  disabled = false,
  loading = false,
  onClick,
  ...props 
}) => {
  const baseStyles = 'font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2';
  
  const variants = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed',
    secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-400 active:scale-95',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500 active:scale-95',
    success: 'bg-green-600 text-white hover:bg-green-700 focus:ring-green-500 active:scale-95',
    outline: 'border-2 border-blue-600 text-blue-600 hover:bg-blue-50 focus:ring-blue-500',
  };

  const sizes = {
    sm: 'px-3 py-1 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };

  return (
    <button
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className} ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
      disabled={disabled || loading}
      onClick={onClick}
      {...props}
    >
      {loading ? (
        <span className="flex items-center gap-2">
          <span className="animate-spin">⏳</span>
          {children}
        </span>
      ) : (
        children
      )}
    </button>
  );
};

export const Card = ({ className = '', children, ...props }) => {
  return (
    <div
      className={`bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-6 ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};

export const Input = ({ 
  label, 
  error, 
  className = '', 
  type = 'text',
  ...props 
}) => {
  return (
    <div className={`w-full ${className}`}>
      {label && <label className="label-base">{label}</label>}
      <input
        type={type}
        className={`input-base ${error ? 'border-red-500 focus:ring-red-500' : ''}`}
        {...props}
      />
      {error && <p className="text-red-500 text-sm mt-1">{error}</p>}
    </div>
  );
};

export const Select = ({ 
  label, 
  error, 
  className = '', 
  options = [],
  ...props 
}) => {
  return (
    <div className={`w-full ${className}`}>
      {label && <label className="label-base">{label}</label>}
      <select
        className={`input-base ${error ? 'border-red-500 focus:ring-red-500' : ''}`}
        {...props}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {error && <p className="text-red-500 text-sm mt-1">{error}</p>}
    </div>
  );
};

export const Modal = ({ 
  isOpen, 
  onClose, 
  title, 
  children, 
  actions,
  className = '',
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className={`bg-white rounded-lg shadow-lg max-w-md w-full mx-4 ${className}`}>
        <div className="flex justify-between items-center p-6 border-b">
          <h2 className="text-xl font-bold">{title}</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl"
          >
            ×
          </button>
        </div>
        <div className="p-6">{children}</div>
        <div className="flex gap-3 p-6 border-t justify-end">
          {actions && actions.map((action, idx) => (
            <Button
              key={idx}
              variant={action.variant || 'secondary'}
              onClick={action.onClick}
            >
              {action.label}
            </Button>
          ))}
        </div>
      </div>
    </div>
  );
};

export const Toast = ({ message, type = 'info', onClose }) => {
  React.useEffect(() => {
    const timer = setTimeout(onClose, 3000);
    return () => clearTimeout(timer);
  }, [onClose]);

  const colors = {
    success: 'bg-green-500',
    error: 'bg-red-500',
    info: 'bg-blue-500',
    warning: 'bg-yellow-500',
  };

  return (
    <div className={`fixed bottom-4 right-4 ${colors[type]} text-white px-6 py-3 rounded-lg shadow-lg animate-pulse z-50`}>
      {message}
    </div>
  );
};

export const Badge = ({ variant = 'primary', children, className = '' }) => {
  const variants = {
    primary: 'bg-blue-100 text-blue-800',
    success: 'bg-green-100 text-green-800',
    danger: 'bg-red-100 text-red-800',
    warning: 'bg-yellow-100 text-yellow-800',
    gray: 'bg-gray-100 text-gray-800',
  };

  return (
    <span className={`px-3 py-1 rounded-full text-sm font-medium ${variants[variant]} ${className}`}>
      {children}
    </span>
  );
};

export const Spinner = ({ size = 'md', className = '' }) => {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  return (
    <div className={`${sizes[size]} border-4 border-gray-200 border-t-blue-600 rounded-full animate-spin ${className}`}></div>
  );
};

export const Alert = ({ variant = 'info', children, onClose, className = '' }) => {
  const colors = {
    success: 'bg-green-50 border-green-200 text-green-800',
    error: 'bg-red-50 border-red-200 text-red-800',
    info: 'bg-blue-50 border-blue-200 text-blue-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
  };

  return (
    <div className={`border rounded-lg p-4 flex justify-between items-start ${colors[variant]} ${className}`}>
      <div>{children}</div>
      {onClose && (
        <button
          onClick={onClose}
          className="text-lg font-bold hover:opacity-70 ml-4"
        >
          ×
        </button>
      )}
    </div>
  );
};
