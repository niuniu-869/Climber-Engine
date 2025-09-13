import React, { useState } from 'react';
import { ArrowLeft, BarChart3, FileText, AlertTriangle, CheckCircle, TrendingUp, Search } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const CodeAnalysis: React.FC = () => {
  const navigate = useNavigate();
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisComplete, setAnalysisComplete] = useState(false);

  const analysisResults = {
    overall: {
      score: 85,
      grade: 'B+',
      filesAnalyzed: 127,
      linesOfCode: 15420
    },
    metrics: {
      complexity: { score: 78, status: 'good' },
      maintainability: { score: 82, status: 'good' },
      testCoverage: { score: 65, status: 'warning' },
      security: { score: 92, status: 'excellent' },
      performance: { score: 88, status: 'good' },
      documentation: { score: 70, status: 'warning' }
    },
    issues: [
      {
        id: 1,
        type: 'warning',
        title: '函数复杂度过高',
        file: 'src/utils/dataProcessor.ts',
        line: 45,
        description: 'calculateMetrics函数的圈复杂度为12，建议重构为多个小函数',
        severity: 'medium'
      },
      {
        id: 2,
        type: 'error',
        title: '潜在的内存泄漏',
        file: 'src/components/Chart.tsx',
        line: 78,
        description: 'useEffect缺少清理函数，可能导致内存泄漏',
        severity: 'high'
      },
      {
        id: 3,
        type: 'info',
        title: '未使用的导入',
        file: 'src/pages/Dashboard.tsx',
        line: 3,
        description: '导入的lodash库未被使用',
        severity: 'low'
      },
      {
        id: 4,
        type: 'warning',
        title: '缺少类型注解',
        file: 'src/services/api.ts',
        line: 23,
        description: 'fetchUserData函数缺少返回类型注解',
        severity: 'medium'
      }
    ],
    suggestions: [
      '增加单元测试覆盖率至80%以上',
      '为所有公共API添加JSDoc文档',
      '使用ESLint规则检查代码风格一致性',
      '考虑使用代码分割优化包大小',
      '实施代码审查流程'
    ]
  };

  const handleStartAnalysis = () => {
    setIsAnalyzing(true);
    // 模拟分析过程
    setTimeout(() => {
      setIsAnalyzing(false);
      setAnalysisComplete(true);
    }, 3000);
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'excellent': return 'bg-green-100 text-green-800';
      case 'good': return 'bg-blue-100 text-blue-800';
      case 'warning': return 'bg-yellow-100 text-yellow-800';
      case 'poor': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'high': return <AlertTriangle className="w-5 h-5 text-red-500" />;
      case 'medium': return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      case 'low': return <AlertTriangle className="w-5 h-5 text-blue-500" />;
      default: return <AlertTriangle className="w-5 h-5 text-gray-500" />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-100">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* 头部导航 */}
        <div className="flex items-center mb-8">
          <button
            onClick={() => navigate('/home')}
            className="flex items-center text-purple-600 hover:text-purple-800 transition-colors mr-4"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            返回主页
          </button>
          <div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">代码质量分析</h1>
            <p className="text-xl text-gray-600">全面分析代码质量，发现潜在问题</p>
          </div>
        </div>

        {!analysisComplete && (
          <div className="bg-white rounded-lg shadow-lg p-8 text-center">
            {!isAnalyzing ? (
              <div>
                <BarChart3 className="w-16 h-16 text-purple-600 mx-auto mb-4" />
                <h2 className="text-2xl font-bold text-gray-900 mb-4">开始代码分析</h2>
                <p className="text-gray-600 mb-6">点击下方按钮开始分析您的代码质量</p>
                <button
                  onClick={handleStartAnalysis}
                  className="bg-purple-600 text-white px-8 py-3 rounded-lg hover:bg-purple-700 transition-colors flex items-center mx-auto"
                >
                  <Search className="w-5 h-5 mr-2" />
                  开始分析
                </button>
              </div>
            ) : (
              <div>
                <div className="animate-spin w-16 h-16 border-4 border-purple-200 border-t-purple-600 rounded-full mx-auto mb-4"></div>
                <h2 className="text-2xl font-bold text-gray-900 mb-4">正在分析中...</h2>
                <p className="text-gray-600">正在扫描代码文件，分析质量指标</p>
              </div>
            )}
          </div>
        )}

        {analysisComplete && (
          <div className="space-y-8">
            {/* 总体评分 */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">总体评分</h2>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="text-center">
                  <div className={`text-6xl font-bold mb-2 ${getScoreColor(analysisResults.overall.score)}`}>
                    {analysisResults.overall.score}
                  </div>
                  <div className="text-2xl font-semibold text-gray-700 mb-1">{analysisResults.overall.grade}</div>
                  <div className="text-gray-500">总体评分</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-600 mb-2">{analysisResults.overall.filesAnalyzed}</div>
                  <div className="text-gray-500">分析文件数</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-green-600 mb-2">{analysisResults.overall.linesOfCode.toLocaleString()}</div>
                  <div className="text-gray-500">代码行数</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-purple-600 mb-2">{analysisResults.issues.length}</div>
                  <div className="text-gray-500">发现问题</div>
                </div>
              </div>
            </div>

            {/* 质量指标 */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">质量指标</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {Object.entries(analysisResults.metrics).map(([key, metric]) => (
                  <div key={key} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-semibold text-gray-900 capitalize">
                        {key === 'complexity' && '代码复杂度'}
                        {key === 'maintainability' && '可维护性'}
                        {key === 'testCoverage' && '测试覆盖率'}
                        {key === 'security' && '安全性'}
                        {key === 'performance' && '性能'}
                        {key === 'documentation' && '文档完整性'}
                      </h3>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(metric.status)}`}>
                        {metric.status === 'excellent' && '优秀'}
                        {metric.status === 'good' && '良好'}
                        {metric.status === 'warning' && '警告'}
                        {metric.status === 'poor' && '较差'}
                      </span>
                    </div>
                    <div className="flex items-center">
                      <div className="flex-1 bg-gray-200 rounded-full h-2 mr-3">
                        <div 
                          className={`h-2 rounded-full ${
                            metric.score >= 90 ? 'bg-green-500' :
                            metric.score >= 70 ? 'bg-yellow-500' : 'bg-red-500'
                          }`}
                          style={{ width: `${metric.score}%` }}
                        ></div>
                      </div>
                      <span className={`font-bold ${getScoreColor(metric.score)}`}>{metric.score}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 问题列表 */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">发现的问题</h2>
              <div className="space-y-4">
                {analysisResults.issues.map((issue) => (
                  <div key={issue.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-start">
                      <div className="mr-3 mt-1">
                        {getSeverityIcon(issue.severity)}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center mb-2">
                          <h3 className="font-semibold text-gray-900 mr-3">{issue.title}</h3>
                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                            issue.severity === 'high' ? 'bg-red-100 text-red-800' :
                            issue.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-blue-100 text-blue-800'
                          }`}>
                            {issue.severity === 'high' && '高'}
                            {issue.severity === 'medium' && '中'}
                            {issue.severity === 'low' && '低'}
                          </span>
                        </div>
                        <p className="text-gray-600 mb-2">{issue.description}</p>
                        <div className="text-sm text-gray-500">
                          <span className="font-medium">{issue.file}</span> : 第 {issue.line} 行
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 改进建议 */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">改进建议</h2>
              <div className="space-y-3">
                {analysisResults.suggestions.map((suggestion, index) => (
                  <div key={index} className="flex items-start">
                    <CheckCircle className="w-5 h-5 text-green-500 mr-3 mt-0.5" />
                    <span className="text-gray-700">{suggestion}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CodeAnalysis;