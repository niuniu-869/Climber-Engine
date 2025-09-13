import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, Users, FileText, BookOpen, Settings, CheckCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import TechnicalDebtBalanceSheet from '../components/TechnicalDebtBalanceSheet';
import LearningCenter from '../components/LearningCenter';
import { technicalDebtService } from '../services/technicalDebtService';
import { learningService } from '../services/learningService';

const Home: React.FC = () => {
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState<string[]>([]);
  const [dashboardStats, setDashboardStats] = useState({
    technicalDebts: 0,
    improvements: 0,
    teamMembers: 5, // 静态数据
    codeRecords: 0
  });
  const [loading, setLoading] = useState(true);
  
  // 模拟用户ID，实际应用中应该从认证系统获取
  const userId = 1;

  const addNotification = (message: string) => {
    setNotifications(prev => [...prev, message]);
    setTimeout(() => {
      setNotifications(prev => prev.slice(1));
    }, 3000);
  };

  const handleViewReport = () => {
    addNotification('正在跳转到技术债务报告...');
    setTimeout(() => {
      navigate('/tech-debt-report');
    }, 500);
  };

  const handleNavigateToLearningCenter = () => {
    addNotification('正在进入学习中心...');
    setTimeout(() => {
      navigate('/learning-center');
    }, 500);
  };

  const handleAnalyzeCode = () => {
    addNotification('正在启动代码质量分析...');
    setTimeout(() => {
      navigate('/code-analysis');
    }, 500);
  };

  const handleRecordCode = () => {
    addNotification('正在打开代码记录界面...');
    setTimeout(() => {
      navigate('/code-record');
    }, 500);
  };

  const handleSettings = () => {
    addNotification('正在打开系统设置...');
    setTimeout(() => {
      navigate('/settings');
    }, 500);
  };

  const handleStartLearning = (content: any) => {
    if (content) {
      addNotification(`开始学习: ${content.title}`);
      // 这里可以导航到具体的学习页面
    } else {
      handleNavigateToLearningCenter();
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // 并行加载仪表板数据
      const [debtSummary, userStats] = await Promise.all([
        technicalDebtService.getUserDebtSummary(userId).catch(() => ({ total_debts: 0, open_debts: 0 })),
        learningService.getUserLearningStatistics({ user_id: userId }).catch(() => ({ total_attempts: 0 }))
      ]);

      setDashboardStats({
        technicalDebts: debtSummary.open_debts || 0,
        improvements: Math.max(0, (debtSummary.total_debts || 0) - (debtSummary.open_debts || 0)),
        teamMembers: 5,
        codeRecords: userStats.total_attempts || 0
      });
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      addNotification('加载仪表板数据失败');
    } finally {
      setLoading(false);
    }
  };
  return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        {/* 通知区域 */}
        {notifications.length > 0 && (
          <div className="fixed top-4 right-4 z-50 space-y-2">
            {notifications.map((notification, index) => (
              <div
                key={index}
                className="bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg flex items-center space-x-2 animate-pulse"
              >
                <CheckCircle className="w-4 h-4" />
                <span>{notification}</span>
              </div>
            ))}
          </div>
        )}
        
        <div className="max-w-7xl mx-auto px-4 py-8">
          {/* 头部 */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">登攀引擎</h1>
            <p className="text-xl text-gray-600">技术债务管理与开发者成长平台</p>
          </div>

        {/* 快速统计 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center">
              <BarChart3 className="w-8 h-8 text-blue-600 mr-3" />
              <div>
                <h3 className="text-lg font-semibold text-gray-900">技术债务</h3>
                <p className="text-2xl font-bold text-blue-600">
                  {loading ? '...' : dashboardStats.technicalDebts}
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center">
              <TrendingUp className="w-8 h-8 text-green-600 mr-3" />
              <div>
                <h3 className="text-lg font-semibold text-gray-900">改进建议</h3>
                <p className="text-2xl font-bold text-green-600">
                  {loading ? '...' : dashboardStats.improvements}
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center">
              <Users className="w-8 h-8 text-purple-600 mr-3" />
              <div>
                <h3 className="text-lg font-semibold text-gray-900">团队成员</h3>
                <p className="text-2xl font-bold text-purple-600">{dashboardStats.teamMembers}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center">
              <FileText className="w-8 h-8 text-orange-600 mr-3" />
              <div>
                <h3 className="text-lg font-semibold text-gray-900">学习记录</h3>
                <p className="text-2xl font-bold text-orange-600">
                  {loading ? '...' : dashboardStats.codeRecords}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* 主要功能区域 */}
        <div className="space-y-8 mb-8">
          {/* 技术资产负债表 */}
          <TechnicalDebtBalanceSheet 
            userId={userId} 
            onViewReport={handleViewReport}
          />

          {/* AI学习中心 */}
          <LearningCenter 
            userId={userId} 
            onStartLearning={handleStartLearning}
          />
        </div>

        {/* 快速操作 */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">快速操作</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button 
              onClick={handleAnalyzeCode}
              className="flex items-center justify-center p-4 border-2 border-blue-200 rounded-lg hover:border-blue-400 hover:bg-blue-50 transition-all duration-300"
            >
              <BarChart3 className="w-6 h-6 text-blue-600 mr-3" />
              <span className="font-medium text-gray-900">分析代码质量</span>
            </button>
            
            <button 
              onClick={handleRecordCode}
              className="flex items-center justify-center p-4 border-2 border-green-200 rounded-lg hover:border-green-400 hover:bg-green-50 transition-all duration-300"
            >
              <FileText className="w-6 h-6 text-green-600 mr-3" />
              <span className="font-medium text-gray-900">记录新代码</span>
            </button>
            
            <button 
              onClick={handleSettings}
              className="flex items-center justify-center p-4 border-2 border-purple-200 rounded-lg hover:border-purple-400 hover:bg-purple-50 transition-all duration-300"
            >
              <Settings className="w-6 h-6 text-purple-600 mr-3" />
              <span className="font-medium text-gray-900">系统设置</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;