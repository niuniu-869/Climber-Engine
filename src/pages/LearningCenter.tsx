import React, { useState } from 'react';
import { ArrowLeft, BookOpen, Play, CheckCircle, Clock, Star, Award } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const LearningCenter: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('courses');

  const courses = [
    {
      id: 1,
      title: 'React 最佳实践',
      description: '学习React开发的最佳实践和设计模式',
      progress: 60,
      duration: '4小时',
      difficulty: '中级',
      rating: 4.8,
      lessons: 12,
      completed: 7
    },
    {
      id: 2,
      title: '代码重构技巧',
      description: '掌握代码重构的原则和实用技巧',
      progress: 30,
      duration: '3小时',
      difficulty: '高级',
      rating: 4.9,
      lessons: 10,
      completed: 3
    },
    {
      id: 3,
      title: '性能优化指南',
      description: '前端性能优化的策略和工具使用',
      progress: 80,
      duration: '5小时',
      difficulty: '高级',
      rating: 4.7,
      lessons: 15,
      completed: 12
    },
    {
      id: 4,
      title: 'TypeScript 进阶',
      description: 'TypeScript高级特性和类型系统',
      progress: 0,
      duration: '6小时',
      difficulty: '高级',
      rating: 4.6,
      lessons: 18,
      completed: 0
    }
  ];

  const achievements = [
    {
      id: 1,
      title: '代码质量专家',
      description: '完成所有代码质量相关课程',
      icon: '🏆',
      earned: true,
      date: '2024-01-15'
    },
    {
      id: 2,
      title: 'React 大师',
      description: '精通React开发技能',
      icon: '⚛️',
      earned: true,
      date: '2024-01-10'
    },
    {
      id: 3,
      title: '性能优化师',
      description: '掌握前端性能优化技能',
      icon: '🚀',
      earned: false,
      date: null
    },
    {
      id: 4,
      title: '学习达人',
      description: '连续学习30天',
      icon: '📚',
      earned: false,
      date: null
    }
  ];

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case '初级': return 'text-green-600 bg-green-50';
      case '中级': return 'text-yellow-600 bg-yellow-50';
      case '高级': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const handleStartCourse = (courseId: number) => {
    alert(`开始学习课程 ${courseId}`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-100">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* 头部导航 */}
        <div className="flex items-center mb-8">
          <button
            onClick={() => navigate('/home')}
            className="flex items-center text-green-600 hover:text-green-800 transition-colors mr-4"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            返回主页
          </button>
          <div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">学习中心</h1>
            <p className="text-xl text-gray-600">提升技能，成就更好的自己</p>
          </div>
        </div>

        {/* 学习统计 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center">
              <BookOpen className="w-8 h-8 text-blue-600 mr-3" />
              <div>
                <h3 className="text-lg font-semibold text-gray-900">总课程</h3>
                <p className="text-2xl font-bold text-blue-600">{courses.length}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center">
              <CheckCircle className="w-8 h-8 text-green-600 mr-3" />
              <div>
                <h3 className="text-lg font-semibold text-gray-900">已完成</h3>
                <p className="text-2xl font-bold text-green-600">{courses.filter(c => c.progress === 100).length}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center">
              <Clock className="w-8 h-8 text-orange-600 mr-3" />
              <div>
                <h3 className="text-lg font-semibold text-gray-900">学习时长</h3>
                <p className="text-2xl font-bold text-orange-600">24h</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center">
              <Award className="w-8 h-8 text-purple-600 mr-3" />
              <div>
                <h3 className="text-lg font-semibold text-gray-900">成就</h3>
                <p className="text-2xl font-bold text-purple-600">{achievements.filter(a => a.earned).length}</p>
              </div>
            </div>
          </div>
        </div>

        {/* 标签页导航 */}
        <div className="bg-white rounded-lg shadow-lg mb-8">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6">
              <button
                onClick={() => setActiveTab('courses')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'courses'
                    ? 'border-green-500 text-green-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                我的课程
              </button>
              <button
                onClick={() => setActiveTab('achievements')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'achievements'
                    ? 'border-green-500 text-green-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                成就徽章
              </button>
            </nav>
          </div>

          <div className="p-6">
            {activeTab === 'courses' && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {courses.map((course) => (
                  <div key={course.id} className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <h3 className="text-xl font-semibold text-gray-900 mb-2">{course.title}</h3>
                        <p className="text-gray-600 mb-3">{course.description}</p>
                        <div className="flex items-center space-x-4 text-sm text-gray-500 mb-4">
                          <span className={`px-2 py-1 rounded ${getDifficultyColor(course.difficulty)}`}>
                            {course.difficulty}
                          </span>
                          <span className="flex items-center">
                            <Clock className="w-4 h-4 mr-1" />
                            {course.duration}
                          </span>
                          <span className="flex items-center">
                            <Star className="w-4 h-4 mr-1 text-yellow-500" />
                            {course.rating}
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    {/* 进度条 */}
                    <div className="mb-4">
                      <div className="flex justify-between text-sm text-gray-600 mb-1">
                        <span>进度: {course.completed}/{course.lessons} 课时</span>
                        <span>{course.progress}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-green-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${course.progress}%` }}
                        ></div>
                      </div>
                    </div>
                    
                    <button
                      onClick={() => handleStartCourse(course.id)}
                      className="w-full bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center"
                    >
                      <Play className="w-4 h-4 mr-2" />
                      {course.progress > 0 ? '继续学习' : '开始学习'}
                    </button>
                  </div>
                ))}
              </div>
            )}

            {activeTab === 'achievements' && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {achievements.map((achievement) => (
                  <div 
                    key={achievement.id} 
                    className={`border rounded-lg p-6 text-center ${
                      achievement.earned 
                        ? 'border-green-200 bg-green-50' 
                        : 'border-gray-200 bg-gray-50'
                    }`}
                  >
                    <div className="text-4xl mb-4">{achievement.icon}</div>
                    <h3 className={`text-lg font-semibold mb-2 ${
                      achievement.earned ? 'text-green-800' : 'text-gray-500'
                    }`}>
                      {achievement.title}
                    </h3>
                    <p className={`text-sm mb-4 ${
                      achievement.earned ? 'text-green-600' : 'text-gray-400'
                    }`}>
                      {achievement.description}
                    </p>
                    {achievement.earned && achievement.date && (
                      <p className="text-xs text-green-500">获得于: {achievement.date}</p>
                    )}
                    {!achievement.earned && (
                      <p className="text-xs text-gray-400">尚未获得</p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LearningCenter;