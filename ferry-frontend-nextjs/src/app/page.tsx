'use client';

import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import Image from 'next/image';
import SearchForm from '../components/SearchForm';
import RouteGroup from '../components/RouteGroup';
import { FerryAPI } from '../lib/api';
import { RouteSearchParams, PopularRoute } from '../types';
import { getIslandIcon } from '../lib/islands';
import { groupRoutesByPath, RouteGroup as RouteGroupType } from '../lib/utils';
import { ExclamationTriangleIcon } from '@heroicons/react/24/outline';

export default function Home() {
  const searchParams = useSearchParams();
  const [routeGroups, setRouteGroups] = useState<RouteGroupType[]>([]);
  const [popularRoutes, setPopularRoutes] = useState<PopularRoute[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentSearchParams, setCurrentSearchParams] = useState<RouteSearchParams>({});
  const [pagination, setPagination] = useState({
    total: 0,
    page: 1,
    limit: 20,
  });

  // 加载热门路线和处理URL参数
  useEffect(() => {
    const loadPopularRoutes = async () => {
      try {
        const response = await FerryAPI.getPopularRoutes();
        if (response.success) {
          setPopularRoutes(response.data);
        }
      } catch (error) {
        console.error('Failed to load popular routes:', error);
      }
    };

    loadPopularRoutes();

    // 检查URL参数并自动搜索
    const departure = searchParams.get('departure');
    const arrival = searchParams.get('arrival');

    if (departure || arrival) {
      const params: RouteSearchParams = {
        departure: departure || '',
        arrival: arrival || '',
        page: 1,
        limit: 20,
      };
      handleSearch(params);
    }
  }, [searchParams]);

  // 搜索航线
  const handleSearch = async (params: RouteSearchParams) => {
    setLoading(true);
    setError(null);
    setCurrentSearchParams(params);

    try {
      const response = await FerryAPI.searchRoutes(params);
      if (response.success) {
        // 按路线分组
        const grouped = groupRoutesByPath(response.data);
        setRouteGroups(grouped);
        setPagination({
          total: response.total || 0,
          page: response.page || 1,
          limit: response.limit || 20,
        });
      } else {
        setError('搜索失败，请重试');
      }
    } catch (error) {
      console.error('Search failed:', error);
      setError('搜索时发生错误，请检查网络连接');
    } finally {
      setLoading(false);
    }
  };

  // 分页处理
  const handlePageChange = (newPage: number) => {
    const newParams = { ...currentSearchParams, page: newPage };
    handleSearch(newParams);
  };

  // 快速搜索热门路线
  const handlePopularRouteClick = (route: PopularRoute) => {
    const params: RouteSearchParams = {
      departure: route.departure,
      arrival: route.arrival,
      page: 1,
      limit: 20,
    };
    handleSearch(params);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 页面标题 */}
        <div className="text-center mb-10">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            🌊 瀬户内海跳岛查询
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-4">
            输入起始岛屿和目的地，查找所有可用的船班路线和时间
          </p>
          <p className="text-lg text-gray-500">
            覆盖 <span className="font-semibold text-blue-600">直島、豊島、小豆島、犬島、女木島、男木島</span> 等主要岛屿
          </p>
        </div>

        {/* 跳島主題横幅 */}
        <div className="mb-8 flex justify-center">
          <Image
            src="/island-hopping-banner.svg"
            alt="瀬戸内海跳島查詢"
            width={1024}
            height={300}
            className="w-full max-w-4xl h-auto rounded-lg shadow-lg"
          />
        </div>

        {/* 搜索表单 */}
        <div className="mb-8">
          <SearchForm onSearch={handleSearch} loading={loading} />
        </div>

        {/* 热门路线 */}
        {popularRoutes.length > 0 && routeGroups.length === 0 && (
          <div className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-6 flex items-center">
              <span className="mr-2">⭐</span>
              热门跳岛路线
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {popularRoutes.map((route, index) => (
                <div
                  key={index}
                  onClick={() => handlePopularRouteClick(route)}
                  className="card cursor-pointer hover:bg-blue-50 transition-all duration-200 hover:scale-105"
                >
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                      <span className="text-2xl">{getIslandIcon(route.departure)}</span>
                      <span className="text-xl text-gray-400">→</span>
                      <span className="text-2xl">{getIslandIcon(route.arrival)}</span>
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 text-lg">
                        {route.departure} → {route.arrival}
                      </h3>
                      <p className="text-sm text-gray-600">{route.description}</p>
                    </div>
                    <div className="text-blue-500 text-2xl">🔍</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 搜索结果 */}
        {routeGroups.length > 0 && (
          <div>
            {/* 结果统计 */}
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-semibold text-gray-900">
                搜索结果 ({routeGroups.length} 条路线，{pagination.total} 个班次)
              </h2>
              <div className="text-sm text-gray-600">
                第 {pagination.page} 页，共 {Math.ceil(pagination.total / pagination.limit)} 页
              </div>
            </div>

            {/* 路线分组列表 */}
            <div className="space-y-6 mb-8">
              {routeGroups.map((routeGroup, index) => (
                <RouteGroup key={index} routeGroup={routeGroup} />
              ))}
            </div>

            {/* 分页 */}
            {pagination.total > pagination.limit && (
              <div className="flex justify-center space-x-2">
                <button
                  onClick={() => handlePageChange(pagination.page - 1)}
                  disabled={pagination.page <= 1 || loading}
                  className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  上一页
                </button>

                <span className="flex items-center px-4 py-2 text-sm text-gray-700">
                  {pagination.page} / {Math.ceil(pagination.total / pagination.limit)}
                </span>

                <button
                  onClick={() => handlePageChange(pagination.page + 1)}
                  disabled={pagination.page >= Math.ceil(pagination.total / pagination.limit) || loading}
                  className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  下一页
                </button>
              </div>
            )}
          </div>
        )}

        {/* 错误提示 */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-center">
              <ExclamationTriangleIcon className="h-5 w-5 text-red-500 mr-2" />
              <span className="text-red-700">{error}</span>
            </div>
          </div>
        )}

        {/* 加载状态 */}
        {loading && (
          <div className="text-center py-8">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-2 text-gray-600">搜索中...</p>
          </div>
        )}

        {/* 空状态 */}
        {!loading && routeGroups.length === 0 && Object.keys(currentSearchParams).length > 0 && !error && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">未找到匹配的航线</h3>
            <p className="text-gray-600 mb-4">请尝试调整搜索条件</p>
            <button
              onClick={() => {
                setRouteGroups([]);
                setCurrentSearchParams({});
              }}
              className="btn-primary"
            >
              重新搜索
            </button>
          </div>
        )}
      </div>
    </div>
  );
}