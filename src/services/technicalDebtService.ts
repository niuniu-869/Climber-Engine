import { apiService } from './api';

// 技术债务相关的类型定义
export interface TechnicalDebt {
  id: number;
  code_record_id: number;
  title: string;
  description: string;
  debt_type: string;
  category?: string;
  file_path?: string;
  line_start?: number;
  line_end?: number;
  severity: 'critical' | 'high' | 'medium' | 'low';
  priority: number;
  impact_score: number;
  effort_estimate: number;
  status: 'open' | 'in_progress' | 'resolved' | 'ignored' | 'wont_fix';
  age_days: number;
  created_at: string;
  first_detected: string;
  resolved_at?: string;
}

export interface TechnicalDebtSummary {
  summary: {
    total_debts: number;
    open_debts: number;
    resolved_debts: number;
    resolution_rate: number;
    total_impact_score: number;
    total_estimated_effort_minutes: number;
    total_estimated_effort_hours: number;
  };
  severity_distribution: Array<{
    severity: string;
    count: number;
  }>;
  type_distribution: Array<{
    debt_type: string;
    count: number;
  }>;
}

export interface DebtMetricsOverview {
  summary: TechnicalDebtSummary;
  trends: {
    daily_activity: Record<string, any>;
    resolution_velocity: number;
    average_age: number;
  };
  recommendations: Array<{
    debt_id: number;
    priority_score: number;
    impact_analysis: Record<string, any>;
    suggested_actions: string[];
    estimated_effort: number;
  }>;
}

class TechnicalDebtService {
  // 获取技术债务列表
  async getTechnicalDebts(params?: {
    user_id?: number;
    severity?: string;
    status?: string;
    debt_type?: string;
    skip?: number;
    limit?: number;
  }): Promise<TechnicalDebt[]> {
    const queryParams = new URLSearchParams();
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, value.toString());
        }
      });
    }
    
    const endpoint = `/technical-debt/?${queryParams.toString()}`;
    return apiService.get<TechnicalDebt[]>(endpoint);
  }

  // 获取用户技术债务汇总
  async getUserDebtSummary(userId: number, days: number = 30): Promise<TechnicalDebtSummary> {
    return apiService.get<TechnicalDebtSummary>(`/technical-debt/user/${userId}/summary?days=${days}`);
  }

  // 获取技术债务指标概览
  async getDebtMetricsOverview(userId?: number): Promise<DebtMetricsOverview> {
    const endpoint = userId 
      ? `/technical-debt/metrics/overview?user_id=${userId}`
      : '/technical-debt/metrics/overview';
    return apiService.get<DebtMetricsOverview>(endpoint);
  }

  // 获取单个技术债务详情
  async getTechnicalDebt(debtId: number): Promise<TechnicalDebt> {
    return apiService.get<TechnicalDebt>(`/technical-debt/${debtId}`);
  }

  // 创建技术债务
  async createTechnicalDebt(debtData: Partial<TechnicalDebt>): Promise<TechnicalDebt> {
    return apiService.post<TechnicalDebt>('/technical-debt/', debtData);
  }

  // 更新技术债务
  async updateTechnicalDebt(debtId: number, debtData: Partial<TechnicalDebt>): Promise<TechnicalDebt> {
    return apiService.put<TechnicalDebt>(`/technical-debt/${debtId}`, debtData);
  }

  // 解决技术债务
  async resolveTechnicalDebt(debtId: number, resolutionNotes?: string): Promise<{ message: string }> {
    return apiService.post<{ message: string }>(`/technical-debt/${debtId}/resolve`, {
      resolution_notes: resolutionNotes
    });
  }

  // 删除技术债务
  async deleteTechnicalDebt(debtId: number): Promise<void> {
    return apiService.delete<void>(`/technical-debt/${debtId}`);
  }

  // 分析代码获取技术债务
  async analyzeCodeForDebt(params: {
    user_id: number;
    file_path: string;
    code_content: string;
  }): Promise<any> {
    return apiService.post<any>('/technical-debt/analyze', params);
  }

  // 获取债务解决建议
  async getDebtResolutionRecommendations(userId: number): Promise<any> {
    return apiService.post<any>(`/technical-debt/user/${userId}/recommendations`);
  }
}

export const technicalDebtService = new TechnicalDebtService();
export default TechnicalDebtService;