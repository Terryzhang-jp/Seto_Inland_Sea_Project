import { FerryRoute } from '../types';

export const formatTime = (time: string): string => {
  return time;
};

export const formatPrice = (price: string): string => {
  return price;
};

// 按路线分组ferry数据
export interface RouteGroup {
  routeKey: string;
  departure: string;
  arrival: string;
  schedules: FerryRoute[];
  companies: string[];
  minPrice: number;
  totalSchedules: number;
}

export const groupRoutesByPath = (routes: FerryRoute[]): RouteGroup[] => {
  const groupMap = new Map<string, RouteGroup>();

  routes.forEach(route => {
    const routeKey = `${route.departure_port}-${route.arrival_port}`;
    
    if (!groupMap.has(routeKey)) {
      groupMap.set(routeKey, {
        routeKey,
        departure: route.departure_port,
        arrival: route.arrival_port,
        schedules: [],
        companies: [],
        minPrice: Infinity,
        totalSchedules: 0
      });
    }

    const group = groupMap.get(routeKey)!;
    group.schedules.push(route);
    
    // 添加公司（去重）
    if (!group.companies.includes(route.company)) {
      group.companies.push(route.company);
    }
    
    // 计算最低价格
    const adultFare = parseInt(route.adult_fare.replace(/[^\d]/g, ''));
    if (adultFare < group.minPrice) {
      group.minPrice = adultFare;
    }
    
    group.totalSchedules++;
  });

  // 对每个组内的班次按时间排序
  groupMap.forEach(group => {
    group.schedules.sort((a, b) => {
      const timeA = a.departure_time.replace(':', '');
      const timeB = b.departure_time.replace(':', '');
      return timeA.localeCompare(timeB);
    });
  });

  return Array.from(groupMap.values());
};

// 计算航行时间
export const calculateDuration = (departure: string, arrival: string): string => {
  try {
    const [depHour, depMin] = departure.split(':').map(Number);
    const [arrHour, arrMin] = arrival.split(':').map(Number);
    
    let depMinutes = depHour * 60 + depMin;
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
