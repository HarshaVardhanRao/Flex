import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Navigate } from 'react-router-dom';
import CertificateForm from '../components/CertificateForm';
import Header from '../components/Header';

const AddCertificatePage = () => {
  const { user, loading } = useAuth();
  
  // If auth is loading, show a loading state
  if (loading) {
    return <div className="flex justify-center items-center h-screen">Loading...</div>;
  }
  
  // Redirect to login if user is not authenticated
  if (!user) {
    return <Navigate to="/login" replace={true} />;
  }
  
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="py-10 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="pb-5 border-b border-gray-200 mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Add New Certificate</h1>
          </div>
          
          <CertificateForm />
        </div>
      </main>
    </div>
  );
};

export default AddCertificatePage;
