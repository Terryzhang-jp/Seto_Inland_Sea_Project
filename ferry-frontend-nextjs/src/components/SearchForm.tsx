'use client';

import React, { useState } from 'react';
import { MagnifyingGlassIcon, ArrowPathIcon } from '@heroicons/react/24/outline';
import { RouteSearchParams } from '@/types';
import IslandSelect from './IslandSelect';

interface SearchFormProps {
  onSearch: (params: RouteSearchParams) => void;
  loading?: boolean;
}

const SearchForm: React.FC<SearchFormProps> = ({ onSearch, loading = false }) => {
  const [formData, setFormData] = useState<RouteSearchParams>({
    departure: '',
    arrival: '',
    page: 1,
    limit: 20,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // 清理空值
    const cleanParams: RouteSearchParams = {};
    Object.entries(formData).forEach(([key, value]) => {
      if (value !== '' && value !== undefined) {
        cleanParams[key as keyof RouteSearchParams] = value;
      }
    });
    
    onSearch(cleanParams);
  };

  const handleReset = () => {
    setFormData({
      departure: '',
      arrival: '',
      page: 1,
      limit: 20,
    });
  };

  const handleInputChange = (field: keyof RouteSearchParams, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <div className="card">
      <div className="flex items-center space-x-2 mb-6">
        <MagnifyingGlassIcon className="h-6 w-6 text-blue-600" />
        <h2 className="text-xl font-semibold text-gray-900">搜索船班</h2>
      </div>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* 出发地和到达地 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <IslandSelect
            value={formData.departure || ''}
            onChange={(value) => handleInputChange('departure', value)}
            placeholder="选择出发岛屿或港口"
            label="出发岛屿"
            icon="🏝️"
          />

          <IslandSelect
            value={formData.arrival || ''}
            onChange={(value) => handleInputChange('arrival', value)}
            placeholder="选择目的地岛屿或港口"
            label="到达岛屿"
            icon="🎯"
          />
        </div>

        {/* 按钮 */}
        <div className="flex space-x-4 pt-6">
          <button
            type="submit"
            disabled={loading}
            className="btn-primary flex-1 flex items-center justify-center space-x-2 text-lg py-3"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>搜索中...</span>
              </>
            ) : (
              <>
                <MagnifyingGlassIcon className="h-5 w-5" />
                <span>🔍 搜索船班</span>
              </>
            )}
          </button>

          <button
            type="button"
            onClick={handleReset}
            className="btn-secondary flex items-center space-x-2 text-lg py-3 px-6"
          >
            <ArrowPathIcon className="h-5 w-5" />
            <span>重置</span>
          </button>
        </div>
      </form>
    </div>
  );
};

export default SearchForm;
