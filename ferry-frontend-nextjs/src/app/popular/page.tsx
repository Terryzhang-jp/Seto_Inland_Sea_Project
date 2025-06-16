'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { FerryAPI } from '@/lib/api';
import { PopularRoute } from '@/types';
import { StarIcon } from '@heroicons/react/24/outline';

export default function PopularPage() {
  const [popularRoutes, setPopularRoutes] = useState<PopularRoute[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  // 加载热门路线
  useEffect(() => {
    const loadPopularRoutes = async () => {
      try {
        setLoading(true);
        const response = await FerryAPI.getPopularRoutes();
        if (response.success) {
          setPopularRoutes(response.data);
        } else {
          setError('加载热门路线失败');
        }
      } catch (error) {
        console.error('Failed to load popular routes:', error);
        setError('加载热门路线时发生错误');
      } finally {
        setLoading(false);
      }
    };

    loadPopularRoutes();
  }, []);

  // 点击路线跳转到主页搜索
  const handleRouteClick = (route: PopularRoute) => {
    const searchParams = new URLSearchParams({
      departure: route.departure,
      arrival: route.arrival
    });
    router.push(`/?${searchParams.toString()}`);
  };

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
            <StarIcon className="h-10 w-10 mr-3 text-yellow-500" />
            热门路线
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            瀬户内海最受欢迎的跳岛路线推荐，点击即可快速搜索。
          </p>
        </div>

        {/* 统计信息 */}
        <div className="mb-6">
          <p className="text-center text-gray-600">
            共 {popularRoutes.length} 条热门路线
          </p>
        </div>

        {/* 热门路线列表 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {popularRoutes.map((route, index) => (
            <div
              key={index}
              onClick={() => handleRouteClick(route)}
              className="card cursor-pointer hover:bg-blue-50 transition-all duration-200 hover:scale-105"
            >
              {/* 路线信息 */}
              <div className="flex items-center space-x-4 mb-4">
                <div className="text-3xl">🚢</div>
                <div className="flex-1">
                  <h3 className="text-xl font-semibold text-gray-900 mb-1">
                    {route.departure} → {route.arrival}
                  </h3>
                  <p className="text-sm text-gray-600">{route.description}</p>
                </div>
                <div className="text-blue-500 text-2xl">→</div>
              </div>

              {/* 推荐标识 */}
              <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                <div className="flex items-center space-x-1 text-yellow-600">
                  <StarIcon className="h-4 w-4" />
                  <span className="text-sm font-medium">热门推荐</span>
                </div>
                <span className="text-sm text-gray-500">点击搜索</span>
              </div>
            </div>
          ))}
        </div>

        {/* 提示信息 */}
        <div className="mt-12 text-center">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 max-w-2xl mx-auto">
            <h3 className="text-lg font-semibold text-blue-900 mb-2">💡 使用提示</h3>
            <p className="text-blue-700">
              点击任意热门路线卡片，系统将自动跳转到搜索页面并显示该路线的所有船班信息。
              您也可以在主页面直接输入出发地和目的地进行搜索。
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
