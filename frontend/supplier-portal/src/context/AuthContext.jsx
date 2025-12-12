import { createContext, useState, useEffect } from 'react';
import { supplierApi } from '../services/api';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [supplier, setSupplier] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check session on mount
    checkSession();
  }, []);

  const checkSession = async () => {
    try {
      const response = await supplierApi.checkSession();
      if (response.authenticated && response.supplier) {
        setSupplier(response.supplier);
      } else {
        setSupplier(null);
      }
    } catch (error) {
      setSupplier(null);
    } finally {
      setLoading(false);
    }
  };

  const requestOTP = async (email) => {
    const response = await supplierApi.requestOTP(email);
    return response;
  };

  const verifyOTP = async (email, otpCode) => {
    const response = await supplierApi.verifyOTP(email, otpCode);
    if (response.success && response.supplier) {
      setSupplier(response.supplier);
    }
    return response;
  };

  const logout = async () => {
    try {
      await supplierApi.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setSupplier(null);
    }
  };

  const register = async (data) => {
    const response = await supplierApi.register(data);
    return response;
  };

  const value = { supplier, requestOTP, verifyOTP, logout, register, checkSession, loading };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

