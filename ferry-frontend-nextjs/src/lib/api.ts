import axios from 'axios';
import { APIResponse, FerryRoute, Port, Company, PopularRoute, RouteSearchParams, IslandTransport, IslandTransportSummary, BicycleRental } from '../types';

// API基础配置
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://setoinlandseaproject-production.up.railway.app';

// 调试信息
console.log('Environment:', process.env.NODE_ENV);
console.log('API_BASE_URL:', API_BASE_URL);
console.log('NEXT_PUBLIC_API_URL:', process.env.NEXT_PUBLIC_API_URL);

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.data);
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// API服务类
export class FerryAPI {
  // 搜索航线
  static async searchRoutes(params: RouteSearchParams): Promise<APIResponse<FerryRoute[]>> {
    const response = await api.get('/api/v1/routes', { params });
    return response.data;
  }

  // 获取热门路线
  static async getPopularRoutes(): Promise<APIResponse<PopularRoute[]>> {
    const response = await api.get('/api/v1/routes/popular');
    return response.data;
  }

  // 获取所有港口
  static async getPorts(search?: string): Promise<APIResponse<Port[]>> {
    const params = search ? { search } : {};
    const response = await api.get('/api/v1/ports', { params });
    return response.data;
  }

  // 获取特定港口
  static async getPortByName(name: string): Promise<APIResponse<Port>> {
    const response = await api.get(`/api/v1/ports/${encodeURIComponent(name)}`);
    return response.data;
  }

  // 获取所有公司
  static async getCompanies(search?: string): Promise<APIResponse<Company[]>> {
    const params = search ? { search } : {};
    const response = await api.get('/api/v1/companies', { params });
    return response.data;
  }

  // 获取特定公司
  static async getCompanyByName(name: string): Promise<APIResponse<Company>> {
    const response = await api.get(`/api/v1/companies/${encodeURIComponent(name)}`);
    return response.data;
  }

  // 健康检查
  static async healthCheck(): Promise<APIResponse<{ status: string; timestamp: string }>> {
    const response = await api.get('/health');
    return response.data;
  }



  // 岛屿交通相关API
  // 获取所有岛屿交通信息
  static async getAllIslands(): Promise<APIResponse<IslandTransport[]>> {
    const response = await api.get('/api/v1/islands');
    return response.data;
  }

  // 获取岛屿交通信息摘要
  static async getIslandsSummary(): Promise<APIResponse<IslandTransportSummary[]>> {
    const response = await api.get('/api/v1/islands/summary');
    return response.data;
  }

  // 获取特定岛屿交通信息
  static async getIslandByName(islandName: string): Promise<APIResponse<IslandTransport>> {
    const response = await api.get(`/api/v1/islands/${encodeURIComponent(islandName)}`);
    return response.data;
  }

  // 获取特定岛屿的自行车租赁信息
  static async getIslandBicycleRentals(islandName: string): Promise<APIResponse<{island_name: string, island_name_en: string, bicycle_rentals: BicycleRental[]}>> {
    const response = await api.get(`/api/v1/islands/${encodeURIComponent(islandName)}/rentals/bicycle`);
    return response.data;
  }

  // 搜索自行车租赁信息
  static async searchBicycleRentals(params?: {
    island_name?: string;
    max_price?: number;
    rental_type?: string;
  }): Promise<APIResponse<Array<{island_name: string, island_name_en: string, rental_info: BicycleRental}>>> {
    const response = await api.get('/api/v1/islands/rentals/bicycle', { params });
    return response.data;
  }

  // 获取特定岛屿的巴士时刻表
  static async getIslandBusSchedule(islandName: string): Promise<APIResponse<{ island_name: string; bus_schedules: unknown[] }>> {
    const response = await api.get(`/api/v1/islands/${encodeURIComponent(islandName)}/bus`);
    return response.data;
  }

  // 获取特定岛屿的其他交通方式
  static async getIslandOtherTransport(islandName: string): Promise<APIResponse<{ island_name: string; other_transport: unknown[] }>> {
    const response = await api.get(`/api/v1/islands/${encodeURIComponent(islandName)}/transport/other`);
    return response.data;
  }
}

export default api;
