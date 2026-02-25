<template>
  <div class="pricing-page">
    <nav class="pricing-nav">
      <button @click="router.push('/')" class="nav-back">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
      </button>
      
      <button @click="showRedeemDialog = true" class="btn-redeem-trigger">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.91 8.84 5.91 2.23a1 1 0 0 0-1.24 1.37l2.35 6.4h9.91a1 1 0 0 1 0 2H7.02l-2.35 6.4a1 1 0 0 0 1.24 1.37l15-6.61a1 1 0 0 0 0-1.83z"/></svg>
        兑换邀请码
      </button>
    </nav>

    <!-- 兑换弹窗 -->
    <div v-if="showRedeemDialog" class="dialog-overlay" @click.self="showRedeemDialog = false">
      <div class="dialog">
        <div class="dialog-header">
          <h3>兑换会员权益</h3>
          <button @click="showRedeemDialog = false" class="btn-close">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
          </button>
        </div>
        <div class="dialog-body">
          <p class="dialog-desc">如果您持有活动邀请码，请输入以解锁相应权益。</p>
          <div class="promo-input-wrapper">
            <input 
              v-model="promoCode" 
              type="text" 
              placeholder="请输入12位邀请码"
              class="promo-input"
              maxlength="12"
              @keyup.enter="handleRedeem"
              v-focus
            />
          </div>
          <p v-if="redeemMessage" class="promo-msg" :class="redeemMessageType">
            {{ redeemMessage }}
          </p>
        </div>
        <div class="dialog-footer">
          <button @click="showRedeemDialog = false" class="btn-cancel">取消</button>
          <button 
            @click="handleRedeem" 
            class="btn-confirm"
            :disabled="isRedeeming || !promoCode || promoCode.length !== 12"
          >
            {{ isRedeeming ? '兑换中...' : '立即兑换' }}
          </button>
        </div>
      </div>
    </div>


    <QuotaBar />

    <div class="pricing-header">
      <h1 class="page-title">选择适合您的计划</h1>
      <p class="page-subtitle">简单的价格，强大的功能。升级您的创作体验。</p>
    </div>

    <div class="plans-container">
      <!-- 免费版 -->
      <div class="plan-card">
        <div class="card-header">
          <h3 class="plan-name">免费版</h3>
          <div class="plan-price">
            <span class="amount">0</span>
            <span class="period">/月</span>
          </div>
          <p class="plan-desc">个人尝鲜体验</p>
        </div>
        <div class="card-body">
          <ul class="features-list">
            <li>
              <span class="check-icon">✓</span>
              <span>每月 10 次导出</span>
            </li>
            <li>
              <span class="check-icon">✓</span>
              <span>每月 5 次 AI 生成</span>
            </li>
          </ul>
        </div>
        <div class="card-footer">
          <button class="btn btn-outline" disabled>
            {{ currentPlan === 'free' ? '当前版本' : '已包含' }}
          </button>
        </div>
      </div>

      <!-- 专业版 (推荐) -->
      <div class="plan-card featured" :class="{ 'current-plan': currentPlan === 'pro' }">
        <div class="popular-tag">推荐</div>
        <div class="card-header">
          <h3 class="plan-name">专业版</h3>
          <div class="plan-price">
            
            <span class="amount">{{ proPriceYuan }}</span>
            <span class="period">/月</span>
          </div>
          <p class="plan-desc">适合个人创作者</p>
        </div>
        <div class="card-body">
          <ul class="features-list">
            <li>
              <span class="check-icon">✓</span>
              <span><strong>每月 500 次</strong> 导出</span>
            </li>
            <li>
              <span class="check-icon">✓</span>
              <span><strong>每月 50 次</strong> AI 生成</span>
            </li>
            <li>
              <span class="check-icon">✓</span>
              <span>优先电子签名支持</span>
            </li>
          </ul>
        </div>
        <div class="card-footer">
          <button 
            class="btn btn-primary" 
            @click="handlePurchase('pro')"
            :disabled="!!processingPlan || currentPlan === 'pro'"
          >
            {{ processingPlan === 'pro' ? '处理中...' : currentPlan === 'pro' ? '当前版本' : '立即升级' }}
          </button>
        </div>
      </div>

      <!-- 团队版 -->
      <div class="plan-card" :class="{ 'current-plan': currentPlan === 'team' }">
        <div class="card-header">
          <h3 class="plan-name">团队版</h3>
          <div class="plan-price">
            <span class="amount">{{ teamPriceYuan }}</span>
            <span class="period">/月</span>
          </div>
          <p class="plan-desc">适合小型团队</p>
        </div>
        <div class="card-body">
          <ul class="features-list">
            <li>
              <span class="check-icon">✓</span>
              <span><strong>无限量</strong> 导出</span>
            </li>
            <li>
              <span class="check-icon">✓</span>
              <span><strong>每月 200 次</strong> AI 生成</span>
            </li>
            <li>
              <span class="check-icon">✓</span>
              <span>团队协作与管理</span>
            </li>
          </ul>
        </div>
        <div class="card-footer">
          <button 
            class="btn btn-outline" 
            @click="handlePurchase('team')"
            :disabled="!!processingPlan || currentPlan === 'team'"
          >
            {{ processingPlan === 'team' ? '处理中...' : currentPlan === 'team' ? '当前版本' : '立即升级' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 支付二维码弹窗 -->
    <div v-if="showPayDialog" class="dialog-overlay" @click.self="handleClosePayDialog">
      <div class="dialog pay-dialog">
        <div class="dialog-header">
          <h3>扫码支付</h3>
          <button @click="handleClosePayDialog" class="btn-close">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
          </button>
        </div>
        <div class="dialog-body pay-dialog-body">
          <p class="pay-tip">请使用支付宝扫码支付</p>
          <div class="qr-code-wrapper">
            <img v-if="isBase64Qr" :src="qrCodeUrl" class="qr-code-img" alt="支付二维码" />
            <canvas v-else ref="qrCodeCanvas" class="qr-code-canvas"></canvas>
          </div>
          <div class="order-info">
            <p class="order-amount">支付金额：<strong>¥{{ currentOrderAmount }}</strong></p>
            <p class="order-no">订单号：{{ currentOrderNo }}</p>
          </div>
          <p v-if="payCountdown > 0" class="countdown-tip">请在 {{ payCountdown }} 秒内完成支付</p>
          <p v-else class="countdown-tip expired">支付已超时，请重新下单</p>
        </div>
        <div class="dialog-footer">
          <button @click="handleClosePayDialog" class="btn-cancel">取消支付</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUser } from '@/composables/useUser';
import { paymentApi } from '@/api/payment';
import { promoApi } from '@/api/promo';
import QuotaBar from '@/components/QuotaBar.vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import QRCode from 'qrcode';

const router = useRouter();
const { userStatus, refreshStatus, initUser } = useUser();
const processingPlan = ref<string | null>(null);
const showRedeemDialog = ref(false);
const promoCode = ref('');
const isRedeeming = ref(false);
const redeemMessage = ref('');
const redeemMessageType = ref<'success' | 'error'>('success');

// 支付相关状态
const showPayDialog = ref(false);
const qrCodeCanvas = ref<HTMLCanvasElement | null>(null);
const currentOrderNo = ref('');
const currentOrderAmount = ref('');
const qrCodeUrl = ref(''); // 新增：保存二维码 URL/Base64
const payCountdown = ref(600); // 10分钟倒计时（秒）
const pollTimer = ref<number | null>(null);
const countdownTimer = ref<number | null>(null);

const isBase64Qr = computed(() => {
  return qrCodeUrl.value && qrCodeUrl.value.startsWith('data:image');
});

const plans = ref<{ id: string; price: number; original_price?: number | null; duration_days: number; name: string }[]>([]);

// 自定义指令：自动获取焦点
const vFocus = {
  mounted: (el: HTMLElement) => el.focus()
};

const currentPlan = computed(() => userStatus.value?.plan_type || 'free');

const toYuanDisplay = (cents?: number | null) => {
  const val = Math.round((cents || 0)) / 100;
  // 价格通常展示为整数；有小数时保留两位并去掉多余 0
  const fixed = val.toFixed(2);
  return fixed.endsWith('.00') ? String(Math.round(val)) : fixed.replace(/0+$/, '').replace(/\.$/, '');
};

const proPriceYuan = computed(() => {
  const p = plans.value.find(x => x.id === 'pro');
  return toYuanDisplay(p?.price);
});

const teamPriceYuan = computed(() => {
  const p = plans.value.find(x => x.id === 'team');
  return toYuanDisplay(p?.price);
});

const loadPlans = async () => {
  try {
    const data = await paymentApi.getPlans();
    plans.value = data.plans || [];
  } catch (e) {
    // 拉取失败不阻塞页面（仍可购买，后端会用默认兜底）
    plans.value = [];
  }
};

const handlePurchase = async (planType: 'pro' | 'team') => {
  if (!userStatus.value) {
    ElMessage.error('请先初始化用户');
    return;
  }

  try {
    processingPlan.value = planType;
    await ElMessageBox.confirm(
      `确定要升级到${planType === 'pro' ? '专业版' : '团队版'}吗？`,
      '确认升级',
      {
        confirmButtonText: '确认支付',
        cancelButtonText: '取消',
        type: 'info'
      }
    );

    // 获取计划信息用于显示金额
    const plan = plans.value.find(p => p.id === planType);
    const planPriceYuan = plan ? toYuanDisplay(plan.price) : '0';

    // 创建扫码支付订单
    const payResult = await paymentApi.createAlipayNativePay(
      userStatus.value.feishu_user_id,
      planType
    );

    currentOrderNo.value = payResult.order_no;
    currentOrderAmount.value = planPriceYuan;
    qrCodeUrl.value = payResult.qr_code_url || '';
    payCountdown.value = 600; // 重置倒计时

    // 生成二维码 (仅当不是 Base64 图片时)
    if (!isBase64Qr.value && qrCodeCanvas.value && payResult.qr_code_url) {
      try {
        await QRCode.toCanvas(qrCodeCanvas.value, payResult.qr_code_url, {
          width: 256,
          margin: 2,
          color: {
            dark: '#000000',
            light: '#FFFFFF'
          }
        });
      } catch (err) {
        console.error('生成二维码失败:', err);
        ElMessage.error('生成二维码失败，请重试');
        return;
      }
    }

    // 显示支付弹窗
    showPayDialog.value = true;

    // 启动订单状态轮询
    startOrderPolling(payResult.order_no);

    // 启动倒计时
    startCountdown();

  } catch (error: any) {
    if (error === 'cancel') return;
    console.error('Purchase failed:', error);
    ElMessage.error(error.response?.data?.detail || '无法完成购买，请重试');
  } finally {
    processingPlan.value = null;
  }
};

const startOrderPolling = (orderNo: string) => {
  // 清除之前的定时器
  if (pollTimer.value) {
    clearInterval(pollTimer.value);
  }

  // 每3秒查询一次订单状态
  pollTimer.value = window.setInterval(async () => {
    try {
      const status = await paymentApi.getOrderStatus(orderNo);
      
      if (status.status === 'paid') {
        // 支付成功
        ElMessage.success('支付成功！享受您的新权益。');
        await refreshStatus();
        handleClosePayDialog();
      }
    } catch (error) {
      console.error('查询订单状态失败:', error);
    }
  }, 6000);
};

const startCountdown = () => {
  if (countdownTimer.value) {
    clearInterval(countdownTimer.value);
  }

  countdownTimer.value = window.setInterval(() => {
    if (payCountdown.value > 0) {
      payCountdown.value--;
    } else {
      // 倒计时结束
      if (countdownTimer.value) {
        clearInterval(countdownTimer.value);
        countdownTimer.value = null;
      }
    }
  }, 1000);
};

const handleClosePayDialog = () => {
  showPayDialog.value = false;
  
  // 清除定时器
  if (pollTimer.value) {
    clearInterval(pollTimer.value);
    pollTimer.value = null;
  }
  if (countdownTimer.value) {
    clearInterval(countdownTimer.value);
    countdownTimer.value = null;
  }
  
  // 重置状态
  currentOrderNo.value = '';
  currentOrderAmount.value = '';
  payCountdown.value = 600;
};

const handleRedeem = async () => {
  if (!promoCode.value || promoCode.value.length !== 12) {
    redeemMessage.value = '请输入有效的12位邀请码';
    redeemMessageType.value = 'error';
    return;
  }

  if (!userStatus.value) {
    ElMessage.error('请先初始化用户');
    return;
  }

  try {
    isRedeeming.value = true;
    redeemMessage.value = '';

    const result = await promoApi.redeem(promoCode.value.toUpperCase(), userStatus.value.feishu_user_id);
    
    if (result.success) {
      ElMessage.success('兑换成功！权益已生效');
      await refreshStatus();
      promoCode.value = '';
      showRedeemDialog.value = false;
    } else {
      redeemMessage.value = result.message || '无效的邀请码';
      redeemMessageType.value = 'error';
    }
  } catch (error: any) {
    const errorMsg = error.response?.data?.detail || '兑换服务暂时不可用';
    redeemMessage.value = errorMsg;
    redeemMessageType.value = 'error';
  } finally {
    isRedeeming.value = false;
  }
};

onMounted(async () => {
  await initUser();
  await loadPlans();
});

onUnmounted(() => {
  // 组件卸载时清除定时器
  if (pollTimer.value) {
    clearInterval(pollTimer.value);
  }
  if (countdownTimer.value) {
    clearInterval(countdownTimer.value);
  }
});
</script>

<style scoped>
.pricing-page {
  min-height: 100vh;
  background-color: #ffffff;
  color: #0f172a;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  padding: 0 1.5rem 4rem;
}

.pricing-nav {
  padding: 1.5rem 0;
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-back {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: white;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
  padding: 0;
}

.nav-back:hover {
  border-color: #cbd5e1;
  background: #f8fafc;
  color: #0f172a;
}

.btn-redeem-trigger {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  color: #475569;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-redeem-trigger:hover {
  border-color: #94a3b8;
  color: #0f172a;
  background: #f8fafc;
}

.pricing-header {
  text-align: center;
  margin: 2rem 0 4rem;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 1rem;
  letter-spacing: -0.025em;
}

.page-subtitle {
  font-size: 1.125rem;
  color: #64748b;
  margin: 0;
}

/* Grid Layout */
.plans-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  max-width: 1000px;
  margin: 0 auto 4rem;
  align-items: start;
}

/* Card Styles */
.plan-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  transition: all 0.2s ease;
  position: relative;
}

.plan-card:hover {
  border-color: #cbd5e1;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.025);
  transform: translateY(-2px);
}

.plan-card.featured {
  border: 1px solid #0f172a;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  z-index: 10;
}

.current-plan {
  background-color: #f8fafc;
}

.popular-tag {
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  background-color: #0f172a;
  color: white;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Plan Header */
.card-header {
  text-align: center;
  margin-bottom: 2rem;
  border-bottom: 1px solid #f1f5f9;
  padding-bottom: 1.5rem;
}

.plan-name {
  font-size: 1.25rem;
  font-weight: 600;
  color: #0f172a;
  margin: 0 0 0.5rem;
}

.plan-price {
  display: flex;
  justify-content: center;
  align-items: baseline;
  color: #0f172a;
}

.currency {
  font-size: 1.25rem;
  font-weight: 500;
  margin-right: 0.125rem;
}

.amount {
  font-size: 3rem;
  font-weight: 700;
  line-height: 1;
  letter-spacing: -0.025em;
}

.period {
  font-size: 0.875rem;
  color: #64748b;
  margin-left: 0.25rem;
}

.plan-desc {
  color: #64748b;
  font-size: 0.875rem;
  margin: 0.75rem 0 0;
}

/* Features List */
.features-list {
  list-style: none;
  padding: 0;
  margin: 0 0 2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.features-list li {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.9375rem;
  color: #334155;
}

.features-list li.disabled {
  color: #94a3b8;
  text-decoration: line-through;
}

.check-icon {
  color: #0f172a;
  font-weight: bold;
}

.cross-icon {
  color: #cbd5e1;
}

/* Buttons */
.card-footer {
  margin-top: auto;
}

.btn {
  width: 100%;
  padding: 0.75rem 1rem;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background-color: #0f172a;
  color: white;
  border: 1px solid #0f172a;
}

.btn-primary:not(:disabled):hover {
  background-color: #1e293b;
  border-color: #1e293b;
}

.btn-outline {
  background-color: white;
  color: #0f172a;
  border: 1px solid #e2e8f0;
}

.btn-outline:not(:disabled):hover {
  background-color: #f8fafc;
  border-color: #cbd5e1;
}

/* Dialog Styles */
.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(2px);
}

.dialog {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 400px;
  overflow: hidden;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  animation: dialog-enter 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes dialog-enter {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #f1f5f9;
}

.dialog-header h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
}

.btn-close {
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  transition: all 0.2s;
  display: flex;
}

.btn-close:hover {
  color: #475569;
  background: #f1f5f9;
}

.dialog-body {
  padding: 1.5rem;
}

.dialog-desc {
  font-size: 0.875rem;
  color: #64748b;
  margin: 0 0 1rem;
  line-height: 1.5;
}

.promo-input-wrapper {
  margin-bottom: 0.5rem;
}

.promo-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
  outline: none;
  transition: all 0.2s;
  background: #f8fafc;
  text-transform: uppercase;
  letter-spacing: 1px;
  text-align: center;
  font-weight: 600;
}

.promo-input:focus {
  border-color: #3b82f6;
  background: white;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.promo-msg {
  font-size: 0.875rem;
  margin: 0.75rem 0 0;
  text-align: center;
  min-height: 1.25em;
}

.promo-msg.success { color: #059669; }
.promo-msg.error { color: #dc2626; }

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  background: #f8fafc;
  border-top: 1px solid #f1f5f9;
}

.btn-cancel {
  padding: 0.625rem 1.25rem;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  color: #475569;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-cancel:hover {
  background: #f1f5f9;
  color: #1e293b;
}

.btn-confirm {
  padding: 0.625rem 1.25rem;
  background: #0f172a;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.btn-confirm:hover:not(:disabled) {
  background: #1e293b;
  transform: translateY(-1px);
}

.btn-confirm:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 支付弹窗样式 */
.pay-dialog {
  max-width: 420px;
}

.pay-dialog-body {
  text-align: center;
  padding: 2rem 1.5rem;
}

.pay-tip {
  font-size: 1rem;
  color: #475569;
  margin: 0 0 1.5rem;
  font-weight: 500;
}

.qr-code-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
  margin: 0 0 1.5rem;
}

.qr-code-canvas {
  max-width: 100%;
  height: auto;
}

.order-info {
  margin: 1.5rem 0;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
}

.order-amount {
  font-size: 1.125rem;
  color: #0f172a;
  margin: 0 0 0.5rem;
}

.order-amount strong {
  color: #dc2626;
  font-size: 1.25rem;
}

.order-no {
  font-size: 0.875rem;
  color: #64748b;
  margin: 0;
  word-break: break-all;
}

.countdown-tip {
  font-size: 0.875rem;
  color: #64748b;
  margin: 1rem 0 0;
}

.countdown-tip.expired {
  color: #dc2626;
  font-weight: 500;
}

/* Responsive */
@media (max-width: 640px) {
  .page-title {
    font-size: 2rem;
  }
  
  .pay-dialog {
    width: 95%;
  }
  
  .qr-code-wrapper {
    padding: 0.5rem;
  }
}
</style>






