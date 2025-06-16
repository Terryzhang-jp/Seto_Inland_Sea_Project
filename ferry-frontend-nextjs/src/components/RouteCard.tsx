'use client';

import React from 'react';
import { ClockIcon, CurrencyYenIcon, TruckIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { FerryRoute } from '@/types';
import { getIslandIcon } from '@/lib/islands';

interface RouteCardProps {
  route: FerryRoute;
}

const RouteCard: React.FC<RouteCardProps> = ({ route }) => {
  // 获取船只类型图标
  const getShipIcon = (shipType: string) => {
    if (shipType.includes('フェリー')) return '⛴️';
    if (shipType.includes('高速船')) return '🚤';
    if (shipType.includes('旅客船')) return '🛥️';
    return '🚢';
  };

  // 获取公司颜色
  const getCompanyColor = (company: string) => {
    const colors: { [key: string]: string } = {
      '四国汽船': 'bg-blue-100 text-blue-800',
      'ジャンボフェリー': 'bg-green-100 text-green-800',
      '国際両備フェリー': 'bg-purple-100 text-purple-800',
      '四国フェリー': 'bg-orange-100 text-orange-800',
      '雌雄島海運': 'bg-pink-100 text-pink-800',
      '豊島フェリー': 'bg-indigo-100 text-indigo-800',
      '小豆島豊島フェリー': 'bg-yellow-100 text-yellow-800',
    };
    return colors[company] || 'bg-gray-100 text-gray-800';
  };

  // 计算航行时间
  const calculateDuration = (departure: string, arrival: string) => {
    try {
      const [depHour, depMin] = departure.split(':').map(Number);
      const [arrHour, arrMin] = arrival.split(':').map(Number);
      
      const depMinutes = depHour * 60 + depMin;
      let arrMinutes = arrHour * 60 + arrMin;
      
      // 处理跨日情况
      if (arrMinutes < depMinutes) {
        arrMinutes += 24 * 60;
      }
      
      const duration = arrMinutes - depMinutes;
      const hours = Math.floor(duration / 60);
      const minutes = duration % 60;
      
      if (hours > 0) {
        return `${hours}时${minutes}分`;
      } else {
        return `${minutes}分`;
      }
    } catch {
      return '-';
    }
  };

  return (
    <div className="card">
      {/* 头部：路线和公司 */}
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <div className="flex items-center space-x-3 mb-2">
            <div className="flex items-center space-x-2">
              <span className="text-xl">{getIslandIcon(route.departure_port)}</span>
              <span className="text-lg text-gray-400">→</span>
              <span className="text-xl">{getIslandIcon(route.arrival_port)}</span>
            </div>
            <h3 className="text-lg font-semibold text-gray-900">
              {route.departure_port} → {route.arrival_port}
            </h3>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-lg">{getShipIcon(route.ship_type)}</span>
            <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${getCompanyColor(route.company)}`}>
              {route.company}
            </span>
          </div>
        </div>
      </div>

      {/* 时间信息 */}
      <div className="grid grid-cols-3 gap-4 mb-4 p-3 bg-gray-50 rounded-lg">
        <div className="text-center">
          <div className="text-xs text-gray-500 mb-1">出发时间</div>
          <div className="text-lg font-semibold text-blue-600">{route.departure_time}</div>
        </div>
        <div className="text-center">
          <div className="text-xs text-gray-500 mb-1">航行时间</div>
          <div className="text-sm font-medium text-gray-700 flex items-center justify-center">
            <ClockIcon className="h-4 w-4 mr-1" />
            {calculateDuration(route.departure_time, route.arrival_time)}
          </div>
        </div>
        <div className="text-center">
          <div className="text-xs text-gray-500 mb-1">到达时间</div>
          <div className="text-lg font-semibold text-blue-600">{route.arrival_time}</div>
        </div>
      </div>

      {/* 详细信息 */}
      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-600">船只类型:</span>
          <span className="font-medium">{route.ship_type}</span>
        </div>
        
        <div className="flex justify-between">
          <span className="text-gray-600">运营日期:</span>
          <span className="font-medium">{route.operating_days}</span>
        </div>
        
        <div className="flex justify-between">
          <span className="text-gray-600 flex items-center">
            <CurrencyYenIcon className="h-4 w-4 mr-1" />
            大人票价:
          </span>
          <span className="font-medium text-green-600">{route.adult_fare}</span>
        </div>
        
        <div className="flex justify-between">
          <span className="text-gray-600 flex items-center">
            <CurrencyYenIcon className="h-4 w-4 mr-1" />
            小人票价:
          </span>
          <span className="font-medium text-green-600">{route.child_fare}</span>
        </div>
      </div>

      {/* 载运信息 */}
      <div className="flex space-x-4 mt-4 pt-4 border-t border-gray-200">
        <div className={`flex items-center space-x-1 text-xs px-2 py-1 rounded-full ${
          route.allows_vehicles ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
        }`}>
          {route.allows_vehicles ? (
            <TruckIcon className="h-3 w-3" />
          ) : (
            <XMarkIcon className="h-3 w-3" />
          )}
          <span>{route.allows_vehicles ? '可载车辆' : '不可载车辆'}</span>
        </div>
        
        <div className={`flex items-center space-x-1 text-xs px-2 py-1 rounded-full ${
          route.allows_bicycles ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
        }`}>
          <span>{route.allows_bicycles ? '🚲' : '🚫'}</span>
          <span>{route.allows_bicycles ? '可载自行车' : '不可载自行车'}</span>
        </div>
      </div>

      {/* 备注 */}
      {route.notes && (
        <div className="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded text-xs text-yellow-800">
          <span className="font-medium">备注:</span> {route.notes}
        </div>
      )}
    </div>
  );
};

export default RouteCard;
