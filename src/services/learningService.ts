import { apiService } from './api';

// 学习内容相关的类型定义
export interface LearningArticle {
  id: number;
  user_id: number;
  title: string;
  subtitle?: string;
  summary?: string;
  article_type: string;
  category: string;
  subcategory?: string;
  target_technologies: string[];
  difficulty_level: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  target_audience?: string;
  learning_objectives?: string[];
  content_quality_score: number;
  educational_value: number;
  view_count: number;
  user_rating: number;
  estimated_reading_time: number;
  status: string;
  is_featured: boolean;
  created_at: string;
  published_at?: string;
}

export interface LearningQuestion {
  id: number;
  user_id: number;
  related_article_id?: number;
  title: string;
  question_type: 'multiple_choice' | 'coding' | 'essay' | 'true_false' | 'fill_blank' | 'practical';
  target_technologies: string[];
  difficulty_level: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  complexity_score: number;
  estimated_time: number;
  max_score: number;
  passing_score: number;
  attempt_count: number;
  correct_count: number;
  average_score: number;
  question_quality_score: number;
  status: string;
  is_featured: boolean;
  created_at: string;
  last_attempted_at?: string;
}

export interface QuestionAttempt {
  id: number;
  user_id: number;
  question_id: number;
  is_correct: boolean;
  score: number;
  time_spent: number;
  hint_used_count: number;
  confidence_level: number;
  understanding_level: number;
  satisfaction_rating: number;
  started_at: string;
  submitted_at?: string;
  created_at: string;
}

export interface LearningProgress {
  technology: string;
  articles_available: number;
  questions_available: number;
  attempt_statistics: {
    total_attempts: number;
    correct_attempts: number;
    accuracy_rate: number;
    average_time_spent: number;
    daily_activity: Record<string, any>;
    technology_performance: Record<string, any>;
  };
  learning_materials: {
    articles: Array<{
      id: number;
      title: string;
      difficulty: string;
      reading_time: number;
    }>;
    questions: Array<{
      id: number;
      difficulty: string;
      type: string;
    }>;
  };
}

export interface ContentGenerationRequest {
  user_id: number;
  technology?: string;
  content_type: 'mixed' | 'article' | 'quiz' | 'exercise';
  difficulty?: string;
  count: number;
}

export interface ContentGenerationResponse {
  status: string;
  content_count: number;
  technologies: string[];
  content: any[];
  saved_ids: number[];
  generated_at: string;
}

export interface LearningRecommendation {
  recommended_technologies: Array<{
    technology: string;
    reason: string;
    urgency?: string;
    importance?: number;
    recommended_difficulty: string;
  }>;
  suggested_content: {
    articles: LearningArticle[];
    questions: LearningQuestion[];
  };
  learning_path: Array<{
    step: number;
    technology: string;
    estimated_duration: number;
    prerequisites: string[];
  }>;
}

class LearningService {
  // ==================== Coding Tutor Agent API ====================
  
  // 生成学习内容
  async generateLearningContent(request: ContentGenerationRequest): Promise<ContentGenerationResponse> {
    return apiService.post<ContentGenerationResponse>('/coding-tutor-agent/generate-content', request);
  }

  // 获取学习推荐
  async getLearningRecommendations(userId: number, limit: number = 10): Promise<LearningRecommendation> {
    return apiService.get<LearningRecommendation>(`/coding-tutor-agent/recommendations?user_id=${userId}&limit=${limit}`);
  }

  // 记录学习尝试
  async recordLearningAttempt(attemptData: {
    user_id: number;
    content_id: number;
    content_type: string;
    attempt_data: any;
  }): Promise<any> {
    return apiService.post<any>('/coding-tutor-agent/record-attempt', attemptData);
  }

  // 提交测验答案
  async submitQuiz(submissionData: {
    user_id: number;
    question_id: number;
    answers: any;
    time_spent: number;
  }): Promise<any> {
    return apiService.post<any>('/coding-tutor-agent/submit-quiz', submissionData);
  }

  // 获取用户学习文章
  async getUserArticles(params: {
    user_id: number;
    technology?: string;
    difficulty_level?: string;
    limit?: number;
  }): Promise<LearningArticle[]> {
    const { user_id, ...queryParams } = params;
    const query = new URLSearchParams();
    
    Object.entries(queryParams).forEach(([key, value]) => {
      if (value !== undefined) {
        query.append(key, value.toString());
      }
    });
    
    const endpoint = `/coding-tutor-agent/users/${user_id}/articles?${query.toString()}`;
    return apiService.get<LearningArticle[]>(endpoint);
  }

  // 获取用户学习问题
  async getUserQuestions(params: {
    user_id: number;
    technology?: string;
    difficulty_level?: string;
    question_type?: string;
    limit?: number;
  }): Promise<LearningQuestion[]> {
    const { user_id, ...queryParams } = params;
    const query = new URLSearchParams();
    
    Object.entries(queryParams).forEach(([key, value]) => {
      if (value !== undefined) {
        query.append(key, value.toString());
      }
    });
    
    const endpoint = `/coding-tutor-agent/users/${user_id}/questions?${query.toString()}`;
    return apiService.get<LearningQuestion[]>(endpoint);
  }

  // 获取学习进度
  async getLearningProgress(userId: number, technology: string): Promise<LearningProgress> {
    return apiService.get<LearningProgress>(`/coding-tutor-agent/users/${userId}/progress/${technology}`);
  }

  // 获取用户学习统计
  async getUserLearningStatistics(params: {
    user_id: number;
    technology?: string;
    days?: number;
  }): Promise<any> {
    const { user_id, ...queryParams } = params;
    const query = new URLSearchParams();
    
    Object.entries(queryParams).forEach(([key, value]) => {
      if (value !== undefined) {
        query.append(key, value.toString());
      }
    });
    
    const endpoint = `/coding-tutor-agent/users/${user_id}/statistics?${query.toString()}`;
    return apiService.get<any>(endpoint);
  }

  // 获取推荐内容
  async getRecommendedContent(params: {
    user_id: number;
    technology: string;
    difficulty_level: string;
    content_type?: string;
    limit?: number;
  }): Promise<any> {
    const query = new URLSearchParams();
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        query.append(key, value.toString());
      }
    });
    
    const endpoint = `/coding-tutor-agent/content/recommended?${query.toString()}`;
    return apiService.get<any>(endpoint);
  }

  // ==================== 技术栈负债相关 API ====================
  
  // 获取用户技术栈负债
  async getUserTechDebts(params: {
    user_id: number;
    status_filter?: string;
    urgency_level?: string;
    is_active?: boolean;
  }): Promise<any[]> {
    const { user_id, ...queryParams } = params;
    const query = new URLSearchParams();
    
    Object.entries(queryParams).forEach(([key, value]) => {
      if (value !== undefined) {
        query.append(key, value.toString());
      }
    });
    
    const endpoint = `/tech-stack-agent/users/${user_id}/debts?${query.toString()}`;
    return apiService.get<any[]>(endpoint);
  }

  // 获取用户技术栈资产 (AI辅助项目)
  async getUserTechAssets(params: {
    user_id: number;
    category?: string;
    proficiency_level?: string;
    is_active?: boolean;
  }): Promise<any[]> {
    const { user_id, ...queryParams } = params;
    const query = new URLSearchParams();
    
    Object.entries(queryParams).forEach(([key, value]) => {
      if (value !== undefined) {
        query.append(key, value.toString());
      }
    });
    
    const endpoint = `/tech-stack-agent/users/${user_id}/assets?${query.toString()}`;
    return apiService.get<any[]>(endpoint);
  }

  // 获取用户技术净资产 (真正掌握的技能)
  async getUserTechNetAssets(params: {
    user_id: number;
    category?: string;
    proficiency_level?: string;
    is_active?: boolean;
  }): Promise<any[]> {
    const { user_id, ...queryParams } = params;
    const query = new URLSearchParams();
    
    Object.entries(queryParams).forEach(([key, value]) => {
      if (value !== undefined) {
        query.append(key, value.toString());
      }
    });
    
    const endpoint = `/tech-stack-agent/users/${user_id}/net-assets?${query.toString()}`;
    return apiService.get<any[]>(endpoint);
  }
}

export const learningService = new LearningService();
export default LearningService;