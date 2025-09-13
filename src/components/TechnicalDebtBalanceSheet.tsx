import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, TrendingDown, AlertTriangle, CheckCircle, Clock, Target } from 'lucide-react';
import { technicalDebtService, TechnicalDebt, TechnicalDebtSummary } from '../services/technicalDebtService';
import { learningService } from '../services/learningService';

interface TechnicalDebtBalanceSheetProps {
  userId: number;
  onViewReport?: () => void;
}

interface TechAsset {
  id: number;
  project_name: string;
  technology_used: string;
  completion_status: string;
  ai_assistance_level: number;
  category: string;
  value_score: number;
}

interface TechNetAsset {
  id: number;
  technology_name: string;
  proficiency_level: string;
  proficiency_score: number;
  category: string;
  mastery_score: number;
}

interface TechDebt {
  id: number;
  technology_name: string;
  urgency_level: string;
  importance_score: number;
  target_proficiency_level: string;
  estimated_learning_hours: number;
}

const TechnicalDebtBalanceSheet: React.FC<TechnicalDebtBalanceSheetProps> = ({ 
  userId, 
  onViewReport 
}) => {
  const [debtSummary, setDebtSummary] = useState<TechnicalDebtSummary | null>(null);
  const [techAssets, setTechAssets] = useState<TechAsset[]>([]);
  const [techNetAssets, setTechNetAssets] = useState<TechNetAsset[]>([]);
  const [techDebts, setTechDebts] = useState<TechDebt[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadBalanceSheetData();
    
    // 监听学习进度更新事件
    const handleLearningProgressUpdate = () => {
      loadBalanceSheetData();
    };
    
    window.addEventListener('learningProgressUpdate', handleLearningProgressUpdate);
    
    return () => {
      window.removeEventListener('learningProgressUpdate', handleLearningProgressUpdate);
    };
  }, [userId]);



  const loadBalanceSheetData = async () => {
    try {
      setLoading(true);
      setError(null);

      // 并行加载数据
      const [summaryData, assetsData, netAssetsData, debtsData] = await Promise.all([
        technicalDebtService.getUserDebtSummary(userId).catch(err => {
          console.error('获取技术债务汇总失败:', err);
          return {
            summary: {
              total_debts: 0,
              open_debts: 0,
              resolved_debts: 0,
              resolution_rate: 0,
              total_impact_score: 0,
              total_estimated_effort_minutes: 0,
              total_estimated_effort_hours: 0
            },
            severity_distribution: [],
            type_distribution: []
          };
        }),
        learningService.getUserTechAssets({ 
          user_id: userId, 
          is_active: true 
        }).catch(err => {
          console.error('获取技术资产失败:', err);
          return [];
        }),
        learningService.getUserTechNetAssets({ 
          user_id: userId, 
          is_active: true 
        }).catch(err => {
          console.error('获取技术净资产失败:', err);
          return [];
        }),
        learningService.getUserTechDebts({ 
          user_id: userId, 
          is_active: true 
        }).catch(err => {
          console.error('获取技术负债失败:', err);
          return [];
        })
      ]);

      setDebtSummary(summaryData);
      setTechAssets(assetsData || []);
      setTechNetAssets(netAssetsData || []);
      setTechDebts(debtsData || []);
    } catch (err) {
      console.error('Failed to load balance sheet data:', err);
      setError('加载技术资产负债表数据失败');
    } finally {
      setLoading(false);
    }
  };

  const calculateAssetValue = () => {
    return techAssets.reduce((total, asset) => total + (asset.value_score || 0), 0);
  };

  const calculateNetAssetValue = () => {
    return techNetAssets.reduce((total, asset) => total + (asset.mastery_score || 0), 0);
  };

  const calculateDebtValue = () => {
    return techDebts.reduce((total, debt) => total + (debt.importance_score || 0), 0);
  };

  const getNetTechEquity = () => {
    return calculateNetAssetValue();
  };

  const getLeverageRatio = () => {
    const netAssets = calculateNetAssetValue();
    if (netAssets === 0) return 0;
    return calculateDebtValue() / netAssets;
  };

  const getLeverageEmoji = (ratio: number) => {
    if (ratio === 0) return '🟢'; // 无杠杆
    if (ratio <= 0.3) return '🟡'; // 低杠杆
    if (ratio <= 0.7) return '🟠'; // 适中杠杆
    if (ratio <= 1.2) return '🔴'; // 高杠杆
    return '💀'; // 危险杠杆
  };

  const getLeverageDescription = (ratio: number) => {
    if (ratio === 0) return '无杠杆 - 保守稳健';
    if (ratio <= 0.3) return '低杠杆 - 可适度增加学习挑战';
    if (ratio <= 0.7) return '适中杠杆 - 理想的学习状态';
    if (ratio <= 1.2) return '高杠杆 - 需要巩固基础';
    return '危险杠杆 - 急需降低学习负债';
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-600 bg-red-50';
      case 'high': return 'text-orange-600 bg-orange-50';
      case 'medium': return 'text-yellow-600 bg-yellow-50';
      case 'low': return 'text-green-600 bg-green-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case 'critical': return 'text-red-600 bg-red-50';
      case 'high': return 'text-orange-600 bg-orange-50';
      case 'medium': return 'text-yellow-600 bg-yellow-50';
      case 'low': return 'text-green-600 bg-green-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getProficiencyColor = (level: string) => {
    switch (level) {
      case 'expert': return 'text-purple-600 bg-purple-50';
      case 'advanced': return 'text-blue-600 bg-blue-50';
      case 'intermediate': return 'text-green-600 bg-green-50';
      case 'beginner': return 'text-yellow-600 bg-yellow-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded mb-4"></div>
          <div className="space-y-3">
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="text-center text-red-600">
          <AlertTriangle className="w-12 h-12 mx-auto mb-4" />
          <p>{error}</p>
          <button 
            onClick={loadBalanceSheetData}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            重新加载
          </button>
        </div>
      </div>
    );
  }

  const netEquity = getNetTechEquity();
  const assetValue = calculateAssetValue();
  const debtValue = calculateDebtValue();

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center">
          <BarChart3 className="w-6 h-6 mr-2 text-blue-600" />
          技术资产负债表
        </h2>
        <div className="text-sm text-gray-500">
          更新时间: {new Date().toLocaleString()}
        </div>
      </div>

      {/* 资产负债概览 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-green-50 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-green-800">技术资产</h3>
              <p className="text-2xl font-bold text-green-600">{assetValue.toFixed(1)}</p>
              <p className="text-xs text-green-600">{techAssets.length} 个AI辅助项目</p>
            </div>
            <TrendingUp className="w-8 h-8 text-green-600" />
          </div>
        </div>

        <div className="bg-red-50 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-red-800">技术负债</h3>
              <p className="text-2xl font-bold text-red-600">{debtValue.toFixed(1)}</p>
              <p className="text-xs text-red-600">{techDebts.length} 项待学习</p>
            </div>
            <TrendingDown className="w-8 h-8 text-red-600" />
          </div>
        </div>

        <div className={`${netEquity >= 0 ? 'bg-blue-50' : 'bg-orange-50'} rounded-lg p-4`}>
          <div className="flex items-center justify-between">
            <div>
              <h3 className={`text-sm font-medium ${netEquity >= 0 ? 'text-blue-800' : 'text-orange-800'}`}>
                技术净资产
              </h3>
              <p className={`text-2xl font-bold ${netEquity >= 0 ? 'text-blue-600' : 'text-orange-600'}`}>
                {netEquity.toFixed(1)}
              </p>
              <p className={`text-xs ${netEquity >= 0 ? 'text-blue-600' : 'text-orange-600'}`}>
                {techNetAssets.length} 项掌握技能
              </p>
            </div>
            <Target className={`w-8 h-8 ${netEquity >= 0 ? 'text-blue-600' : 'text-orange-600'}`} />
          </div>
        </div>

        <div className="bg-purple-50 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-purple-800">技术杠杆率</h3>
              <p className="text-2xl font-bold text-purple-600 flex items-center">
                <span className="mr-2">{getLeverageEmoji(getLeverageRatio())}</span>
                {getLeverageRatio().toFixed(2)}
              </p>
              <p className="text-xs text-purple-600">
                {getLeverageDescription(getLeverageRatio())}
              </p>
            </div>
            <BarChart3 className="w-8 h-8 text-purple-600" />
          </div>
        </div>
      </div>

      {/* 详细资产负债表 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 技术资产 */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <CheckCircle className="w-5 h-5 mr-2 text-green-600" />
            技术资产 (AI辅助项目)
          </h3>
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {techAssets.length > 0 ? (
              techAssets.map((asset) => (
                <div key={asset.id} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-gray-900">{asset.project_name}</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        getProficiencyColor(asset.completion_status)
                      }`}>
                        {asset.completion_status}
                      </span>
                    </div>
                    <div className="flex items-center mt-1">
                      <span className="text-sm text-gray-600 mr-2">{asset.technology_used}</span>
                      <div className="flex-1 bg-gray-200 rounded-full h-2 mr-2">
                        <div 
                          className="bg-orange-500 h-2 rounded-full" 
                          style={{ width: `${asset.ai_assistance_level}%` }}
                        ></div>
                      </div>
                      <span className="text-xs text-gray-600">AI辅助{asset.ai_assistance_level}%</span>
                    </div>
                  </div>
                  <div className="ml-4 text-right">
                    <div className="text-sm font-medium text-green-600">
                      +{asset.value_score?.toFixed(1) || '0.0'}
                    </div>
                    <div className="text-xs text-gray-500">{asset.category}</div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center text-gray-500 py-8">
                <CheckCircle className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                <p>暂无技术资产记录</p>
              </div>
            )}
          </div>
        </div>

        {/* 技术净资产 */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Target className="w-5 h-5 mr-2 text-blue-600" />
            技术净资产 (真正掌握)
          </h3>
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {techNetAssets.length > 0 ? (
              techNetAssets.map((asset) => (
                <div key={asset.id} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-gray-900">{asset.technology_name}</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        getProficiencyColor(asset.proficiency_level)
                      }`}>
                        {asset.proficiency_level}
                      </span>
                    </div>
                    <div className="flex items-center mt-1">
                      <div className="flex-1 bg-gray-200 rounded-full h-2 mr-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full" 
                          style={{ width: `${asset.proficiency_score}%` }}
                        ></div>
                      </div>
                      <span className="text-sm text-gray-600">{asset.proficiency_score}%</span>
                    </div>
                  </div>
                  <div className="ml-4 text-right">
                    <div className="text-sm font-medium text-blue-600">
                      +{asset.mastery_score?.toFixed(1) || '0.0'}
                    </div>
                    <div className="text-xs text-gray-500">{asset.category}</div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center text-gray-500 py-8">
                <Target className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                <p>暂无净资产记录</p>
              </div>
            )}
          </div>
        </div>

        {/* 技术负债 */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Clock className="w-5 h-5 mr-2 text-red-600" />
            技术负债 (待学习技能)
          </h3>
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {techDebts.length > 0 ? (
              techDebts.map((debt) => (
                <div key={debt.id} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-gray-900">{debt.technology_name}</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        getUrgencyColor(debt.urgency_level)
                      }`}>
                        {debt.urgency_level}
                      </span>
                    </div>
                    <div className="flex items-center mt-1">
                      <span className="text-sm text-gray-600">
                        目标: {debt.target_proficiency_level}
                      </span>
                      {debt.estimated_learning_hours && (
                        <span className="ml-2 text-xs text-gray-500">
                          预计 {debt.estimated_learning_hours}h
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="ml-4 text-right">
                    <div className="text-sm font-medium text-red-600">
                      -{debt.importance_score?.toFixed(1) || '0.0'}
                    </div>
                    <div className="text-xs text-gray-500">重要性</div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center text-gray-500 py-8">
                <Clock className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                <p>暂无技术负债记录</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 传统技术债务汇总 */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">代码技术债务汇总</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">{debtSummary?.summary?.total_debts || 0}</div>
            <div className="text-sm text-gray-600">总债务</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">{debtSummary?.summary?.open_debts || 0}</div>
            <div className="text-sm text-gray-600">未解决</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{debtSummary?.summary?.resolved_debts || 0}</div>
            <div className="text-sm text-gray-600">已解决</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{debtSummary?.summary?.resolution_rate?.toFixed(1) || '0.0'}</div>
            <div className="text-sm text-gray-600">解决率(%)</div>
          </div>
        </div>
      </div>

      {/* 操作按钮 */}
      <div className="mt-6 flex justify-between items-center">
        <button 
          onClick={loadBalanceSheetData}
          className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 flex items-center"
        >
          <Clock className="w-4 h-4 mr-1" />
          刷新数据
        </button>
        
        {onViewReport && (
          <button 
            onClick={onViewReport}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            查看详细报告
          </button>
        )}
      </div>
    </div>
  );
};

export default TechnicalDebtBalanceSheet;