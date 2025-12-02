<template>
  <v-container class="fill-height" fluid>
    <v-row justify="center" align="center">
      <v-col cols="12" sm="8" md="4">
        <v-card>
          <v-card-title class="text-h5 text-center">注册</v-card-title>
          <v-card-text>
            <v-form ref="registerForm">
              <v-text-field
                v-model="form.username"
                label="用户名"
                prepend-icon="mdi-account"
                :rules="[rules.required]"
              ></v-text-field>
              <v-text-field
                v-model="form.password"
                label="密码"
                prepend-icon="mdi-lock"
                type="password"
                :rules="[rules.required, rules.password]"
              ></v-text-field>
              <v-text-field
                v-model="form.confirmPassword"
                label="确认密码"
                prepend-icon="mdi-lock-check"
                type="password"
                :rules="[rules.required, rules.confirmPassword]"
              ></v-text-field>
              <v-btn
                color="primary"
                class="mt-4"
                block
                @click="onSubmit"
              >注册</v-btn>
            </v-form>
            <div class="mt-5 text-center">
              已有账号？<span class="link-text" @click="goLogin">去登录</span>
            </div>
          </v-card-text>
        </v-card>

        <!-- 顶部弹窗 -->
        <v-snackbar
          v-model="snackbar.show"
          :color="snackbar.color"
          timeout="2000"
          location="top"
          elevation="2"
          rounded
        >
          {{ snackbar.message }}
        </v-snackbar>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import request from '@/plugins/axios'

export default defineComponent({
  setup() {
    const router = useRouter()
    const registerForm = ref()
    const form = reactive({ username: '', password: '', confirmPassword: '' })
    const snackbar = reactive({ show: false, message: '', color: 'success' })

    const rules = {
      required: (v: string) => !!v || '此项为必填',
      password: (v: string) => v.length >= 6 || '密码至少6位',
      confirmPassword: (v: string) => v === form.password || '两次输入的密码不一致'
    }

    const showSnackbar = (message: string, color: string = 'success') => {
      snackbar.message = message
      snackbar.color = color
      snackbar.show = true
    }

    const onSubmit = async () => {
      if (!registerForm.value?.validate?.()) return
      try {
        const res = await request.post('/user/register', {
          username: form.username,
          password: form.password
        })
        if (res.data.code === 0) {
          showSnackbar('注册成功，正在跳转登录', 'success')
          setTimeout(() => router.push('/login'), 1000)
        } else {
          showSnackbar(res.data.msg, 'error')
        }
      } catch (err: any) {
        showSnackbar(err.response?.data?.msg || '注册失败', 'error')
      }
    }

    const goLogin = () => { router.push('/login') }

    return { form, rules, registerForm, onSubmit, goLogin, snackbar }
  }
})
</script>

<style scoped>
.link-text { color: #1976d2; cursor: pointer; text-decoration: underline; }
</style>
