'use client';

import React, { useState, useRef, useEffect } from 'react';
import { ChevronDownIcon, CheckIcon } from '@heroicons/react/24/outline';
import { ISLANDS, ISLAND_GROUPS, IslandOption } from '@/lib/islands';

interface IslandSelectProps {
  value: string;
  onChange: (value: string) => void;
  placeholder: string;
  label: string;
  icon: string;
}

const IslandSelect: React.FC<IslandSelectProps> = ({
  value,
  onChange,
  placeholder,
  label,
  icon
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const dropdownRef = useRef<HTMLDivElement>(null);

  // 关闭下拉框
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setSearchTerm('');
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // 过滤岛屿选项
  const filteredIslands = ISLANDS.filter(island =>
    island.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
    island.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // 获取当前选中的岛屿
  const selectedIsland = ISLANDS.find(island => island.value === value);

  // 处理选择
  const handleSelect = (island: IslandOption) => {
    onChange(island.value);
    setIsOpen(false);
    setSearchTerm('');
  };

  // 按组分类显示
  const renderIslandsByGroup = () => {
    const groups = Object.entries(ISLAND_GROUPS);
    
    return groups.map(([groupKey, group]) => {
      const groupIslands = filteredIslands.filter(island => 
        group.islands.includes(island.value)
      );
      
      if (groupIslands.length === 0) return null;
      
      return (
        <div key={groupKey} className="py-2">
          <div className="px-3 py-1 text-xs font-semibold text-gray-500 uppercase tracking-wide">
            {group.title}
          </div>
          {groupIslands.map((island) => (
            <button
              key={island.value}
              onClick={() => handleSelect(island)}
              className={`w-full text-left px-3 py-2 hover:bg-blue-50 flex items-center space-x-3 ${
                value === island.value ? 'bg-blue-100 text-blue-900' : 'text-gray-900'
              }`}
            >
              <span className="text-lg">{island.icon}</span>
              <div className="flex-1">
                <div className="font-medium">{island.label}</div>
                <div className="text-sm text-gray-500">{island.description}</div>
              </div>
              {value === island.value && (
                <CheckIcon className="h-4 w-4 text-blue-600" />
              )}
            </button>
          ))}
        </div>
      );
    });
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <label className="block text-lg font-medium text-gray-700 mb-3">
        {icon} {label}
      </label>
      
      {/* 选择框 */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className={`input-field text-lg py-3 flex items-center justify-between ${
          isOpen ? 'ring-2 ring-blue-500 border-transparent' : ''
        }`}
      >
        <div className="flex items-center space-x-3">
          {selectedIsland ? (
            <>
              <span className="text-xl">{selectedIsland.icon}</span>
              <div className="text-left">
                <div className="font-medium text-gray-900">{selectedIsland.label}</div>
                <div className="text-sm text-gray-500">{selectedIsland.description}</div>
              </div>
            </>
          ) : (
            <span className="text-gray-500">{placeholder}</span>
          )}
        </div>
        <ChevronDownIcon 
          className={`h-5 w-5 text-gray-400 transition-transform duration-200 ${
            isOpen ? 'transform rotate-180' : ''
          }`} 
        />
      </button>

      {/* 下拉菜单 */}
      {isOpen && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-80 overflow-y-auto">
          {/* 搜索框 */}
          <div className="p-3 border-b border-gray-200">
            <input
              type="text"
              placeholder="搜索岛屿..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              onClick={(e) => e.stopPropagation()}
            />
          </div>

          {/* 岛屿选项 */}
          <div className="py-1">
            {filteredIslands.length > 0 ? (
              renderIslandsByGroup()
            ) : (
              <div className="px-3 py-4 text-center text-gray-500">
                未找到匹配的岛屿
              </div>
            )}
          </div>
        </div>
      )}
      
      <p className="mt-1 text-sm text-gray-500">
        选择{label.includes('出发') ? '出发' : '目的地'}岛屿或港口
      </p>
    </div>
  );
};

export default IslandSelect;
