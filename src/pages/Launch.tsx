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
        <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
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

        {/* Climber-Recorder 配置与简介 */}
        <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Climber-Recorder 技术栈记录器</h2>
          
          {/* Climber-Recorder 简介 */}
          <div className="mb-8 p-6 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg border border-green-200">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">关于 Climber-Recorder</h3>
            <p className="text-gray-700 mb-4">
              Climber-Recorder 是一个专门的 MCP 工具服务器，用于记录 AI Agent 工作过程中使用的技术栈。它可以帮助您：
            </p>
            <ul className="list-disc list-inside text-gray-700 space-y-2 mb-4">
              <li>📝 自动记录每次工作会话中使用的技术栈</li>
              <li>📊 跟踪不同任务类型和难度级别的技术使用情况</li>
              <li>🎯 分析技能发展轨迹和技术栈演进</li>
              <li>📈 为学习路径规划提供数据支持</li>
            </ul>
            <div className="flex items-center space-x-2 text-sm text-green-700">
              <Server className="w-4 h-4" />
              <span>独立 MCP 服务器，专注技术栈记录</span>
            </div>
          </div>

          {/* Climber-Recorder 配置 */}
          <div className="space-y-6">
            <h3 className="text-xl font-semibold text-gray-900">一键配置 Climber-Recorder</h3>
            
            <div className="bg-gray-50 rounded-lg p-6">
              <h4 className="font-semibold text-gray-900 mb-3">UV 配置文件 (推荐)</h4>
              <p className="text-sm text-gray-600 mb-4">
                将以下配置添加到您的 Claude Desktop 配置文件中：
              </p>
              <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto">
                <pre className="text-green-400 text-sm font-mono">
{`{
  "mcpServers": {
    "climber-recorder": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/mac/Desktop/AccountingLLM/Climber Engine/backend",
        "run",
        "python",
        "climber_recorder_server.py"
      ],
      "env": {}
    }
  }
}`}
                </pre>
              </div>
              <button
                onClick={() => {
                  const config = {
                    mcpServers: {
                      "climber-recorder": {
                        command: "uv",
                        args: [
                          "--directory",
                          "/Users/mac/Desktop/AccountingLLM/Climber Engine/backend",
                          "run",
                          "python",
                          "climber_recorder_server.py"
                        ],
                        env: {}
                      }
                    }
                  };
                  navigator.clipboard.writeText(JSON.stringify(config, null, 2));
                  alert('Climber-Recorder 配置已复制到剪贴板！');
                }}
                className="mt-4 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                📋 复制配置到剪贴板
              </button>
            </div>

            <div className="bg-blue-50 rounded-lg p-6">
              <h4 className="font-semibold text-gray-900 mb-3">配置步骤</h4>
              <ol className="list-decimal list-inside text-gray-700 space-y-2">
                <li>确保已安装 uv 包管理器 (启动脚本会自动安装)</li>
                <li>打开 Claude Desktop 应用</li>
                <li>进入设置 → MCP 服务器配置</li>
                <li>粘贴上方的 Climber-Recorder 配置 JSON</li>
                <li>重启 Claude Desktop 以加载配置</li>
                <li>在对话中输入 "记录技术栈" 开始使用</li>
              </ol>
            </div>

            <div className="bg-green-50 rounded-lg p-6 border border-green-200">
              <h4 className="font-semibold text-gray-900 mb-3">🎯 使用方法</h4>
              <p className="text-gray-700 mb-3">配置完成后，您可以在 Claude 对话中使用以下命令：</p>
              <div className="bg-white rounded p-3 border border-green-300">
                <code className="text-sm text-green-800">
                  请记录本次工作的技术栈：Python, FastAPI, SQLAlchemy, React, TypeScript
                </code>
              </div>
              <p className="text-sm text-gray-600 mt-2">
                Climber-Recorder 会自动记录技术栈、任务描述、工作类型和难度级别等信息。
              </p>
            </div>

            <div className="bg-yellow-50 rounded-lg p-6 border border-yellow-200">
              <h4 className="font-semibold text-gray-900 mb-3">⚠️ 注意事项</h4>
              <ul className="list-disc list-inside text-gray-700 space-y-1">
                <li>请确保路径 "/Users/mac/Desktop/AccountingLLM/Climber Engine/backend" 正确</li>
                <li>如果项目路径不同，请修改配置中的 "--directory" 参数</li>
                <li>Climber-Recorder 是独立运行的，不需要启动完整的登攀引擎服务</li>
                <li>记录的数据会保存在会话中，可通过 API 端点查询</li>
              </ul>
            </div>
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