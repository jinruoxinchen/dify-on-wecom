<template>
  <div class="config-container">
    <el-card class="config-card">
      <template #header>
        <div class="card-header">
          <h2>微信企业级智能客服配置</h2>
        </div>
      </template>
      
      <!-- Dify配置区域 -->
      <el-form :model="difyConfig" label-width="120px" class="config-form">
        <h3>Dify配置</h3>
        <el-form-item label="API Key">
          <el-input v-model="difyConfig.apiKey" placeholder="请输入Dify API Key" show-password />
        </el-form-item>
        <el-form-item label="API URL">
          <el-input v-model="difyConfig.apiUrl" placeholder="请输入Dify API URL" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveDifyConfig">保存Dify配置</el-button>
        </el-form-item>
      </el-form>
      
      <el-divider />
      
      <!-- 企业微信配置区域 -->
      <el-form :model="wecomConfig" label-width="120px" class="config-form">
        <h3>企业微信配置</h3>
        <el-form-item label="Access Token">
          <el-input v-model="wecomConfig.accessToken" placeholder="请输入企业微信Access Token" show-password />
        </el-form-item>
        <el-form-item label="Open KFID">
          <el-input v-model="wecomConfig.openKfid" placeholder="请输入企业微信Open KFID" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveWecomConfig">保存企业微信配置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 操作结果提示 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="30%"
      center
    >
      <span>{{ dialogMessage }}</span>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'

export default {
  name: 'ConfigApp',
  setup() {
    // Dify配置
    const difyConfig = reactive({
      apiKey: '',
      apiUrl: ''
    })
    
    // 企业微信配置
    const wecomConfig = reactive({
      accessToken: '',
      openKfid: ''
    })
    
    // 对话框状态
    const dialogVisible = ref(false)
    const dialogTitle = ref('')
    const dialogMessage = ref('')
    
    // 显示提示对话框
    const showDialog = (title, message) => {
      dialogTitle.value = title
      dialogMessage.value = message
      dialogVisible.value = true
    }
    
    // 加载配置
    const loadConfig = async () => {
      try {
        const response = await axios.get('/api/config')
        if (response.data.success) {
          const { dify, wecom } = response.data.data
          
          if (dify) {
            difyConfig.apiKey = dify.apiKey || ''
            difyConfig.apiUrl = dify.apiUrl || ''
          }
          
          if (wecom) {
            wecomConfig.accessToken = wecom.accessToken || ''
            wecomConfig.openKfid = wecom.openKfid || ''
          }
        }
      } catch (error) {
        console.error('加载配置失败:', error)
      }
    }
    
    // 保存Dify配置
    const saveDifyConfig = async () => {
      try {
        const response = await axios.post('/api/config/dify', difyConfig)
        if (response.data.success) {
          showDialog('成功', 'Dify配置保存成功')
        } else {
          showDialog('错误', response.data.message || 'Dify配置保存失败')
        }
      } catch (error) {
        showDialog('错误', '保存失败，请检查网络连接')
        console.error('保存Dify配置失败:', error)
      }
    }
    
    // 保存企业微信配置
    const saveWecomConfig = async () => {
      try {
        const response = await axios.post('/api/config/wecom', wecomConfig)
        if (response.data.success) {
          showDialog('成功', '企业微信配置保存成功')
        } else {
          showDialog('错误', response.data.message || '企业微信配置保存失败')
        }
      } catch (error) {
        showDialog('错误', '保存失败，请检查网络连接')
        console.error('保存企业微信配置失败:', error)
      }
    }
    
    // 组件挂载时加载配置
    onMounted(() => {
      loadConfig()
    })
    
    return {
      difyConfig,
      wecomConfig,
      dialogVisible,
      dialogTitle,
      dialogMessage,
      saveDifyConfig,
      saveWecomConfig
    }
  }
}
</script>

<style>
.config-container {
  max-width: 800px;
  margin: 20px auto;
  padding: 20px;
}

.config-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.config-form {
  margin-top: 20px;
}

.el-divider {
  margin: 30px 0;
}
</style>