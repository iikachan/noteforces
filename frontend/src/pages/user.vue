<template>
  <v-app>
    <NavDrawer title="用户设置" />

    <v-main>
      <v-container>
        <!-- 用户信息卡片 -->
        <v-card max-width="600" class="mx-auto mt-8">
          <v-card-title class="text-h6 text-center">用户信息</v-card-title>
          <v-card-text>
            <v-text-field
              label="用户名"
              v-model="user.username"
              readonly
            />
            <v-text-field
              label="角色"
              v-model="user.role"
              readonly
            />
          </v-card-text>
        </v-card>

        <!-- 修改密码卡片 -->
        <v-card max-width="600" class="mx-auto mt-4">
          <v-card-title class="text-h6 text-center">修改密码</v-card-title>
          <v-card-text>
            <v-form ref="passwordForm">
              <v-text-field
                label="旧密码"
                v-model="form.oldPassword"
                type="password"
                :rules="[rules.required]"
                required
              />
              <v-text-field
                label="新密码"
                v-model="form.newPassword"
                type="password"
                :rules="[rules.required, rules.password]"
                required
              />
              <v-text-field
                label="确认新密码"
                v-model="form.confirmPassword"
                type="password"
                :rules="[rules.required, rules.confirmPassword]"
                required
              />
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-btn color="primary" block @click="onSubmit">修改密码</v-btn>
          </v-card-actions>
        </v-card>

        <!-- 顶部提示 -->
        <v-snackbar
          v-model="snackbar.show"
          :color="snackbar.color"
          timeout="3000"
          location="top"
          elevation="2"
          rounded
        >
          {{ snackbar.message }}
        </v-snackbar>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import axios from '@/plugins/axios'
import NavDrawer from '@/components/NavDrawer.vue'

interface User {
  username: string
  role: string
}

const user = ref<User>({ username: '', role: '' })
const form = reactive({ oldPassword: '', newPassword: '', confirmPassword: '' })
const snackbar = reactive({ show: false, message: '', color: 'success' })
const passwordForm = ref()

const rules = {
  required: (v: string) => !!v || '此项为必填',
  password: (v: string) => v.length >= 6 || '密码至少6位',
  confirmPassword: (v: string) => v === form.newPassword || '两次输入的密码不一致'
}

function showMessage(message: string, color: string = 'success') {
  snackbar.message = message
  snackbar.color = color
  snackbar.show = true
}

async function loadUser() {
  try {
    const res = await axios.get('/user/me')
    if (res.data.code === 0) user.value = res.data.data
    else showMessage(res.data.msg, 'error')
  } catch (err: any) {
    showMessage(err.response?.data?.msg || '获取用户信息失败', 'error')
  }
}

async function onSubmit() {
  if (!passwordForm.value?.validate?.()) return
  try {
    const res = await axios.post('/user/changePassword', {
      oldPassword: form.oldPassword,
      newPassword: form.newPassword
    })
    if (res.data.code === 0) {
      showMessage('密码修改成功', 'success')
      form.oldPassword = ''
      form.newPassword = ''
      form.confirmPassword = ''
    } else {
      showMessage(res.data.msg, 'error')
    }
  } catch (err: any) {
    showMessage(err.response?.data?.msg || '修改密码失败', 'error')
  }
}

onMounted(loadUser)
</script>

<style scoped>
.v-card { padding: 16px; }
</style>
