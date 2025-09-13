import React, { useState, useEffect } from 'react';
import { Play, Server, Database, Zap, CheckCircle, XCircle, Clock } from 'lucide-react';

interface ServiceStatus {
  name: string;
  url: string;
  status: 'checking' | 'online' | 'offline';
  icon: React.ReactNode;
}

const Launch: React.FC = () => {
  const [services, setServices] = useState<ServiceStatus[]>([
    {
      name: '后端 API',
      url: 'http://localhost:8000/health',
      status: 'checking',
      icon: <Server className="w-5 h-5" />
    },
    {
      name: '前端应用',
      url: 'http://localhost:5173',
      status: 'checking',
      icon: <Zap className="w-5 h-5" />
    },
    {
      name: 'MCP 服务',
      url: 'http://localhost:8000/api/v1/mcp/capabilities',
      status: 'checking',
      icon: <Database className="w-5 h-5" />
    }
  ]);

  const checkServiceStatus = async (service: ServiceStatus): Promise<'online' | 'offline'> => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      const response = await fetch(service.url, {
        method: 'GET',
        mode: 'cors',
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      return response.ok ? 'online' : 'offline';
    } catch (error) {
      return 'offline';
    }
  };

  const checkAllServices = async () => {
    const updatedServices = await Promise.all(
      services.map(async (service) => {
        const status = await checkServiceStatus(service);
        return { ...service, status };
      })
    );
    setServices(updatedServices);
  };

  useEffect(() => {
    checkAllServices();
    const interval = setInterval(checkAllServices, 10000); // 每10秒检查一次
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'offline':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'checking':
      default:
        return <Clock className="w-4 h-4 text-yellow-500 animate-spin" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
        return 'border-green-200 bg-green-50';
      case 'offline':
        return 'border-red-200 bg-red-50';
      case 'checking':
      default:
        return 'border-yellow-200 bg-yellow-50';
    }
  };

  const allServicesOnline = services.every(service => service.status === 'online');

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-4xl mx-auto">
        {/* 头部 */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-6">
            <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-4 rounded-full">
              <Play className="w-12 h-12 text-white" />
            </div>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            登攀引擎启动中心
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            智能 AI 驱动的编程技能提升平台
          </p>
        </div>

        {/* 服务状态卡片 */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          {services.map((service, index) => (
            <div
              key={index}
              className={`p-6 rounded-lg border-2 transition-all duration-300 ${
                getStatusColor(service.status)
              }`}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  {service.icon}
                  <h3 className="font-semibold text-gray-900">{service.name}</h3>
                </div>
                {getStatusIcon(service.status)}
              </div>
              <p className="text-sm text-gray-600 mb-2">{service.url}</p>
              <div className="flex items-center space-x-2">
                <span className="text-sm font-medium">
                  状态: 
                </span>
                <span className={`text-sm font-semibold ${
                  service.status === 'online' ? 'text-green-600' :
                  service.status === 'offline' ? 'text-red-600' : 'text-yellow-600'
                }`}>
                  {service.status === 'online' ? '在线' :
                   service.status === 'offline' ? '离线' : '检查中'}
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* 系统状态总览 */}
        <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900">系统状态</h2>
            <button
              onClick={checkAllServices}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              刷新状态
            </button>
          </div>
          
          <div className={`p-4 rounded-lg border-2 ${
            allServicesOnline ? 'border-green-200 bg-green-50' : 'border-yellow-200 bg-yellow-50'
          }`}>
            <div className="flex items-center space-x-3">
              {allServicesOnline ? (
                <CheckCircle className="w-6 h-6 text-green-500" />
              ) : (
                <Clock className="w-6 h-6 text-yellow-500" />
              )}
              <div>
                <h3 className="font-semibold text-gray-900">
                  {allServicesOnline ? '系统就绪' : '系统启动中'}
                </h3>
                <p className="text-sm text-gray-600">
                  {allServicesOnline 
                    ? '所有服务正常运行，可以开始使用登攀引擎'
                    : '正在检查服务状态，请稍候...'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* 快速操作 */}
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">快速操作</h2>
          <div className="grid md:grid-cols-2 gap-4">
            <a
              href="http://localhost:5173/home"
              target="_blank"
              rel="noopener noreferrer"
              className="p-4 border-2 border-blue-200 rounded-lg hover:border-blue-400 hover:bg-blue-50 transition-all duration-300"
            >
              <div className="flex items-center space-x-3">
                <Zap className="w-6 h-6 text-blue-600" />
                <div>
                  <h3 className="font-semibold text-gray-900">打开前端应用</h3>
                  <p className="text-sm text-gray-600">访问登攀引擎用户界面</p>
                </div>
              </div>
            </a>
            
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="p-4 border-2 border-green-200 rounded-lg hover:border-green-400 hover:bg-green-50 transition-all duration-300"
            >
              <div className="flex items-center space-x-3">
                <Database className="w-6 h-6 text-green-600" />
                <div>
                  <h3 className="font-semibold text-gray-900">API 文档</h3>
                  <p className="text-sm text-gray-600">查看后端 API 接口文档</p>
                </div>
              </div>
            </a>
          </div>
        </div>

        {/* 版本信息 */}
        <div className="text-center mt-8 text-gray-500">
          <p>登攀引擎 v1.0.0 | 构建时间: {new Date().toLocaleDateString()}</p>
        </div>
      </div>
    </div>
  );
};

export default Launch;