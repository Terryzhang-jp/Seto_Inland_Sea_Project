'use client';

import React, { useState } from 'react';
import { ChevronDownIcon, ChevronUpIcon, ClockIcon, CurrencyYenIcon, TruckIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { RouteGroup as RouteGroupType } from '@/lib/utils';
import { calculateDuration } from '@/lib/utils';
import { getIslandIcon } from '@/lib/islands';

interface RouteGroupProps {
  routeGroup: RouteGroupType;
}

const RouteGroup: React.FC<RouteGroupProps> = ({ routeGroup }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  // 检查是否为期间限定航线
  const isLimitedPeriod = routeGroup.schedules.some(schedule =>
    schedule.operating_days === '期間限定'
  );

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

  return (
    <div className={`card ${isLimitedPeriod ? 'border-2 border-orange-300 bg-orange-50' : ''}`}>
      {/* 期间限定标识 */}
      {isLimitedPeriod && (
        <div className="mb-3 flex items-center space-x-2">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-orange-100 text-orange-800">
            🎨 期間限定航路
          </span>
          <span className="text-sm text-orange-700">
            瀬戸内国際芸術祭期間のみ運航
          </span>
        </div>
      )}

      {/* 路线头部 */}
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <div className="flex items-center space-x-3 mb-3">
            <div className="flex items-center space-x-2">
              <span className="text-2xl">{getIslandIcon(routeGroup.departure)}</span>
              <span className="text-xl text-gray-400">→</span>
              <span className="text-2xl">{getIslandIcon(routeGroup.arrival)}</span>
            </div>
            <h3 className="text-xl font-bold text-gray-900">
              {routeGroup.departure} → {routeGroup.arrival}
            </h3>
          </div>
          
          <div className="flex items-center space-x-4 text-sm text-gray-600">
            <span className="flex items-center">
              <ClockIcon className="h-4 w-4 mr-1" />
              {routeGroup.totalSchedules} 班次
            </span>
            <span className="flex items-center">
              <CurrencyYenIcon className="h-4 w-4 mr-1" />
              最低 {routeGroup.minPrice}円起
            </span>
            <div className="flex space-x-1">
              {routeGroup.companies.map((company, index) => (
                <span key={index} className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${getCompanyColor(company)}`}>
                  {company}
                </span>
              ))}
            </div>
          </div>
        </div>
        
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center space-x-1 text-blue-600 hover:text-blue-800 transition-colors"
        >
          <span className="text-sm font-medium">
            {isExpanded ? '收起' : '展开时刻表'}
          </span>
          {isExpanded ? (
            <ChevronUpIcon className="h-4 w-4" />
          ) : (
            <ChevronDownIcon className="h-4 w-4" />
          )}
        </button>
      </div>

      {/* 快速预览（前3个班次） */}
      {!isExpanded && (
        <div className="bg-gray-50 rounded-lg p-3">
          <div className="text-xs text-gray-500 mb-2">今日班次预览</div>
          <div className="grid grid-cols-3 gap-2">
            {routeGroup.schedules.slice(0, 3).map((schedule, index) => (
              <div key={index} className="text-center">
                <div className="text-sm font-semibold text-blue-600">{schedule.departure_time}</div>
                <div className="text-xs text-gray-500">
                  {calculateDuration(schedule.departure_time, schedule.arrival_time)}
                </div>
              </div>
            ))}
          </div>
          {routeGroup.schedules.length > 3 && (
            <div className="text-center mt-2 text-xs text-gray-500">
              还有 {routeGroup.schedules.length - 3} 个班次...
            </div>
          )}
        </div>
      )}

      {/* 详细时刻表 */}
      {isExpanded && (
        <div className="mt-4">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50">
                  <th className="text-left p-2 font-medium text-gray-700">出发</th>
                  <th className="text-left p-2 font-medium text-gray-700">到达</th>
                  <th className="text-left p-2 font-medium text-gray-700">时长</th>
                  <th className="text-left p-2 font-medium text-gray-700">船型</th>
                  <th className="text-left p-2 font-medium text-gray-700">公司</th>
                  <th className="text-left p-2 font-medium text-gray-700">票价</th>
                  <th className="text-left p-2 font-medium text-gray-700">载运</th>
                </tr>
              </thead>
              <tbody>
                {routeGroup.schedules.map((schedule, index) => (
                  <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                    <td className="p-2">
                      <div className="font-semibold text-blue-600">{schedule.departure_time}</div>
                    </td>
                    <td className="p-2">
                      <div className="font-semibold text-blue-600">{schedule.arrival_time}</div>
                    </td>
                    <td className="p-2">
                      <div className="text-gray-700">
                        {calculateDuration(schedule.departure_time, schedule.arrival_time)}
                      </div>
                    </td>
                    <td className="p-2">
                      <div className="flex items-center space-x-1">
                        <span>{getShipIcon(schedule.ship_type)}</span>
                        <span className="text-xs text-gray-600">{schedule.ship_type}</span>
                      </div>
                    </td>
                    <td className="p-2">
                      <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${getCompanyColor(schedule.company)}`}>
                        {schedule.company}
                      </span>
                    </td>
                    <td className="p-2">
                      <div className="text-green-600 font-medium">{schedule.adult_fare}</div>
                      <div className="text-xs text-gray-500">{schedule.child_fare}</div>
                    </td>
                    <td className="p-2">
                      <div className="flex space-x-1">
                        <div className={`flex items-center space-x-1 text-xs px-1 py-0.5 rounded ${
                          schedule.allows_vehicles ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                        }`}>
                          {schedule.allows_vehicles ? (
                            <TruckIcon className="h-3 w-3" />
                          ) : (
                            <XMarkIcon className="h-3 w-3" />
                          )}
                        </div>
                        <div className={`flex items-center space-x-1 text-xs px-1 py-0.5 rounded ${
                          schedule.allows_bicycles ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                        }`}>
                          <span>{schedule.allows_bicycles ? '🚲' : '🚫'}</span>
                        </div>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          {/* 运营信息 */}
          <div className={`mt-4 p-3 rounded-lg ${isLimitedPeriod ? 'bg-orange-50' : 'bg-blue-50'}`}>
            <div className="text-sm">
              <div className={`font-medium mb-1 ${isLimitedPeriod ? 'text-orange-900' : 'text-blue-900'}`}>运营信息</div>
              <div className={isLimitedPeriod ? 'text-orange-800' : 'text-blue-800'}>
                运营日期: {routeGroup.schedules[0]?.operating_days || '每日'}
              </div>
              {isLimitedPeriod && (
                <div className="mt-2">
                  <div className="font-medium text-orange-900 mb-1">期间限定详情</div>
                  <div className="text-xs text-orange-700 space-y-1">
                    <div>• 运营期间：2025年4月18日-5月25日</div>
                    <div>• 运营期间：2025年8月1日-8月31日</div>
                    <div>• 运营期间：2025年10月3日-11月9日</div>
                    <div>• 仅限金、土、日、祝日运航</div>
                    <div>• 无需预约，先到先得</div>
                  </div>
                </div>
              )}
              {routeGroup.schedules.some(s => s.notes) && (
                <div className="mt-2">
                  <div className={`font-medium mb-1 ${isLimitedPeriod ? 'text-orange-900' : 'text-blue-900'}`}>注意事项</div>
                  {Array.from(new Set(routeGroup.schedules.filter(s => s.notes).map(s => s.notes))).map((note, index) => (
                    <div key={index} className={`text-xs ${isLimitedPeriod ? 'text-orange-700' : 'text-blue-700'}`}>• {note}</div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RouteGroup;
