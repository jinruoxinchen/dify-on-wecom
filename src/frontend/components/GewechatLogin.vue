<template>
  <div class="gewechat-login-container">
    <div class="card">
      <div class="card-header">
        <h2>微信登录</h2>
      </div>
      <div class="card-body">
        <div v-if="loginStatus === 'initial' || loginStatus === 'loading'" class="qrcode-container">
          <div v-if="loginStatus === 'loading'" class="loading-overlay">
            <div class="spinner"></div>
            <p>加载中...</p>
          </div>
          <div v-if="qrcodeUrl" class="qrcode-wrapper">
            <img :src="qrcodeUrl" alt="登录二维码" />
            <p class="qrcode-tip">请使用微信扫描二维码登录</p>
          </div>
          <div v-else class="qrcode-placeholder">
            <button @click="getLoginQrcode" class="get-qrcode-btn">获取登录二维码</button>
          </div>
        </div>

        <div v-if="loginStatus === 'scanning'" class="status-message">
          <div class="status-icon scanning"></div>
          <p>请在微信中确认登录</p>
        </div>

        <div v-if="loginStatus === 'success'" class="status-message success">
          <div class="status-icon success"></div>
          <p>登录成功！</p>
          <div class="account-info" v-if="accountInfo">
            <div class="avatar">
              <img :src="accountInfo.avatar" alt="头像" v-if="accountInfo.avatar" />
              <div class="avatar-placeholder" v-else></div>
            </div>
            <div class="info">
              <p class="nickname">{{ accountInfo.nickname || '未知用户' }}</p>
              <p class="wxid">{{ accountInfo.wxid || '' }}</p>
            </div>
          </div>
        </div>

        <div v-if="loginStatus === 'error'" class="status-message error">
          <div class="status-icon error"></div>
          <p>{{ errorMessage || '登录失败，请重试' }}</p>
          <button @click="resetLogin" class="retry-btn">重试</button>
        </div>

        <div v-if="loginStatus === 'timeout'" class="status-message timeout">
          <div class="status-icon timeout"></div>
          <p>二维码已过期，请重新获取</p>
          <button @click="getLoginQrcode" class="retry-btn">刷新二维码</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'GewechatLogin',
  data() {
    return {
      qrcodeUrl: '',
      loginStatus: 'initial', // initial, loading, scanning, success, error, timeout
      pollTimer: null,
      token: '',
      errorMessage: '',
      accountInfo: null,
    };
  },
  mounted() {
    this.getLoginQrcode();
  },
  beforeDestroy() {
    this.clearPollTimer();
  },
  methods: {
    // 获取登录二维码
    async getLoginQrcode() {
      this.loginStatus = 'loading';
      this.errorMessage = '';
      this.clearPollTimer();

      try {
        // API请求获取二维码
        const response = await fetch('/api/gewechat/login/qrcode', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        const data = await response.json();

        if (response.ok && data.success) {
          this.qrcodeUrl = data.qrcodeUrl;
          this.token = data.token; // 保存token用于后续状态查询
          this.loginStatus = 'initial';
          this.startPollingLoginStatus();
        } else {
          this.loginStatus = 'error';
          this.errorMessage = data.message || '获取二维码失败';
        }
      } catch (error) {
        console.error('获取二维码出错:', error);
        this.loginStatus = 'error';
        this.errorMessage = '网络错误，请检查网络连接';
      }
    },

    // 开始轮询登录状态
    startPollingLoginStatus() {
      this.pollTimer = setInterval(async () => {
        await this.checkLoginStatus();
      }, 2000); // 每2秒检查一次
    },

    // 清除轮询定时器
    clearPollTimer() {
      if (this.pollTimer) {
        clearInterval(this.pollTimer);
        this.pollTimer = null;
      }
    },

    // 检查登录状态
    async checkLoginStatus() {
      if (!this.token) return;

      try {
        const response = await fetch(`/api/gewechat/login/status?token=${this.token}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        const data = await response.json();

        if (response.ok && data.success) {
          // 根据状态码更新界面
          switch (data.status) {
            case 0: // 未扫码
              this.loginStatus = 'initial';
              break;
            case 1: // 已扫码，等待确认
              this.loginStatus = 'scanning';
              break;
            case 2: // 已确认，登录成功
              this.loginStatus = 'success';
              this.accountInfo = data.accountInfo;
              this.clearPollTimer();
              this.saveLoginConfig(data.config);
              this.$emit('login-success', data.config);
              break;
            case 3: // 二维码已过期
              this.loginStatus = 'timeout';
              this.clearPollTimer();
              break;
            default:
              this.loginStatus = 'error';
              this.errorMessage = '未知状态';
              break;
          }
        } else {
          this.loginStatus = 'error';
          this.errorMessage = data.message || '获取登录状态失败';
          this.clearPollTimer();
        }
      } catch (error) {
        console.error('检查登录状态出错:', error);
        // 网络错误不终止轮询，但更新界面状态
        this.loginStatus = 'error';
        this.errorMessage = '网络错误，请检查网络连接';
      }
    },

    // 保存登录配置
    async saveLoginConfig(config) {
      try {
        const response = await fetch('/api/gewechat/config/save', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(config),
        });

        const data = await response.json();
        if (!response.ok || !data.success) {
          console.error('保存配置失败:', data.message);
        }
      } catch (error) {
        console.error('保存配置出错:', error);
      }
    },

    // 重置登录状态
    resetLogin() {
      this.loginStatus = 'initial';
      this.qrcodeUrl = '';
      this.token = '';
      this.errorMessage = '';
      this.accountInfo = null;
      this.clearPollTimer();
      this.getLoginQrcode();
    },
  },
};
</script>

<style scoped>
.gewechat-login-container {
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
  padding: 20px;
}

.card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.card-header {
  background: #07c160;
  color: white;
  padding: 15px 20px;
  text-align: center;
}

.card-header h2 {
  margin: 0;
  font-weight: 500;
  font-size: 18px;
}

.card-body {
  padding: 20px;
}

.qrcode-container {
  position: relative;
  width: 200px;
  height: 200px;
  margin: 0 auto 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #e6e6e6;
  border-radius: 4px;
}

.qrcode-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.qrcode-wrapper img {
  max-width: 180px;
  max-height: 180px;
}

.qrcode-tip {
  margin-top: 10px;
  font-size: 12px;
  color: #999;
  text-align: center;
}

.qrcode-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(7, 193, 96, 0.3);
  border-radius: 50%;
  border-top-color: #07c160;
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.get-qrcode-btn, .retry-btn {
  background: #07c160;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}

.get-qrcode-btn:hover, .retry-btn:hover {
  background: #06ae56;
}

.status-message {
  text-align: center;
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.status-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background-size: 30px;
  background-position: center;
  background-repeat: no-repeat;
}

.status-icon.scanning {
  background-color: #ffd166;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='white' viewBox='0 0 24 24'%3E%3Cpath d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z'/%3E%3C/svg%3E");
}

.status-icon.success {
  background-color: #07c160;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='white' viewBox='0 0 24 24'%3E%3Cpath d='M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z'/%3E%3C/svg%3E");
}

.status-icon.error, .status-icon.timeout {
  background-color: #ff6b6b;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='white' viewBox='0 0 24 24'%3E%3Cpath d='M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12 19 6.41z'/%3E%3C/svg%3E");
}

.status-message p {
  margin: 5px 0;
  font-size: 16px;
}

.status-message.success p {
  color: #07c160;
}

.status-message.error p {
  color: #ff6b6b;
}

.status-message.timeout p {
  color: #ff9900;
}

.account-info {
  display: flex;
  align-items: center;
  margin-top: 15px;
  padding: 10px;
  background: #f8f8f8;
  border-radius: 8px;
  width: 100%;
}

.avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  overflow: hidden;
  margin-right: 10px;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  background-color: #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.info {
  flex: 1;
  overflow: hidden;
}

.nickname {
  font-weight: bold;
  margin: 0 0 5px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.wxid {
  font-size: 12px;
  color: #999;
  margin: 0;
}
</style>
