import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { bitable } from '@lark-base-open/js-sdk';
import { userApi, type UserStatus } from '@/api/user';
import { ElMessage, ElMessageBox } from 'element-plus';
import axios from 'axios';

// 全局用户状态
const userStatus = ref<UserStatus | null>(null);
const isLoading = ref(false);
const isInitialized = ref(false);

// 生成客户端指纹（用于识别设备）
function generateClientFingerprint(): string {
  try {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    let canvasData = '';
    
    if (ctx) {
      ctx.textBaseline = 'top';
      ctx.font = '14px Arial';
      ctx.fillText('fingerprint', 2, 2);
      canvasData = canvas.toDataURL().substring(0, 50);
    }
    
    const fingerprint = {
      userAgent: navigator.userAgent,
      language: navigator.language,
      platform: navigator.platform,
      screenResolution: `${screen.width}x${screen.height}`,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      canvasHash: canvasData
    };
    
    return btoa(JSON.stringify(fingerprint));
  } catch (e) {
    console.warn('生成客户端指纹失败:', e);
    return '';
  }
}

// 配置 axios 拦截器，自动携带 session token
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('session_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 处理 token 过期
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Token 过期，清除并重新初始化
      localStorage.removeItem('session_token');
      isInitialized.value = false;
      ElMessage.warning('登录已过期，请刷新页面');
    }
    return Promise.reject(error);
  }
);

export function useUser() {
  const router = useRouter();

  /**
   * 初始化用户（应用启动时调用一次）
   */
  const initUser = async () => {
    if (isInitialized.value) {
      return userStatus.value;
    }

    isLoading.value = true;
    try {
      // 获取飞书用户ID
      const feishuUserId = await bitable.bridge.getUserId();
      
      let tenantKey: string | undefined;

      try {
        tenantKey = await bitable.bridge.getTenantKey();
      } catch (e) {
        // 某些环境可能不支持获取租户ID
        console.warn('获取租户Key失败:', e);
      }

      // 生成客户端指纹
      const clientFingerprint = generateClientFingerprint();

      // 初始化用户（会返回 session_token）
      const response = await userApi.init(feishuUserId, tenantKey, undefined, clientFingerprint);
      
      // 保存 session token
      if (response.session_token) {
        localStorage.setItem('session_token', response.session_token);
      }
      
      userStatus.value = response.user;
      isInitialized.value = true;

      return userStatus.value;
    } catch (error: any) {
      console.error('[useUser] 初始化用户失败:', error);
      console.error('[useUser] 错误详情:', error.response?.data);
      
      // 处理特定错误
      if (error.response?.status === 403) {
        ElMessage.error('请在飞书客户端中使用本插件');
      } else if (error.response?.status === 429) {
        ElMessage.error('请求过于频繁，请稍后再试');
      } else {
        ElMessage.error('初始化失败，请刷新页面重试');
      }
      
      return null;
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * 刷新用户状态
   */
  const refreshStatus = async () => {
    if (!userStatus.value) return;

    try {
      userStatus.value = await userApi.getStatus(userStatus.value.feishu_user_id);
    } catch (error) {
      console.error('刷新用户状态失败:', error);
    }
  };

  /**
   * 检查并使用功能
   * @param feature 功能名称
   * @returns 是否允许使用
   */
  const checkAndUseFeature = async (
    feature: 'pdf_export' | 'ai_generate' | 'signature' | 'premium_templates'
  ): Promise<boolean> => {
    if (!userStatus.value) {
      await initUser();
    }

    if (!userStatus.value) {
      ElMessage.error('用户状态获取失败，请刷新页面重试');
      return false;
    }

    try {
      // 先检查权限
      const permission = await userApi.checkPermission(userStatus.value.feishu_user_id, feature);

      if (!permission.allowed) {
        // 显示错误提示
        ElMessage.warning(permission.reason || '权限不足');

        // 如果是需要升级的功能，可以引导用户到付费页面
        if (permission.reason?.includes('升级会员')) {
          ElMessageBox.confirm(
            permission.reason,
            '需要升级会员',
            {
              confirmButtonText: '去升级',
              cancelButtonText: '取消',
              type: 'warning'
            }
          ).then(() => {
            // 跳转到付费页面
            router.push('/pricing');
          }).catch(() => {
            // 用户取消
          });
        }

        return false;
      }

      // 如果是需要计数的功能，记录使用
      // 记录使用情况
      if (feature === 'pdf_export') {
        await userApi.useFeature(userStatus.value.feishu_user_id, feature);
        // 刷新状态以更新UI
        await refreshStatus();
      }

      return true;
    } catch (error: any) {
      console.error('检查权限失败:', error);
      // 出错时根据错误信息判断
      if (error.response?.status === 404) {
        ElMessage.error('用户不存在，请刷新页面重试');
        return false;
      }
      // 其他错误默认允许，避免阻塞用户
      return true;
    }
  };

  // 计算属性
  const isPro = computed(() =>
    userStatus.value?.plan_type === 'pro' || userStatus.value?.plan_type === 'team'
  );

  const isTeam = computed(() =>
    userStatus.value?.plan_type === 'team'
  );

  const planName = computed(() => {
    switch (userStatus.value?.plan_type) {
      case 'pro': return '专业版';
      case 'team': return '团队版';
      default: return '免费版';
    }
  });

  const pdfExportsRemaining = computed(() => {
    if (!userStatus.value) return 0;
    if (userStatus.value.pdf_exports_limit === -1) return -1;
    return userStatus.value.pdf_exports_limit - userStatus.value.pdf_exports_used;
  });

  const aiGeneratesRemaining = computed(() => {
    if (!userStatus.value) return 0;
    if (userStatus.value.ai_generates_limit === -1) return -1;
    return userStatus.value.ai_generates_limit - userStatus.value.ai_generates_used;
  });

  return {
    userStatus,
    isLoading,
    isInitialized,
    initUser,
    refreshStatus,
    checkAndUseFeature,
    isPro,
    isTeam,
    planName,
    pdfExportsRemaining,
    aiGeneratesRemaining
  };
}
