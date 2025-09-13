import React, { useState, useEffect } from 'react';
import { BookOpen, Brain, Target, TrendingUp, Play, Clock, Star, ChevronRight, Lightbulb, Award } from 'lucide-react';
import { learningService, LearningRecommendation, LearningArticle, LearningQuestion } from '../services/learningService';

interface LearningCenterProps {
  userId: number;
  onStartLearning?: (content: any) => void;
}

interface LearningContent {
  id: number;
  title: string;
  type: 'article' | 'question' | 'exercise';
  technology: string;
  difficulty: string;
  estimatedTime: number;
  progress?: number;
  isRecommended?: boolean;
}

const LearningCenter: React.FC<LearningCenterProps> = ({ 
  userId, 
  onStartLearning 
}) => {
  const [recommendations, setRecommendations] = useState<LearningRecommendation | null>(null);
  const [recentArticles, setRecentArticles] = useState<LearningArticle[]>([]);
  const [practiceQuestions, setPracticeQuestions] = useState<LearningQuestion[]>([]);
  const [userStats, setUserStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTechnology, setSelectedTechnology] = useState<string>('all');

  useEffect(() => {
    loadLearningData();
  }, [userId]);

  const loadLearningData = async () => {
    try {
      setLoading(true);
      setError(null);

      // 并行加载数据
      const [recommendationsData, articlesData, questionsData, statsData] = await Promise.all([
        learningService.getLearningRecommendations(userId, 10),
        learningService.getUserArticles({ 
          user_id: userId, 
          limit: 10 
        }),
        learningService.getUserQuestions({ 
          user_id: userId, 
          limit: 15 
        }),
        learningService.getUserLearningStatistics({ 
          user_id: userId, 
          days: 30 
        })
      ]);

      setRecommendations(recommendationsData);
      setRecentArticles(articlesData);
      setPracticeQuestions(questionsData);
      setUserStats(statsData);
    } catch (err) {
      console.error('Failed to load learning data:', err);
      setError('加载学习数据失败');
    } finally {
      setLoading(false);
    }
  };

  const generateNewContent = async (technology?: string) => {
    try {
      const response = await learningService.generateLearningContent({
        user_id: userId,
        technology,
        content_type: 'mixed',
        count: 5
      });
      
      if (response.status === 'success') {
        // 重新加载数据以显示新生成的内容
        await loadLearningData();
      }
    } catch (err) {
      console.error('Failed to generate content:', err);
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'text-green-600 bg-green-50';
      case 'intermediate': return 'text-blue-600 bg-blue-50';
      case 'advanced': return 'text-purple-600 bg-purple-50';
      case 'expert': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'article': return <BookOpen className="w-4 h-4" />;
      case 'question': return <Brain className="w-4 h-4" />;
      case 'exercise': return <Target className="w-4 h-4" />;
      default: return <BookOpen className="w-4 h-4" />;
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-3">
              <div className="h-4 bg-gray-200 rounded"></div>
              <div className="h-4 bg-gray-200 rounded"></div>
              <div className="h-4 bg-gray-200 rounded"></div>
            </div>
            <div className="space-y-3">
              <div className="h-4 bg-gray-200 rounded"></div>
              <div className="h-4 bg-gray-200 rounded"></div>
              <div className="h-4 bg-gray-200 rounded"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="text-center text-red-600">
          <Brain className="w-12 h-12 mx-auto mb-4" />
          <p>{error}</p>
          <button 
            onClick={loadLearningData}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            重新加载
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center">
          <Brain className="w-6 h-6 mr-2 text-purple-600" />
          AI学习中心
        </h2>
        <button 
          onClick={() => generateNewContent()}
          className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center"
        >
          <Lightbulb className="w-4 h-4 mr-2" />
          生成新内容
        </button>
      </div>

      {/* 学习统计概览 */}
      {userStats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-blue-50 rounded-lg p-4">
            <div className="flex items-center">
              <BookOpen className="w-6 h-6 text-blue-600 mr-2" />
              <div>
                <h3 className="text-sm font-medium text-blue-800">学习文章</h3>
                <p className="text-xl font-bold text-blue-600">{userStats.articles?.total || 0}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-green-50 rounded-lg p-4">
            <div className="flex items-center">
              <Brain className="w-6 h-6 text-green-600 mr-2" />
              <div>
                <h3 className="text-sm font-medium text-green-800">练习题目</h3>
                <p className="text-xl font-bold text-green-600">{userStats.questions?.total || 0}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-purple-50 rounded-lg p-4">
            <div className="flex items-center">
              <TrendingUp className="w-6 h-6 text-purple-600 mr-2" />
              <div>
                <h3 className="text-sm font-medium text-purple-800">正确率</h3>
                <p className="text-xl font-bold text-purple-600">
                  {userStats.accuracy_rate ? `${userStats.accuracy_rate.toFixed(1)}%` : '0%'}
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-orange-50 rounded-lg p-4">
            <div className="flex items-center">
              <Clock className="w-6 h-6 text-orange-600 mr-2" />
              <div>
                <h3 className="text-sm font-medium text-orange-800">学习时长</h3>
                <p className="text-xl font-bold text-orange-600">
                  {userStats.total_time ? `${Math.round(userStats.total_time / 60)}h` : '0h'}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 智能推荐 */}
      {recommendations && recommendations.recommended_technologies && recommendations.recommended_technologies.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Star className="w-5 h-5 mr-2 text-yellow-500" />
            AI智能推荐
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {recommendations.recommended_technologies.slice(0, 6).map((tech, index) => (
              <div key={index} className="border border-yellow-200 bg-yellow-50 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-gray-900">{tech.technology}</h4>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    getDifficultyColor(tech.recommended_difficulty)
                  }`}>
                    {tech.recommended_difficulty}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-3">{tech.reason}</p>
                <div className="flex items-center justify-between">
                  {tech.urgency && (
                    <span className={`px-2 py-1 rounded text-xs ${
                      tech.urgency === 'high' ? 'bg-red-100 text-red-800' :
                      tech.urgency === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {tech.urgency} 优先级
                    </span>
                  )}
                  <button 
                    onClick={() => generateNewContent(tech.technology)}
                    className="text-blue-600 hover:text-blue-800 text-sm font-medium flex items-center"
                  >
                    开始学习 <ChevronRight className="w-4 h-4 ml-1" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 学习内容 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 学习文章 */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <BookOpen className="w-5 h-5 mr-2 text-blue-600" />
            学习文章
          </h3>
          <div className="space-y-3 max-h-80 overflow-y-auto">
            {recentArticles.length > 0 ? (
              recentArticles.map((article) => (
                <div key={article.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900 mb-1">{article.title}</h4>
                      {article.subtitle && (
                        <p className="text-sm text-gray-600 mb-2">{article.subtitle}</p>
                      )}
                      <div className="flex items-center space-x-4 text-xs text-gray-500">
                        <span className={`px-2 py-1 rounded-full ${
                          getDifficultyColor(article.difficulty_level)
                        }`}>
                          {article.difficulty_level}
                        </span>
                        <span className="flex items-center">
                          <Clock className="w-3 h-3 mr-1" />
                          {article.estimated_reading_time}分钟
                        </span>
                        <span className="flex items-center">
                          <Star className="w-3 h-3 mr-1" />
                          {article.user_rating.toFixed(1)}
                        </span>
                      </div>
                    </div>
                    <button 
                      onClick={() => onStartLearning && onStartLearning(article)}
                      className="ml-4 px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 flex items-center"
                    >
                      <Play className="w-3 h-3 mr-1" />
                      阅读
                    </button>
                  </div>
                  <div className="mt-2 flex flex-wrap gap-1">
                    {article.target_technologies && article.target_technologies.slice(0, 3).map((tech, index) => (
                      <span key={index} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                        {tech}
                      </span>
                    ))}
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center text-gray-500 py-8">
                <BookOpen className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                <p>暂无学习文章</p>
                <button 
                  onClick={() => generateNewContent()}
                  className="mt-2 text-blue-600 hover:text-blue-800 text-sm"
                >
                  生成学习内容
                </button>
              </div>
            )}
          </div>
        </div>

        {/* 练习题目 */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Brain className="w-5 h-5 mr-2 text-green-600" />
            练习题目
          </h3>
          <div className="space-y-3 max-h-80 overflow-y-auto">
            {practiceQuestions.length > 0 ? (
              practiceQuestions.map((question) => (
                <div key={question.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900 mb-1">{question.title}</h4>
                      <div className="flex items-center space-x-4 text-xs text-gray-500 mb-2">
                        <span className={`px-2 py-1 rounded-full ${
                          getDifficultyColor(question.difficulty_level)
                        }`}>
                          {question.difficulty_level}
                        </span>
                        <span className="flex items-center">
                          <Clock className="w-3 h-3 mr-1" />
                          {question.estimated_time}分钟
                        </span>
                        <span className="flex items-center">
                          {getTypeIcon(question.question_type)}
                          <span className="ml-1">{question.question_type}</span>
                        </span>
                      </div>
                      <div className="flex items-center text-xs text-gray-500">
                        <span>正确率: {question.attempt_count > 0 ? 
                          ((question.correct_count / question.attempt_count) * 100).toFixed(1) : '0'
                        }%</span>
                        <span className="ml-4">尝试次数: {question.attempt_count}</span>
                      </div>
                    </div>
                    <button 
                      onClick={() => onStartLearning && onStartLearning(question)}
                      className="ml-4 px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700 flex items-center"
                    >
                      <Play className="w-3 h-3 mr-1" />
                      练习
                    </button>
                  </div>
                  <div className="mt-2 flex flex-wrap gap-1">
                    {question.target_technologies && question.target_technologies.slice(0, 3).map((tech, index) => (
                      <span key={index} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                        {tech}
                      </span>
                    ))}
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center text-gray-500 py-8">
                <Brain className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                <p>暂无练习题目</p>
                <button 
                  onClick={() => generateNewContent()}
                  className="mt-2 text-blue-600 hover:text-blue-800 text-sm"
                >
                  生成练习题目
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 学习路径 */}
      {recommendations && recommendations.learning_path && recommendations.learning_path.length > 0 && (
        <div className="mt-6 pt-6 border-t border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Target className="w-5 h-5 mr-2 text-purple-600" />
            推荐学习路径
          </h3>
          <div className="space-y-3">
            {recommendations.learning_path.slice(0, 5).map((step, index) => (
              <div key={index} className="flex items-center p-3 bg-purple-50 rounded-lg">
                <div className="flex-shrink-0 w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
                  {step.step}
                </div>
                <div className="ml-4 flex-1">
                  <h4 className="font-medium text-gray-900">{step.technology}</h4>
                  <div className="flex items-center text-sm text-gray-600">
                    <Clock className="w-4 h-4 mr-1" />
                    <span>预计 {step.estimated_duration} 小时</span>
                    {step.prerequisites && step.prerequisites.length > 0 && (
                      <span className="ml-4">前置: {step.prerequisites.join(', ')}</span>
                    )}
                  </div>
                </div>
                <button 
                  onClick={() => generateNewContent(step.technology)}
                  className="ml-4 px-3 py-1 bg-purple-600 text-white text-sm rounded hover:bg-purple-700"
                >
                  开始
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 操作按钮 */}
      <div className="mt-6 flex justify-between items-center">
        <button 
          onClick={loadLearningData}
          className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 flex items-center"
        >
          <Clock className="w-4 h-4 mr-1" />
          刷新数据
        </button>
        
        <div className="flex space-x-3">
          <button 
            onClick={() => generateNewContent()}
            className="px-4 py-2 bg-green-600 text-white text-sm rounded hover:bg-green-700 flex items-center"
          >
            <Award className="w-4 h-4 mr-1" />
            AI生成内容
          </button>
          
          {onStartLearning && (
            <button 
              onClick={() => onStartLearning(null)}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              进入学习模式
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default LearningCenter;