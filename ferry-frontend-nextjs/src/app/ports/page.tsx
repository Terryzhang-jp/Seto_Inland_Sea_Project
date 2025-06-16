'use client';

import React, { useState, useEffect } from 'react';
import { FerryAPI } from '@/lib/api';
import { Port } from '@/types';
import { MagnifyingGlassIcon, MapPinIcon } from '@heroicons/react/24/outline';

export default function PortsPage() {
  const [ports, setPorts] = useState<Port[]>([]);
  const [filteredPorts, setFilteredPorts] = useState<Port[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  // 加载港口数据
  useEffect(() => {
    const loadPorts = async () => {
      try {
        setLoading(true);
        const response = await FerryAPI.getPorts();
        if (response.success) {
          setPorts(response.data);
          setFilteredPorts(response.data);
        } else {
          setError('加载港口信息失败');
        }
      } catch (error) {
        console.error('Failed to load ports:', error);
        setError('加载港口信息时发生错误');
      } finally {
        setLoading(false);
      }
    };

    loadPorts();
  }, []);

  // 搜索过滤
  useEffect(() => {
    if (searchQuery.trim() === '') {
      setFilteredPorts(ports);
    } else {
      const filtered = ports.filter(port =>
        port.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        port.island.toLowerCase().includes(searchQuery.toLowerCase()) ||
        port.address.toLowerCase().includes(searchQuery.toLowerCase()) ||
        port.features.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setFilteredPorts(filtered);
    }
  }, [searchQuery, ports]);

  // 获取岛屿图标
  const getIslandIcon = (island: string) => {
    const icons: { [key: string]: string } = {
      '直島': '🎨',
      '豊島': '🏛️',
      '小豆島': '🫒',
      '犬島': '🏭',
      '女木島': '👹',
      '男木島': '🐱',
      '本州': '🏙️',
    };
    return icons[island] || '🏝️';
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
            <MapPinIcon className="h-10 w-10 mr-3 text-blue-600" />
            港口信息
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            瀬户内海各岛屿港口详细信息，包括位置、特色和连接信息。
          </p>
        </div>

        {/* 搜索框 */}
        <div className="mb-8">
          <div className="max-w-md mx-auto">
            <div className="relative">
              <input
                type="text"
                className="input-field pl-10"
                placeholder="搜索港口、岛屿或地址..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
              </div>
            </div>
          </div>
        </div>

        {/* 统计信息 */}
        <div className="mb-6">
          <p className="text-center text-gray-600">
            共 {filteredPorts.length} 个港口
            {searchQuery && ` (搜索: "${searchQuery}")`}
          </p>
        </div>

        {/* 港口列表 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredPorts.map((port, index) => (
            <div key={index} className="card">
              {/* 港口名称和岛屿 */}
              <div className="flex items-center space-x-3 mb-4">
                <span className="text-3xl">{getIslandIcon(port.island)}</span>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{port.name}</h3>
                  <p className="text-sm text-gray-600">{port.island}</p>
                </div>
              </div>

              {/* 地址 */}
              <div className="mb-4">
                <div className="flex items-start space-x-2">
                  <MapPinIcon className="h-4 w-4 text-gray-400 mt-1 flex-shrink-0" />
                  <div>
                    <p className="text-sm font-medium text-gray-700">地址</p>
                    <p className="text-sm text-gray-600">{port.address}</p>
                  </div>
                </div>
              </div>

              {/* 特点 */}
              <div className="mb-4">
                <div className="flex items-start space-x-2">
                  <span className="text-gray-400 mt-1 text-sm">✨</span>
                  <div>
                    <p className="text-sm font-medium text-gray-700">特点</p>
                    <p className="text-sm text-gray-600">{port.features}</p>
                  </div>
                </div>
              </div>

              {/* 连接信息 */}
              <div className="pt-4 border-t border-gray-200">
                <div className="flex items-start space-x-2">
                  <span className="text-gray-400 mt-1 text-sm">🔗</span>
                  <div>
                    <p className="text-sm font-medium text-gray-700">连接岛屿</p>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {port.connections.split('、').map((connection, idx) => (
                        <span
                          key={idx}
                          className="inline-block px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full"
                        >
                          {connection.trim()}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* 空状态 */}
        {filteredPorts.length === 0 && searchQuery && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">未找到匹配的港口</h3>
            <p className="text-gray-600 mb-4">请尝试其他搜索关键词</p>
            <button
              onClick={() => setSearchQuery('')}
              className="btn-primary"
            >
              显示所有港口
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
