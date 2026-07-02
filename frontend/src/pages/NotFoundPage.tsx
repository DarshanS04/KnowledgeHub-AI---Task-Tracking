import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import { BookOpen } from 'lucide-react';

export const NotFoundPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#090d16] flex flex-col items-center justify-center p-6 text-center">
      <div className="space-y-6 max-w-md">
        <div className="flex justify-center mb-4">
          <BookOpen className="h-16 w-16 text-indigo-500" />
        </div>
        <h1 className="text-6xl font-extrabold text-indigo-500">404</h1>
        <h2 className="text-2xl font-bold text-slate-100">Page Not Found</h2>
        <p className="text-slate-400 text-sm">
          The knowledge space you are trying to access does not exist or has been shifted.
        </p>
        <div className="pt-4">
          <Link to="/">
            <Button>Return to Safety</Button>
          </Link>
        </div>
      </div>
    </div>
  );
};
export default NotFoundPage;
