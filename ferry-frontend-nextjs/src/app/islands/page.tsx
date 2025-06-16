'use client';

import { useState, useEffect } from 'react';
import { FerryAPI } from '@/lib/api';
import { IslandTransportSummary } from '@/types';

export default function IslandsPage() {
  const [islands, setIslands] = useState<IslandTransportSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchIslands = async () => {
      try {
        setLoading(true);
        const response = await FerryAPI.getIslandsSummary();
        if (response.success) {
          setIslands(response.data);
        } else {
          setError('获取岛屿信息失败');
        }
      } catch (err) {
        setError('网络错误，请稍后重试');
        console.error('Error fetching islands:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchIslands();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">加载中...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 text-lg">{error}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            重试
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">濑户内海岛屿交通信息</h1>
          <p className="text-gray-600">查看各岛屿的交通方式、自行车租赁和巴士信息</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {islands.map((island) => (
            <div key={island.island_name_en} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
              <div className="mb-4">
                <h2 className="text-xl font-semibold text-gray-900">{island.island_name}</h2>
                <p className="text-sm text-gray-500">{island.island_name_en}</p>
              </div>

              <div className="space-y-3">
                {/* 交通方式 */}
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-1">可用交通方式</h3>
                  <div className="flex flex-wrap gap-1">
                    {island.transport_types.map((type, index) => (
                      <span 
                        key={index}
                        className="inline-block px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded"
                      >
                        {type}
                      </span>
                    ))}
                  </div>
                </div>

                {/* 自行车租赁 */}
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-1">自行车租赁</h3>
                  {island.has_bicycle_rental ? (
                    <div className="text-sm text-gray-600">
                      <p>租赁店数量: {island.bicycle_rental_count}家</p>
                      {island.min_bicycle_price && (
                        <p>最低价格: ¥{island.min_bicycle_price}/天</p>
                      )}
                    </div>
                  ) : (
                    <p className="text-sm text-red-600">无自行车租赁服务</p>
                  )}
                </div>

                {/* 巴士服务 */}
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-1">巴士服务</h3>
                  <p className="text-sm text-gray-600">
                    {island.has_bus ? '有巴士服务' : '无巴士服务'}
                  </p>
                </div>

                {/* 特殊说明 */}
                {island.special_notes && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-1">特殊说明</h3>
                    <p className="text-sm text-orange-600">{island.special_notes}</p>
                  </div>
                )}
              </div>

              <div className="mt-4 pt-4 border-t border-gray-200">
                <a 
                  href={`/islands/${island.island_name_en}`}
                  className="inline-block w-full text-center px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                >
                  查看详细信息
                </a>
              </div>
            </div>
          ))}
        </div>

        {islands.length === 0 && !loading && (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">暂无岛屿信息</p>
          </div>
        )}
      </div>
    </div>
  );
}
