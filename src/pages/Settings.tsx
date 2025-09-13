import React, { useState } from 'react';
import { ArrowLeft, User, Bell, Shield, Palette, Database, Download, Upload, Save } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const Settings: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('profile');
  const [settings, setSettings] = useState({
    profile: {
      name: '张三',
      email: 'zhangsan@example.com',
      role: '高级开发工程师',
      avatar: '',
      bio: '专注于前端开发和代码质量提升'
    },
    notifications: {
      emailNotifications: true,
      pushNotifications: false,
      weeklyReport: true,
      codeAnalysisAlerts: true,
      learningReminders: false
    },
    security: {
      twoFactorAuth: false,
      sessionTimeout: 30,
      passwordLastChanged: '2024-01-01',
      loginHistory: true
    },
    appearance: {
      theme: 'light',
      language: 'zh-CN',
      fontSize: 'medium',
      codeTheme: 'dark'
    },
    data: {
      autoBackup: true,
      backupFrequency: 'weekly',
      dataRetention: 365,
      exportFormat: 'json'
    }
  });

  const [notifications, setNotifications] = useState<string[]>([]);

  const addNotification = (message: string) => {
    setNotifications(prev => [...prev, message]);
    setTimeout(() => {
      setNotifications(prev => prev.slice(1));
    }, 3000);
  };

  const handleSave = () => {
    addNotification('设置已保存');
  };

  const handleExportData = () => {
    addNotification('数据导出已开始，请稍候...');
  };

  const handleImportData = () => {
    addNotification('请选择要导入的数据文件');
  };

  const updateSetting = (category: string, key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category as keyof typeof prev],
        [key]: value
      }
    }));
  };

  const tabs = [
    { id: 'profile', name: '个人资料', icon: User },
    { id: 'notifications', name: '通知设置', icon: Bell },
    { id: 'security', name: '安全设置', icon: Shield },
    { id: 'appearance', name: '外观设置', icon: Palette },
    { id: 'data', name: '数据管理', icon: Database }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-100">
      {/* 通知区域 */}
      {notifications.length > 0 && (
        <div className="fixed top-4 right-4 z-50 space-y-2">
          {notifications.map((notification, index) => (
            <div
              key={index}
              className="bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg flex items-center space-x-2 animate-pulse"
            >
              <Save className="w-4 h-4" />
              <span>{notification}</span>
            </div>
          ))}
        </div>
      )}

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* 头部导航 */}
        <div className="flex items-center mb-8">
          <button
            onClick={() => navigate('/home')}
            className="flex items-center text-gray-600 hover:text-gray-800 transition-colors mr-4"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            返回主页
          </button>
          <div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">系统设置</h1>
            <p className="text-xl text-gray-600">个性化您的登攀引擎体验</p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          <div className="flex">
            {/* 侧边栏 */}
            <div className="w-64 bg-gray-50 border-r border-gray-200">
              <nav className="p-4 space-y-2">
                {tabs.map((tab) => {
                  const Icon = tab.icon;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`w-full flex items-center px-4 py-3 text-left rounded-lg transition-colors ${
                        activeTab === tab.id
                          ? 'bg-blue-100 text-blue-700 border border-blue-200'
                          : 'text-gray-600 hover:bg-gray-100'
                      }`}
                    >
                      <Icon className="w-5 h-5 mr-3" />
                      {tab.name}
                    </button>
                  );
                })}
              </nav>
            </div>

            {/* 主内容区 */}
            <div className="flex-1 p-8">
              {activeTab === 'profile' && (
                <div className="space-y-6">
                  <h2 className="text-2xl font-bold text-gray-900">个人资料</h2>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">姓名</label>
                      <input
                        type="text"
                        value={settings.profile.name}
                        onChange={(e) => updateSetting('profile', 'name', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">邮箱</label>
                      <input
                        type="email"
                        value={settings.profile.email}
                        onChange={(e) => updateSetting('profile', 'email', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">职位</label>
                      <input
                        type="text"
                        value={settings.profile.role}
                        onChange={(e) => updateSetting('profile', 'role', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">个人简介</label>
                    <textarea
                      value={settings.profile.bio}
                      onChange={(e) => updateSetting('profile', 'bio', e.target.value)}
                      rows={4}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>
              )}

              {activeTab === 'notifications' && (
                <div className="space-y-6">
                  <h2 className="text-2xl font-bold text-gray-900">通知设置</h2>
                  
                  <div className="space-y-4">
                    {Object.entries(settings.notifications).map(([key, value]) => (
                      <div key={key} className="flex items-center justify-between py-3 border-b border-gray-200">
                        <div>
                          <h3 className="font-medium text-gray-900">
                            {key === 'emailNotifications' && '邮件通知'}
                            {key === 'pushNotifications' && '推送通知'}
                            {key === 'weeklyReport' && '周报提醒'}
                            {key === 'codeAnalysisAlerts' && '代码分析警告'}
                            {key === 'learningReminders' && '学习提醒'}
                          </h3>
                          <p className="text-sm text-gray-500">
                            {key === 'emailNotifications' && '接收重要更新的邮件通知'}
                            {key === 'pushNotifications' && '接收浏览器推送通知'}
                            {key === 'weeklyReport' && '每周接收学习进度报告'}
                            {key === 'codeAnalysisAlerts' && '代码质量问题及时提醒'}
                            {key === 'learningReminders' && '学习计划提醒'}
                          </p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={value as boolean}
                            onChange={(e) => updateSetting('notifications', key, e.target.checked)}
                            className="sr-only peer"
                          />
                          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                        </label>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'security' && (
                <div className="space-y-6">
                  <h2 className="text-2xl font-bold text-gray-900">安全设置</h2>
                  
                  <div className="space-y-6">
                    <div className="flex items-center justify-between py-3 border-b border-gray-200">
                      <div>
                        <h3 className="font-medium text-gray-900">双因素认证</h3>
                        <p className="text-sm text-gray-500">为您的账户添加额外的安全保护</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={settings.security.twoFactorAuth}
                          onChange={(e) => updateSetting('security', 'twoFactorAuth', e.target.checked)}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                      </label>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">会话超时时间 (分钟)</label>
                      <select
                        value={settings.security.sessionTimeout}
                        onChange={(e) => updateSetting('security', 'sessionTimeout', parseInt(e.target.value))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value={15}>15分钟</option>
                        <option value={30}>30分钟</option>
                        <option value={60}>1小时</option>
                        <option value={120}>2小时</option>
                      </select>
                    </div>
                    
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h3 className="font-medium text-gray-900 mb-2">密码安全</h3>
                      <p className="text-sm text-gray-600 mb-3">上次修改密码: {settings.security.passwordLastChanged}</p>
                      <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                        修改密码
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'appearance' && (
                <div className="space-y-6">
                  <h2 className="text-2xl font-bold text-gray-900">外观设置</h2>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">主题</label>
                      <select
                        value={settings.appearance.theme}
                        onChange={(e) => updateSetting('appearance', 'theme', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="light">浅色主题</option>
                        <option value="dark">深色主题</option>
                        <option value="auto">跟随系统</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">语言</label>
                      <select
                        value={settings.appearance.language}
                        onChange={(e) => updateSetting('appearance', 'language', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="zh-CN">简体中文</option>
                        <option value="en-US">English</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">字体大小</label>
                      <select
                        value={settings.appearance.fontSize}
                        onChange={(e) => updateSetting('appearance', 'fontSize', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="small">小</option>
                        <option value="medium">中</option>
                        <option value="large">大</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">代码主题</label>
                      <select
                        value={settings.appearance.codeTheme}
                        onChange={(e) => updateSetting('appearance', 'codeTheme', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="dark">深色</option>
                        <option value="light">浅色</option>
                        <option value="monokai">Monokai</option>
                        <option value="github">GitHub</option>
                      </select>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'data' && (
                <div className="space-y-6">
                  <h2 className="text-2xl font-bold text-gray-900">数据管理</h2>
                  
                  <div className="space-y-6">
                    <div className="flex items-center justify-between py-3 border-b border-gray-200">
                      <div>
                        <h3 className="font-medium text-gray-900">自动备份</h3>
                        <p className="text-sm text-gray-500">定期自动备份您的数据</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={settings.data.autoBackup}
                          onChange={(e) => updateSetting('data', 'autoBackup', e.target.checked)}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                      </label>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">备份频率</label>
                        <select
                          value={settings.data.backupFrequency}
                          onChange={(e) => updateSetting('data', 'backupFrequency', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        >
                          <option value="daily">每日</option>
                          <option value="weekly">每周</option>
                          <option value="monthly">每月</option>
                        </select>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">数据保留期 (天)</label>
                        <input
                          type="number"
                          value={settings.data.dataRetention}
                          onChange={(e) => updateSetting('data', 'dataRetention', parseInt(e.target.value))}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                    </div>
                    
                    <div className="bg-gray-50 p-6 rounded-lg">
                      <h3 className="font-medium text-gray-900 mb-4">数据导入/导出</h3>
                      <div className="flex space-x-4">
                        <button
                          onClick={handleExportData}
                          className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                        >
                          <Download className="w-4 h-4 mr-2" />
                          导出数据
                        </button>
                        <button
                          onClick={handleImportData}
                          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                        >
                          <Upload className="w-4 h-4 mr-2" />
                          导入数据
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* 保存按钮 */}
              <div className="mt-8 pt-6 border-t border-gray-200">
                <button
                  onClick={handleSave}
                  className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors flex items-center"
                >
                  <Save className="w-5 h-5 mr-2" />
                  保存设置
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;