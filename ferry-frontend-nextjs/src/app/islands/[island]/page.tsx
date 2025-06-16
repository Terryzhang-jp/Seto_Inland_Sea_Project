'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { FerryAPI } from '@/lib/api';
import { IslandTransport, BicycleRental, BusSchedule, OtherTransport } from '@/types';

export default function IslandDetailPage() {
  const params = useParams();
  const islandName = params.island as string;
  
  const [island, setIsland] = useState<IslandTransport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'bicycle' | 'bus' | 'other'>('bicycle');

  useEffect(() => {
    const fetchIslandDetail = async () => {
      try {
        setLoading(true);
        const response = await FerryAPI.getIslandByName(islandName);
        if (response.success) {
          setIsland(response.data);
        } else {
          setError('获取岛屿详细信息失败');
        }
      } catch (err) {
        setError('网络错误，请稍后重试');
        console.error('Error fetching island detail:', err);
      } finally {
        setLoading(false);
      }
    };

    if (islandName) {
      fetchIslandDetail();
    }
  }, [islandName]);

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

  if (error || !island) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 text-lg">{error || '岛屿信息不存在'}</p>
          <button 
            onClick={() => window.history.back()} 
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            返回
          </button>
        </div>
      </div>
    );
  }

  // 按店铺分组自行车租赁
  const groupBicycleRentals = () => {
    const grouped: { [key: string]: BicycleRental[] } = {};

    island.bicycle_rentals.forEach(rental => {
      const key = rental.shop_name;
      if (!grouped[key]) {
        grouped[key] = [];
      }
      grouped[key].push(rental);
    });

    return grouped;
  };

  const renderBicycleRentals = () => {
    const groupedRentals = groupBicycleRentals();
    const shopNames = Object.keys(groupedRentals);

    if (shopNames.length === 0) {
      return (
        <div className="text-center py-8">
          <p className="text-gray-500">该岛屿无自行车租赁服务</p>
        </div>
      );
    }

    return (
      <div className="space-y-6">
        {shopNames.map((shopName) => {
          const rentals = groupedRentals[shopName];
          const firstRental = rentals[0];

          return (
            <div key={shopName} className="bg-white rounded-lg border border-gray-200 overflow-hidden">
              {/* 店铺信息 */}
              <div className="bg-green-50 px-6 py-4 border-b border-gray-200">
                <div className="flex flex-col md:flex-row md:items-start md:justify-between">
                  <div className="flex-1">
                    <h4 className="text-lg font-semibold text-gray-900">{shopName}</h4>
                    <div className="mt-2 space-y-1">
                      <p className="text-sm text-gray-600">📍 位置: {firstRental.location}</p>
                      <p className="text-sm text-gray-600">🕒 营业时间: {firstRental.operating_hours}</p>
                      <p className="text-sm text-gray-600">📞 联系方式: {firstRental.contact}</p>
                    </div>
                  </div>
                  {firstRental.notes && (
                    <div className="mt-3 md:mt-0 md:ml-4">
                      <p className="text-sm text-orange-600 bg-orange-100 px-3 py-1 rounded">
                        ⚠️ {firstRental.notes}
                      </p>
                    </div>
                  )}
                </div>
              </div>

              {/* 自行车类型和价格 */}
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {rentals.map((rental, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between mb-3">
                        <h5 className="font-medium text-gray-900">{rental.bicycle_type}</h5>
                        {rental.price_1day_yen && (
                          <span className="text-lg font-bold text-green-600">
                            ¥{rental.price_1day_yen}
                          </span>
                        )}
                      </div>

                      <div className="space-y-2 text-sm text-gray-600">
                        {rental.price_4hours_yen && (
                          <p>4小时: ¥{rental.price_4hours_yen}</p>
                        )}
                        {rental.price_overnight_yen && (
                          <p>过夜: ¥{rental.price_overnight_yen}</p>
                        )}
                        {rental.equipment && (
                          <p>🔧 设备: {rental.equipment}</p>
                        )}
                        {rental.insurance && (
                          <p>🛡️ 保险: {rental.insurance}</p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  // 按巴士类型和路线分组
  const groupBusSchedules = () => {
    const grouped: { [key: string]: BusSchedule[] } = {};

    island.bus_schedules.forEach(bus => {
      const key = `${bus.bus_type}_${bus.route}`;
      if (!grouped[key]) {
        grouped[key] = [];
      }
      grouped[key].push(bus);
    });

    return grouped;
  };

  const renderBusSchedules = () => {
    const groupedBuses = groupBusSchedules();
    const groupKeys = Object.keys(groupedBuses);

    if (groupKeys.length === 0) {
      return (
        <div className="text-center py-8">
          <p className="text-gray-500">该岛屿无巴士服务</p>
        </div>
      );
    }

    return (
      <div className="space-y-6">
        {groupKeys.map((groupKey) => {
          const buses = groupedBuses[groupKey];
          const firstBus = buses[0];

          return (
            <div key={groupKey} className="bg-white rounded-lg border border-gray-200 overflow-hidden">
              {/* 线路标题 */}
              <div className="bg-blue-50 px-6 py-4 border-b border-gray-200">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between">
                  <div>
                    <h4 className="text-lg font-semibold text-gray-900">{firstBus.bus_type}</h4>
                    <p className="text-sm text-gray-600 mt-1">{firstBus.route}</p>
                  </div>
                  <div className="mt-2 md:mt-0 text-right">
                    <p className="text-sm text-gray-600">运营商: {firstBus.operator}</p>
                    {firstBus.fare_adult_yen && (
                      <p className="text-lg font-semibold text-green-600">
                        ¥{firstBus.fare_adult_yen}
                        {firstBus.fare_child_yen && (
                          <span className="text-sm text-gray-500 ml-2">
                            (儿童: ¥{firstBus.fare_child_yen})
                          </span>
                        )}
                      </p>
                    )}
                  </div>
                </div>
                {firstBus.frequency && (
                  <p className="text-sm text-blue-600 mt-2">班次频率: {firstBus.frequency}</p>
                )}
                {firstBus.notes && (
                  <p className="text-sm text-orange-600 mt-2">⚠️ {firstBus.notes}</p>
                )}
              </div>

              {/* 时刻表 */}
              <div className="p-6">
                <div className="overflow-x-auto">
                  <table className="min-w-full">
                    <thead>
                      <tr className="border-b border-gray-200">
                        <th className="text-left py-2 px-3 text-sm font-medium text-gray-700">出发站</th>
                        <th className="text-left py-2 px-3 text-sm font-medium text-gray-700">到达站</th>
                        <th className="text-left py-2 px-3 text-sm font-medium text-gray-700">出发时间</th>
                        <th className="text-left py-2 px-3 text-sm font-medium text-gray-700">到达时间</th>
                        <th className="text-left py-2 px-3 text-sm font-medium text-gray-700">用时</th>
                      </tr>
                    </thead>
                    <tbody>
                      {buses.map((bus, index) => {
                        const duration = bus.departure_time && bus.arrival_time
                          ? calculateDuration(bus.departure_time, bus.arrival_time)
                          : '';

                        return (
                          <tr key={index} className={index % 2 === 0 ? 'bg-gray-50' : 'bg-white'}>
                            <td className="py-2 px-3 text-sm text-gray-900">{bus.departure_stop}</td>
                            <td className="py-2 px-3 text-sm text-gray-900">{bus.arrival_stop}</td>
                            <td className="py-2 px-3 text-sm font-medium text-blue-600">
                              {bus.departure_time || '-'}
                            </td>
                            <td className="py-2 px-3 text-sm font-medium text-blue-600">
                              {bus.arrival_time || '-'}
                            </td>
                            <td className="py-2 px-3 text-sm text-gray-600">{duration}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  // 计算行程时间
  const calculateDuration = (departureTime: string, arrivalTime: string): string => {
    try {
      const [depHour, depMin] = departureTime.split(':').map(Number);
      const [arrHour, arrMin] = arrivalTime.split(':').map(Number);

      const depMinutes = depHour * 60 + depMin;
      const arrMinutes = arrHour * 60 + arrMin;

      const diffMinutes = arrMinutes - depMinutes;

      if (diffMinutes < 0) return '';

      const hours = Math.floor(diffMinutes / 60);
      const minutes = diffMinutes % 60;

      if (hours > 0) {
        return `${hours}小时${minutes}分钟`;
      } else {
        return `${minutes}分钟`;
      }
    } catch {
      return '';
    }
  };

  // 按交通类型分组其他交通方式
  const groupOtherTransports = () => {
    const grouped: { [key: string]: OtherTransport[] } = {};

    island.other_transports.forEach(transport => {
      const key = transport.transport_type;
      if (!grouped[key]) {
        grouped[key] = [];
      }
      grouped[key].push(transport);
    });

    return grouped;
  };

  const renderOtherTransports = () => {
    const groupedTransports = groupOtherTransports();
    const transportTypes = Object.keys(groupedTransports);

    if (transportTypes.length === 0) {
      return (
        <div className="text-center py-8">
          <p className="text-gray-500">暂无其他交通方式信息</p>
        </div>
      );
    }

    return (
      <div className="space-y-6">
        {transportTypes.map((transportType) => {
          const transports = groupedTransports[transportType];

          return (
            <div key={transportType} className="bg-white rounded-lg border border-gray-200 overflow-hidden">
              {/* 交通类型标题 */}
              <div className="bg-purple-50 px-6 py-4 border-b border-gray-200">
                <h4 className="text-lg font-semibold text-gray-900">{transportType}</h4>
                <p className="text-sm text-gray-600 mt-1">共 {transports.length} 个服务选项</p>
              </div>

              {/* 服务列表 */}
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {transports.map((transport, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between mb-3">
                        <h5 className="font-medium text-gray-900">{transport.service_name}</h5>
                        {transport.price_yen && (
                          <span className="text-lg font-bold text-green-600">
                            ¥{transport.price_yen}
                          </span>
                        )}
                      </div>

                      <div className="space-y-2 text-sm text-gray-600">
                        <p>📍 位置: {transport.location}</p>
                        <p>🕒 营业时间: {transport.operating_hours}</p>
                        <p>📞 联系方式: {transport.contact}</p>
                        {transport.capacity && (
                          <p>👥 容量: {transport.capacity}</p>
                        )}
                        {transport.notes && (
                          <div className="mt-3 p-2 bg-orange-50 border border-orange-200 rounded">
                            <p className="text-orange-700">⚠️ {transport.notes}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* 页面标题 */}
        <div className="mb-8">
          <button 
            onClick={() => window.history.back()}
            className="mb-4 text-blue-600 hover:text-blue-800"
          >
            ← 返回岛屿列表
          </button>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">{island.island_name}</h1>
          <p className="text-gray-600">{island.island_name_en} - 交通信息详情</p>
        </div>

        {/* 标签页导航 */}
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('bicycle')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'bicycle'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                自行车租赁 ({island.bicycle_rentals.length})
              </button>
              <button
                onClick={() => setActiveTab('bus')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'bus'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                巴士时刻表 ({island.bus_schedules.length})
              </button>
              <button
                onClick={() => setActiveTab('other')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'other'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                其他交通 ({island.other_transports.length})
              </button>
            </nav>
          </div>
        </div>

        {/* 标签页内容 */}
        <div className="mb-8">
          {activeTab === 'bicycle' && renderBicycleRentals()}
          {activeTab === 'bus' && renderBusSchedules()}
          {activeTab === 'other' && renderOtherTransports()}
        </div>
      </div>
    </div>
  );
}
