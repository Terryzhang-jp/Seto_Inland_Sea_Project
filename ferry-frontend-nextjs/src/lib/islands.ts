// 瀬户内海岛屿和港口数据
export interface IslandOption {
  value: string;
  label: string;
  icon: string;
  description: string;
}

export const ISLANDS: IslandOption[] = [
  // 主要岛屿
  { value: '高松', label: '高松', icon: '🏙️', description: '四国门户，主要交通枢纽' },
  { value: '宇野', label: '宇野', icon: '🚢', description: '本州重要港口' },
  { value: '神戸', label: '神戸', icon: '🌆', description: '关西主要港口' },
  { value: '新岡山港', label: '新岡山港', icon: '⚓', description: '岡山主要港口' },
  
  // 艺术岛屿
  { value: '直島', label: '直島', icon: '🎨', description: '现代艺术圣地' },
  { value: '豊島', label: '豊島', icon: '🏛️', description: '豊島美术馆所在地' },
  { value: '犬島', label: '犬島', icon: '🏭', description: '犬島精炼所美术馆' },
  
  // 其他重要岛屿
  { value: '小豆島', label: '小豆島', icon: '🫒', description: '橄榄之岛' },
  { value: '女木島', label: '女木島', icon: '👹', description: '鬼岛传说' },
  { value: '男木島', label: '男木島', icon: '🐱', description: '猫咪天堂' },
];

// 按类型分组的岛屿
export const ISLAND_GROUPS = {
  mainland: {
    title: '本州港口',
    islands: ['高松', '宇野', '神戸', '新岡山港']
  },
  art: {
    title: '艺术岛屿',
    islands: ['直島', '豊島', '犬島']
  },
  other: {
    title: '其他岛屿',
    islands: ['小豆島', '女木島', '男木島']
  }
};

// 获取岛屿图标
export const getIslandIcon = (islandName: string): string => {
  const island = ISLANDS.find(i => i.value === islandName);
  return island?.icon || '🏝️';
};

// 获取岛屿描述
export const getIslandDescription = (islandName: string): string => {
  const island = ISLANDS.find(i => i.value === islandName);
  return island?.description || '';
};
