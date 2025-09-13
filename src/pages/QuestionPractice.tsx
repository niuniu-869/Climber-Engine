import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Brain, Clock, Star, ArrowLeft, CheckCircle, AlertCircle, Lightbulb, Code } from 'lucide-react';
import { apiService } from '../services/api';
import { LearningQuestion } from '../services/learningService';

// 扩展的题目接口，包含完整的题目内容
interface FullLearningQuestion extends LearningQuestion {
  question_text?: string;
  options?: Array<{
    id: string;
    text: string;
  }> | string[];
  correct_answer?: string;
  explanation?: string;
  hints?: string[];
  starter_code?: string;
  test_cases?: Array<{
    input: string;
    expected_output: string;
  }>;
}

interface QuestionPracticeProps {
  onLearningComplete?: () => void;
}

const QuestionPractice: React.FC<QuestionPracticeProps> = ({ onLearningComplete }) => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [question, setQuestion] = useState<FullLearningQuestion | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedAnswer, setSelectedAnswer] = useState<string>('');
  const [userCode, setUserCode] = useState<string>('');
  const [submitted, setSubmitted] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [showHint, setShowHint] = useState(false);
  const [startTime] = useState(Date.now());

  useEffect(() => {
    if (id) {
      loadQuestion(parseInt(id));
    }
  }, [id]);

  const loadQuestion = async (questionId: number) => {
    try {
      setLoading(true);
      const questionData = await apiService.get<FullLearningQuestion>(`/coding-tutor-agent/questions/${questionId}`);
      setQuestion(questionData);
      if (questionData.starter_code) {
        setUserCode(questionData.starter_code);
      }
    } catch (err) {
      console.error('Failed to load question:', err);
      setError('加载题目失败');
    } finally {
      setLoading(false);
    }
  };

  const submitAnswer = async () => {
    if (!question) return;
    
    try {
      const timeSpent = Math.round((Date.now() - startTime) / 1000); // 秒
      const attemptData = {
        user_id: question.user_id,
        content_id: question.id,
        content_type: 'question',
        attempt_data: {
          answer: question.question_type === 'coding' ? userCode : selectedAnswer,
          time_spent: timeSpent,
          question_type: question.question_type
        }
      };
      
      const response = await apiService.post('/coding-tutor-agent/record-attempt', attemptData);
      setResult(response);
      setSubmitted(true);
      
      // 通知父组件更新学习进度
      if (onLearningComplete) {
        onLearningComplete();
      }
    } catch (err) {
      console.error('Failed to submit answer:', err);
      setError('提交答案失败');
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

  const getQuestionTypeIcon = (type: string) => {
    switch (type) {
      case 'coding': return <Code className="w-5 h-5" />;
      case 'multiple_choice': return <Brain className="w-5 h-5" />;
      default: return <Brain className="w-5 h-5" />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-pulse text-center">
          <Brain className="w-12 h-12 mx-auto mb-4 text-gray-400" />
          <p className="text-gray-600">加载题目中...</p>
        </div>
      </div>
    );
  }

  if (error || !question) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Brain className="w-12 h-12 mx-auto mb-4 text-red-400" />
          <p className="text-red-600 mb-4">{error || '题目不存在'}</p>
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
      {/* 头部导航 */}
      <div className="bg-white shadow-sm border-b">
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
              {question.hints && question.hints.length > 0 && (
                <button 
                  onClick={() => setShowHint(!showHint)}
                  className="flex items-center px-4 py-2 text-blue-600 hover:text-blue-800"
                >
                  <Lightbulb className="w-4 h-4 mr-2" />
                  {showHint ? '隐藏提示' : '显示提示'}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* 题目信息 */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-gray-900 mb-2">{question.title}</h1>
              <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500">
                <span className={`px-3 py-1 rounded-full font-medium ${
                  getDifficultyColor(question.difficulty_level)
                }`}>
                  {question.difficulty_level}
                </span>
                
                <span className="flex items-center">
                  {getQuestionTypeIcon(question.question_type)}
                  <span className="ml-1">{question.question_type}</span>
                </span>
                
                <span className="flex items-center">
                  <Clock className="w-4 h-4 mr-1" />
                  {question.estimated_time} 分钟
                </span>
                
                <span className="flex items-center">
                  <Star className="w-4 h-4 mr-1" />
                  {question.max_score} 分
                </span>
              </div>
            </div>
          </div>

          {/* 技术标签 */}
          {question.target_technologies && question.target_technologies.length > 0 && (
            <div className="mb-4">
              <div className="flex flex-wrap gap-2">
                {question.target_technologies.map((tech, index) => (
                  <span key={index} className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">
                    {tech}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* 题目描述 */}
          {question.question_text && (
            <div className="prose max-w-none">
              <p className="text-gray-700 leading-relaxed">{question.question_text}</p>
            </div>
          )}
        </div>

        {/* 提示信息 */}
        {showHint && question.hints && question.hints.length > 0 && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
            <div className="flex items-start">
              <Lightbulb className="w-5 h-5 text-yellow-600 mr-2 mt-0.5" />
              <div>
                <h3 className="text-yellow-800 font-medium mb-2">提示</h3>
                <ul className="text-yellow-700 space-y-1">
                  {question.hints.map((hint, index) => (
                    <li key={index}>• {hint}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* 答题区域 */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          {question.question_type === 'multiple_choice' && question.options && (
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">请选择正确答案:</h3>
              <div className="space-y-3">
                {question.options.map((option, index) => {
                  // 处理字符串数组和对象数组两种格式
                  const optionId = typeof option === 'string' ? index.toString() : option.id;
                  const optionText = typeof option === 'string' ? option : option.text;
                  
                  return (
                    <label key={optionId} className="flex items-center p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
                      <input
                        type="radio"
                        name="answer"
                        value={optionId}
                        checked={selectedAnswer === optionId}
                        onChange={(e) => setSelectedAnswer(e.target.value)}
                        disabled={submitted}
                        className="mr-3"
                      />
                      <span className="text-gray-700">{optionText}</span>
                    </label>
                  );
                })}
              </div>
            </div>
          )}

          {question.question_type === 'coding' && (
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">编写代码:</h3>
              <textarea
                value={userCode}
                onChange={(e) => setUserCode(e.target.value)}
                disabled={submitted}
                className="w-full h-64 p-4 border rounded-lg font-mono text-sm bg-gray-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="在这里编写你的代码..."
              />
              
              {/* 测试用例 */}
              {question.test_cases && question.test_cases.length > 0 && (
                <div className="mt-4">
                  <h4 className="text-md font-medium text-gray-800 mb-2">测试用例:</h4>
                  <div className="space-y-2">
                    {question.test_cases.map((testCase, index) => (
                      <div key={index} className="bg-gray-100 p-3 rounded text-sm">
                        <div><strong>输入:</strong> {testCase.input}</div>
                        <div><strong>期望输出:</strong> {testCase.expected_output}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* 提交按钮 */}
          {!submitted && (
            <div className="mt-6 flex justify-end">
              <button
                onClick={submitAnswer}
                disabled={!selectedAnswer && !userCode.trim()}
                className="flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                <CheckCircle className="w-5 h-5 mr-2" />
                提交答案
              </button>
            </div>
          )}
        </div>

        {/* 结果显示 */}
        {submitted && result && (
          <div className={`rounded-lg p-6 mb-6 ${
            result.is_correct ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
          }`}>
            <div className="flex items-start">
              {result.is_correct ? (
                <CheckCircle className="w-6 h-6 text-green-600 mr-3 mt-0.5" />
              ) : (
                <AlertCircle className="w-6 h-6 text-red-600 mr-3 mt-0.5" />
              )}
              <div className="flex-1">
                <h3 className={`text-lg font-medium mb-2 ${
                  result.is_correct ? 'text-green-800' : 'text-red-800'
                }`}>
                  {result.is_correct ? '回答正确！' : '回答错误'}
                </h3>
                
                {result.score && (
                  <p className={`mb-2 ${
                    result.is_correct ? 'text-green-700' : 'text-red-700'
                  }`}>
                    得分: {result.score} / {question.max_score}
                  </p>
                )}
                
                {question.explanation && (
                  <div className="mt-4">
                    <h4 className="font-medium text-gray-800 mb-2">解析:</h4>
                    <p className="text-gray-700">{question.explanation}</p>
                  </div>
                )}
                
                {question.correct_answer && (
                  <div className="mt-4">
                    <h4 className="font-medium text-gray-800 mb-2">正确答案:</h4>
                    <p className="text-gray-700">{question.correct_answer}</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* 底部操作 */}
        <div className="flex justify-between items-center">
          <button 
            onClick={() => navigate(-1)}
            className="flex items-center px-6 py-3 text-gray-600 hover:text-gray-800"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            返回学习中心
          </button>
          
          {submitted && (
            <button 
              onClick={() => navigate('/learning-center')}
              className="flex items-center px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              <CheckCircle className="w-5 h-5 mr-2" />
              完成练习
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

// 创建一个包装组件来处理路由
const QuestionPracticeWrapper: React.FC = () => {
  const handleLearningComplete = () => {
    // 触发全局事件来通知其他组件更新
    window.dispatchEvent(new CustomEvent('learningProgressUpdate'));
  };

  return <QuestionPractice onLearningComplete={handleLearningComplete} />;
};

export default QuestionPracticeWrapper;