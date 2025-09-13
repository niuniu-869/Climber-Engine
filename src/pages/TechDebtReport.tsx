import React from 'react';
import { ArrowLeft, AlertTriangle, TrendingUp, Clock, Users } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const TechDebtReport: React.FC = () => {
  const navigate = useNavigate();

  const debtItems = [
    {
      id: 1,
      title: '代码重复率过高',
      severity: 'high',
      impact: '维护成本增加',
      estimatedHours: 16,
      files: ['src/utils/helpers.js', 'src/components/Form.tsx'],
      description: '多个文件中存在相似的业务逻辑代码，建议提取公共函数。'
    },
    {
      id: 2,
      title: '过时的依赖包',
      severity: 'medium',
      impact: '安全风险',
      estimatedHours: 8,
      files: ['package.json'],
      description: '项目中使用了多个过时的npm包，存在安全漏洞。'
    },
    {
      id: 3,
      title: '缺少单元测试',
      severity: 'medium',
      impact: '代码质量',
      estimatedHours: 24,
      files: ['src/services/', 'src/utils/'],
      description: '核心业务逻辑缺少单元测试覆盖。'
    },
    {
      id: 4,
      title: '性能瓶颈',
      severity: 'low',
      impact: '用户体验',
      estimatedHours: 12,
      files: ['src/components/DataTable.tsx'],
      description: '大数据量渲染时存在性能问题。'
    }
  ];

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'text-red-600 bg-red-50 border-red-200';
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'low': return 'text-green-600 bg-green-50 border-green-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getSeverityText = (severity: string) => {
    switch (severity) {
      case 'high': return '高优先级';
      case 'medium': return '中优先级';
      case 'low': return '低优先级';
      default: return '未知';
    }
  };

  const totalHours = debtItems.reduce((sum, item) => sum + item.estimatedHours, 0);
  const highPriorityCount = debtItems.filter(item => item.severity === 'high').length;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* 头部导航 */}
        <div className="flex items-center mb-8">
          <button
            onClick={() => navigate('/home')}
            className="flex items-center text-blue-600 hover:text-blue-800 transition-colors mr-4"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            返回主页
          </button>
          <div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">技术债务详细报告</h1>
            <p className="text-xl text-gray-600">代码质量分析与改进建议</p>
          </div>
        </div>

        {/* 统计概览 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center">
              <AlertTriangle className="w-8 h-8 text-red-600 mr-3" />
              <div>
                <h3 className="text-lg font-semibold text-gray-900">总债务项</h3>
                <p className="text-2xl font-bold text-red-600">{debtItems.length}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center">
              <TrendingUp className="w-8 h-8 text-orange-600 mr-3" />
              <div>
                <h3 className="text-lg font-semibold text-gray-900">高优先级</h3>
                <p className="text-2xl font-bold text-orange-600">{highPriorityCount}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center">
              <Clock className="w-8 h-8 text-blue-600 mr-3" />
              <div>
                <h3 className="text-lg font-semibold text-gray-900">预估工时</h3>
                <p className="text-2xl font-bold text-blue-600">{totalHours}h</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center">
              <Users className="w-8 h-8 text-green-600 mr-3" />
              <div>
                <h3 className="text-lg font-semibold text-gray-900">建议人员</h3>
                <p className="text-2xl font-bold text-green-600">2-3人</p>
              </div>
            </div>
          </div>
        </div>

        {/* 债务详情列表 */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">债务详情</h2>
          <div className="space-y-6">
            {debtItems.map((item) => (
              <div key={item.id} className="border border-gray-200 rounded-lg p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center mb-2">
                      <h3 className="text-xl font-semibold text-gray-900 mr-3">{item.title}</h3>
                      <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getSeverityColor(item.severity)}`}>
                        {getSeverityText(item.severity)}
                      </span>
                    </div>
                    <p className="text-gray-600 mb-3">{item.description}</p>
                    <div className="flex items-center space-x-6 text-sm text-gray-500">
                      <span>影响: {item.impact}</span>
                      <span>预估工时: {item.estimatedHours}小时</span>
                    </div>
                  </div>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">涉及文件:</h4>
                  <div className="flex flex-wrap gap-2">
                    {item.files.map((file, index) => (
                      <span key={index} className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-sm">
                        {file}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 行动建议 */}
        <div className="bg-white rounded-lg shadow-lg p-6 mt-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">行动建议</h2>
          <div className="space-y-4">
            <div className="flex items-start">
              <div className="w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-bold mr-4 mt-1">1</div>
              <div>
                <h3 className="font-semibold text-gray-900">优先处理高优先级债务</h3>
                <p className="text-gray-600">建议先解决代码重复率问题，这将显著降低维护成本。</p>
              </div>
            </div>
            <div className="flex items-start">
              <div className="w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-bold mr-4 mt-1">2</div>
              <div>
                <h3 className="font-semibold text-gray-900">建立代码审查流程</h3>
                <p className="text-gray-600">实施代码审查机制，防止新的技术债务产生。</p>
              </div>
            </div>
            <div className="flex items-start">
              <div className="w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-bold mr-4 mt-1">3</div>
              <div>
                <h3 className="font-semibold text-gray-900">定期更新依赖</h3>
                <p className="text-gray-600">建立定期更新依赖包的流程，确保项目安全性。</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TechDebtReport;