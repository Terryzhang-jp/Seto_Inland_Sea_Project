import type { Metadata } from "next";
import Navigation from "../components/Navigation";
import "./globals.css";

export const metadata: Metadata = {
  title: "瀬户内海船班查询",
  description: "查找瀬户内海各岛屿间的船班信息，规划您的跳岛之旅",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body className="antialiased">
        <Navigation />
        <main>{children}</main>

        {/* 页脚 */}
        <footer className="bg-white border-t border-gray-200 mt-12">
          <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
            <div className="text-center text-gray-500 text-sm">
              <p>瀬户内海船班查询系统 - 让岛屿跳岛旅行变得简单</p>
              <p className="mt-1">数据来源：各船运公司官方时刻表</p>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
