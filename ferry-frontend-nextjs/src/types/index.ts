// API响应类型
export interface APIResponse<T> {
  success: boolean;
  data: T;
  message: string;
  total?: number;
  page?: number;
  limit?: number;
}

// 航线类型
export interface FerryRoute {
  departure_port: string;
  arrival_port: string;
  departure_time: string;
  arrival_time: string;
  company: string;
  ship_type: string;
  allows_vehicles: boolean;
  allows_bicycles: boolean;
  adult_fare: string;
  child_fare: string;
  operating_days: string;
  notes?: string;
}

// 港口类型
export interface Port {
  name: string;
  island: string;
  address: string;
  features: string;
  connections: string;
}

// 公司类型
export interface Company {
  name: string;
  phone: string;
  website: string;
  main_routes: string;
  notes: string;
}

// 热门路线类型
export interface PopularRoute {
  departure: string;
  arrival: string;
  description: string;
}

// 搜索参数类型
export interface RouteSearchParams {
  departure?: string;
  arrival?: string;
  company?: string;
  departure_time_start?: string;
  departure_time_end?: string;
  allows_vehicles?: boolean;
  allows_bicycles?: boolean;
  page?: number;
  limit?: number;
}

// 岛屿交通相关类型
export interface BicycleRental {
  shop_name: string;
  location: string;
  bicycle_type: string;
  price_1day_yen?: number;
  price_4hours_yen?: number;
  price_overnight_yen?: number;
  operating_hours: string;
  contact: string;
  notes?: string;
  equipment?: string;
  insurance?: string;
}

export interface BusSchedule {
  bus_type: string;
  route: string;
  departure_stop: string;
  arrival_stop: string;
  departure_time?: string;
  arrival_time?: string;
  fare_adult_yen?: number;
  fare_child_yen?: number;
  operator: string;
  notes?: string;
  frequency?: string;
}

export interface OtherTransport {
  transport_type: string;
  service_name: string;
  location: string;
  price_yen?: number;
  operating_hours: string;
  contact: string;
  notes?: string;
  capacity?: string;
  requirements?: string;
}

export interface IslandTransport {
  island_name: string;
  island_name_en: string;
  bicycle_rentals: BicycleRental[];
  bus_schedules: BusSchedule[];
  other_transports: OtherTransport[];
  summary?: string;
}

export interface IslandTransportSummary {
  island_name: string;
  island_name_en: string;
  has_bus: boolean;
  has_bicycle_rental: boolean;
  bicycle_rental_count: number;
  min_bicycle_price?: number;
  transport_types: string[];
  special_notes?: string;
}
