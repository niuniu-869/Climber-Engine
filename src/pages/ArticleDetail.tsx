import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { BookOpen, Clock, Star, ArrowLeft, CheckCircle, User, Calendar } from 'lucide-react';
import { apiService } from '../services/api';
import { LearningArticle } from '../services/learningService';

// 扩展的文章接口，包含完整的文章内容
interface FullLearningArticle extends LearningArticle {
  content?: string;
  code_examples?: Array<{
    title: string;
    code: string;
    language: string;
  }>;
}

const ArticleDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [article, setArticle] = useState<FullLearningArticle | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [readingProgress, setReadingProgress] = useState(0);
  const [startTime] = useState(Date.now());

  useEffect(() => {
    if (id) {
      loadArticle(parseInt(id));
    }
  }, [id]);

  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = window.pageYOffset;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      const scrollPercent = (scrollTop / docHeight) * 100;
      setReadingProgress(Math.min(scrollPercent, 100));
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const loadArticle = async (articleId: number) => {
    try {
      setLoading(true);
      const articleData = await apiService.get<FullLearningArticle>(`/coding-tutor-agent/articles/${articleId}`);
      setArticle(articleData);
    } catch (err) {
      console.error('Failed to load article:', err);
      setError('加载文章失败');
    } finally {
      setLoading(false);
    }
  };

  const markAsCompleted = async () => {
    if (!article) return;
    
    try {
      const readingTime = Math.round((Date.now() - startTime) / 1000 / 60); // 分钟
      await apiService.post('/coding-tutor-agent/record-attempt', {
        user_id: article.user_id,
        content_id: article.id,
        content_type: 'article',
        attempt_data: {
          reading_time: readingTime,
          completion_rate: readingProgress,
          completed: true
        }
      });
      
      // 显示完成提示
      alert('文章学习完成！');
      navigate(-1);
    } catch (err) {
      console.error('Failed to record reading:', err);
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

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-pulse text-center">
          <BookOpen className="w-12 h-12 mx-auto mb-4 text-gray-400" />
          <p className="text-gray-600">加载文章中...</p>
        </div>
      </div>
    );
  }

  if (error || !article) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <BookOpen className="w-12 h-12 mx-auto mb-4 text-red-400" />
          <p className="text-red-600 mb-4">{error || '文章不存在'}</p>
          <button 
            onClick={() => navigate(-1)}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            返回
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 阅读进度条 */}
      <div className="fixed top-0 left-0 w-full h-1 bg-gray-200 z-50">
        <div 
          className="h-full bg-blue-600 transition-all duration-300"
          style={{ width: `${readingProgress}%` }}
        />
      </div>

      {/* 头部导航 */}
      <div className="bg-white shadow-sm border-b sticky top-0 z-40">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <button 
              onClick={() => navigate(-1)}
              className="flex items-center text-gray-600 hover:text-gray-800"
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              返回学习中心
            </button>
            
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-500">
                阅读进度: {Math.round(readingProgress)}%
              </span>
              <button 
                onClick={markAsCompleted}
                className="flex items-center px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
              >
                <CheckCircle className="w-4 h-4 mr-2" />
                标记完成
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* 文章内容 */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* 文章头部信息 */}
        <div className="bg-white rounded-lg shadow-sm p-8 mb-6">
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">{article.title}</h1>
            {article.subtitle && (
              <p className="text-xl text-gray-600 mb-4">{article.subtitle}</p>
            )}
            
            <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500">
              <span className={`px-3 py-1 rounded-full font-medium ${
                getDifficultyColor(article.difficulty_level)
              }`}>
                {article.difficulty_level}
              </span>
              
              <span className="flex items-center">
                <Clock className="w-4 h-4 mr-1" />
                {article.estimated_reading_time} 分钟阅读
              </span>
              
              <span className="flex items-center">
                <Star className="w-4 h-4 mr-1" />
                {article.user_rating.toFixed(1)} 评分
              </span>
              
              <span className="flex items-center">
                <User className="w-4 h-4 mr-1" />
                {article.view_count} 次阅读
              </span>
              
              <span className="flex items-center">
                <Calendar className="w-4 h-4 mr-1" />
                {new Date(article.created_at).toLocaleDateString()}
              </span>
            </div>
          </div>

          {/* 技术标签 */}
          {article.target_technologies && article.target_technologies.length > 0 && (
            <div className="mb-6">
              <h3 className="text-sm font-medium text-gray-700 mb-2">涉及技术:</h3>
              <div className="flex flex-wrap gap-2">
                {article.target_technologies.map((tech, index) => (
                  <span key={index} className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">
                    {tech}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* 学习目标 */}
          {article.learning_objectives && article.learning_objectives.length > 0 && (
            <div className="mb-6">
              <h3 className="text-sm font-medium text-gray-700 mb-2">学习目标:</h3>
              <ul className="list-disc list-inside space-y-1 text-gray-600">
                {article.learning_objectives.map((objective, index) => (
                  <li key={index}>{objective}</li>
                ))}
              </ul>
            </div>
          )}

          {/* 文章摘要 */}
          {article.summary && (
            <div className="mb-6 p-4 bg-blue-50 rounded-lg">
              <h3 className="text-sm font-medium text-blue-800 mb-2">文章摘要</h3>
              <p className="text-blue-700">{article.summary}</p>
            </div>
          )}
        </div>

        {/* 文章正文 */}
        <div className="bg-white rounded-lg shadow-sm p-8">
          <div className="prose prose-lg max-w-none">
            {article.content.split('\n').map((paragraph, index) => {
              if (paragraph.startsWith('##')) {
                return (
                  <h2 key={index} className="text-2xl font-bold text-gray-900 mt-8 mb-4">
                    {paragraph.replace('##', '').trim()}
                  </h2>
                );
              } else if (paragraph.startsWith('#')) {
                return (
                  <h1 key={index} className="text-3xl font-bold text-gray-900 mt-8 mb-4">
                    {paragraph.replace('#', '').trim()}
                  </h1>
                );
              } else if (paragraph.startsWith('```')) {
                return (
                  <pre key={index} className="bg-gray-100 p-4 rounded-lg overflow-x-auto my-4">
                    <code>{paragraph.replace(/```\w*/, '').replace('```', '')}</code>
                  </pre>
                );
              } else if (paragraph.trim()) {
                return (
                  <p key={index} className="text-gray-700 leading-relaxed mb-4">
                    {paragraph}
                  </p>
                );
              }
              return null;
            })}
          </div>

          {/* 代码示例 */}
          {article.code_examples && article.code_examples.length > 0 && (
            <div className="mt-8">
              <h3 className="text-xl font-bold text-gray-900 mb-4">代码示例</h3>
              {article.code_examples.map((example: any, index: number) => (
                <div key={index} className="mb-6">
                  <h4 className="text-lg font-medium text-gray-800 mb-2">{example.title}</h4>
                  <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto">
                    <code>{example.code}</code>
                  </pre>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* 底部操作 */}
        <div className="mt-8 flex justify-between items-center">
          <button 
            onClick={() => navigate(-1)}
            className="flex items-center px-6 py-3 text-gray-600 hover:text-gray-800"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            返回学习中心
          </button>
          
          <button 
            onClick={markAsCompleted}
            className="flex items-center px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            <CheckCircle className="w-5 h-5 mr-2" />
            完成学习
          </button>
        </div>
      </div>
    </div>
  );
};

export default ArticleDetail;