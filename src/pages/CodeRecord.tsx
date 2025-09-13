import React, { useState } from 'react';
import { ArrowLeft, Plus, FileText, Calendar, Tag, Search, Filter, Edit, Trash2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const CodeRecord: React.FC = () => {
  const navigate = useNavigate();
  const [showAddForm, setShowAddForm] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTag, setSelectedTag] = useState('all');

  const [records, setRecords] = useState([
    {
      id: 1,
      title: '实现用户认证系统',
      description: '使用JWT实现用户登录、注册和权限验证功能',
      code: `// JWT认证中间件\nconst authenticateToken = (req, res, next) => {\n  const authHeader = req.headers['authorization'];\n  const token = authHeader && authHeader.split(' ')[1];\n  \n  if (!token) {\n    return res.sendStatus(401);\n  }\n  \n  jwt.verify(token, process.env.ACCESS_TOKEN_SECRET, (err, user) => {\n    if (err) return res.sendStatus(403);\n    req.user = user;\n    next();\n  });\n};`,
      tags: ['认证', 'JWT', 'Node.js'],
      language: 'javascript',
      createdAt: '2024-01-15',
      updatedAt: '2024-01-15'
    },
    {
      id: 2,
      title: 'React Hook 表单验证',
      description: '自定义Hook实现表单验证逻辑，支持多种验证规则',
      code: `// 自定义表单验证Hook\nimport { useState, useEffect } from 'react';\n\nconst useFormValidation = (initialState, validate) => {\n  const [values, setValues] = useState(initialState);\n  const [errors, setErrors] = useState({});\n  const [isSubmitting, setIsSubmitting] = useState(false);\n\n  useEffect(() => {\n    if (isSubmitting) {\n      const noErrors = Object.keys(errors).length === 0;\n      if (noErrors) {\n        // 提交表单\n        setIsSubmitting(false);\n      } else {\n        setIsSubmitting(false);\n      }\n    }\n  }, [errors, isSubmitting]);\n\n  const handleChange = (event) => {\n    setValues({\n      ...values,\n      [event.target.name]: event.target.value\n    });\n  };\n\n  const handleSubmit = (event) => {\n    event.preventDefault();\n    const validationErrors = validate(values);\n    setErrors(validationErrors);\n    setIsSubmitting(true);\n  };\n\n  return {\n    handleChange,\n    handleSubmit,\n    values,\n    errors,\n    isSubmitting\n  };\n};\n\nexport default useFormValidation;`,
      tags: ['React', 'Hook', '表单验证'],
      language: 'javascript',
      createdAt: '2024-01-12',
      updatedAt: '2024-01-14'
    },
    {
      id: 3,
      title: 'Python 数据处理工具',
      description: 'pandas数据清洗和转换的常用函数集合',
      code: `import pandas as pd\nimport numpy as np\n\ndef clean_data(df):\n    """数据清洗函数"""\n    # 删除重复行\n    df = df.drop_duplicates()\n    \n    # 处理缺失值\n    df = df.fillna(method='ffill')\n    \n    # 数据类型转换\n    for col in df.select_dtypes(include=['object']).columns:\n        df[col] = df[col].astype('category')\n    \n    return df\n\ndef transform_data(df, columns):\n    """数据转换函数"""\n    for col in columns:\n        if col in df.columns:\n            # 标准化数值列\n            if df[col].dtype in ['int64', 'float64']:\n                df[col] = (df[col] - df[col].mean()) / df[col].std()\n    \n    return df`,
      tags: ['Python', 'pandas', '数据处理'],
      language: 'python',
      createdAt: '2024-01-10',
      updatedAt: '2024-01-10'
    }
  ]);

  const [newRecord, setNewRecord] = useState({
    title: '',
    description: '',
    code: '',
    tags: '',
    language: 'javascript'
  });

  const allTags = ['all', ...new Set(records.flatMap(record => record.tags))];

  const filteredRecords = records.filter(record => {
    const matchesSearch = record.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         record.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesTag = selectedTag === 'all' || record.tags.includes(selectedTag);
    return matchesSearch && matchesTag;
  });

  const handleAddRecord = () => {
    if (newRecord.title && newRecord.code) {
      const record = {
        id: Date.now(),
        ...newRecord,
        tags: newRecord.tags.split(',').map(tag => tag.trim()).filter(tag => tag),
        createdAt: new Date().toISOString().split('T')[0],
        updatedAt: new Date().toISOString().split('T')[0]
      };
      setRecords([record, ...records]);
      setNewRecord({ title: '', description: '', code: '', tags: '', language: 'javascript' });
      setShowAddForm(false);
    }
  };

  const handleDeleteRecord = (id: number) => {
    setRecords(records.filter(record => record.id !== id));
  };

  const getLanguageColor = (language: string) => {
    switch (language) {
      case 'javascript': return 'bg-yellow-100 text-yellow-800';
      case 'python': return 'bg-blue-100 text-blue-800';
      case 'typescript': return 'bg-blue-100 text-blue-800';
      case 'java': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-purple-100">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* 头部导航 */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center">
            <button
              onClick={() => navigate('/home')}
              className="flex items-center text-indigo-600 hover:text-indigo-800 transition-colors mr-4"
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              返回主页
            </button>
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-2">代码记录</h1>
              <p className="text-xl text-gray-600">记录和管理您的代码片段</p>
            </div>
          </div>
          <button
            onClick={() => setShowAddForm(true)}
            className="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition-colors flex items-center"
          >
            <Plus className="w-5 h-5 mr-2" />
            添加记录
          </button>
        </div>

        {/* 统计信息 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center">
              <FileText className="w-8 h-8 text-indigo-600 mr-3" />
              <div>
                <h3 className="text-lg font-semibold text-gray-900">总记录数</h3>
                <p className="text-2xl font-bold text-indigo-600">{records.length}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center">
              <Tag className="w-8 h-8 text-green-600 mr-3" />
              <div>
                <h3 className="text-lg font-semibold text-gray-900">标签数量</h3>
                <p className="text-2xl font-bold text-green-600">{allTags.length - 1}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center">
              <Calendar className="w-8 h-8 text-purple-600 mr-3" />
              <div>
                <h3 className="text-lg font-semibold text-gray-900">最近更新</h3>
                <p className="text-2xl font-bold text-purple-600">今天</p>
              </div>
            </div>
          </div>
        </div>

        {/* 搜索和过滤 */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="搜索代码记录..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
            <div className="flex items-center space-x-2">
              <Filter className="w-5 h-5 text-gray-400" />
              <select
                value={selectedTag}
                onChange={(e) => setSelectedTag(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              >
                {allTags.map(tag => (
                  <option key={tag} value={tag}>
                    {tag === 'all' ? '全部标签' : tag}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* 代码记录列表 */}
        <div className="space-y-6">
          {filteredRecords.map((record) => (
            <div key={record.id} className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">{record.title}</h3>
                  <p className="text-gray-600 mb-3">{record.description}</p>
                  <div className="flex items-center space-x-4 text-sm text-gray-500">
                    <span className={`px-2 py-1 rounded ${getLanguageColor(record.language)}`}>
                      {record.language}
                    </span>
                    <span>创建: {record.createdAt}</span>
                    <span>更新: {record.updatedAt}</span>
                  </div>
                </div>
                <div className="flex space-x-2">
                  <button className="p-2 text-gray-400 hover:text-blue-600 transition-colors">
                    <Edit className="w-4 h-4" />
                  </button>
                  <button 
                    onClick={() => handleDeleteRecord(record.id)}
                    className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
              
              {/* 标签 */}
              <div className="flex flex-wrap gap-2 mb-4">
                {record.tags.map((tag, index) => (
                  <span key={index} className="px-2 py-1 bg-indigo-100 text-indigo-800 rounded text-sm">
                    {tag}
                  </span>
                ))}
              </div>
              
              {/* 代码块 */}
              <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto">
                <pre className="text-green-400 text-sm">
                  <code>{record.code}</code>
                </pre>
              </div>
            </div>
          ))}
        </div>

        {/* 添加记录表单模态框 */}
        {showAddForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">添加新的代码记录</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">标题</label>
                  <input
                    type="text"
                    value={newRecord.title}
                    onChange={(e) => setNewRecord({...newRecord, title: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="输入代码记录标题"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">描述</label>
                  <textarea
                    value={newRecord.description}
                    onChange={(e) => setNewRecord({...newRecord, description: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    rows={3}
                    placeholder="输入代码描述"
                  />
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">编程语言</label>
                    <select
                      value={newRecord.language}
                      onChange={(e) => setNewRecord({...newRecord, language: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    >
                      <option value="javascript">JavaScript</option>
                      <option value="typescript">TypeScript</option>
                      <option value="python">Python</option>
                      <option value="java">Java</option>
                      <option value="css">CSS</option>
                      <option value="html">HTML</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">标签 (用逗号分隔)</label>
                    <input
                      type="text"
                      value={newRecord.tags}
                      onChange={(e) => setNewRecord({...newRecord, tags: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      placeholder="React, Hook, 表单"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">代码</label>
                  <textarea
                    value={newRecord.code}
                    onChange={(e) => setNewRecord({...newRecord, code: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent font-mono"
                    rows={10}
                    placeholder="粘贴您的代码..."
                  />
                </div>
              </div>
              
              <div className="flex justify-end space-x-4 mt-6">
                <button
                  onClick={() => setShowAddForm(false)}
                  className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  取消
                </button>
                <button
                  onClick={handleAddRecord}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  保存记录
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CodeRecord;