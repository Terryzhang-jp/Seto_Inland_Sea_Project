'use client';

import React, { useState, useEffect } from 'react';
import { FerryAPI } from '../../lib/api';
import { Company } from '../../types';
import { BuildingOfficeIcon, PhoneIcon, GlobeAltIcon } from '@heroicons/react/24/outline';

export default function CompaniesPage() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 加载公司数据
  useEffect(() => {
    const loadCompanies = async () => {
      try {
        setLoading(true);
        const response = await FerryAPI.getCompanies();
        if (response.success) {
          setCompanies(response.data);
        } else {
          setError('加载公司信息失败');
        }
      } catch (error) {
        console.error('Failed to load companies:', error);
        setError('加载公司信息时发生错误');
      } finally {
        setLoading(false);
      }
    };

    loadCompanies();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600">加载中...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <span className="text-red-500 mr-2">⚠️</span>
            <span className="text-red-700">{error}</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 页面标题 */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4 flex items-center justify-center">
            <BuildingOfficeIcon className="h-10 w-10 mr-3 text-blue-600" />
            船运公司
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            瀬户内海各船运公司详细信息，包括联系方式和主要航线。
          </p>
        </div>

        {/* 统计信息 */}
        <div className="mb-6">
          <p className="text-center text-gray-600">
            共 {companies.length} 家船运公司
          </p>
        </div>

        {/* 公司列表 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {companies.map((company, index) => (
            <div key={index} className="card">
              {/* 公司名称 */}
              <div className="flex items-center space-x-3 mb-4">
                <BuildingOfficeIcon className="h-8 w-8 text-blue-600" />
                <h3 className="text-lg font-semibold text-gray-900">{company.name}</h3>
              </div>

              {/* 联系电话 */}
              <div className="mb-4">
                <div className="flex items-center space-x-2">
                  <PhoneIcon className="h-4 w-4 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-700">联系电话</p>
                    <p className="text-sm text-gray-600">{company.phone}</p>
                  </div>
                </div>
              </div>

              {/* 网站 */}
              <div className="mb-4">
                <div className="flex items-center space-x-2">
                  <GlobeAltIcon className="h-4 w-4 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-700">官方网站</p>
                    <a 
                      href={company.website} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-sm text-blue-600 hover:text-blue-800 underline"
                    >
                      {company.website}
                    </a>
                  </div>
                </div>
              </div>

              {/* 主要航线 */}
              <div className="mb-4">
                <div className="flex items-start space-x-2">
                  <span className="text-gray-400 mt-1 text-sm">🚢</span>
                  <div>
                    <p className="text-sm font-medium text-gray-700">主要航线</p>
                    <p className="text-sm text-gray-600">{company.main_routes}</p>
                  </div>
                </div>
              </div>

              {/* 备注 */}
              {company.notes && (
                <div className="pt-4 border-t border-gray-200">
                  <div className="flex items-start space-x-2">
                    <span className="text-gray-400 mt-1 text-sm">📝</span>
                    <div>
                      <p className="text-sm font-medium text-gray-700">备注</p>
                      <p className="text-sm text-gray-600">{company.notes}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
