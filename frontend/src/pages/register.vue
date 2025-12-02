<template>
  <v-container class="fill-height" fluid>
    <v-row justify="center" align="center">
      <v-col cols="12" sm="8" md="4">
        <v-card>
          <v-card-title class="text-h5">注册</v-card-title>
          <v-card-text>
            <v-form ref="registerForm" @submit.prevent="onSubmit">
              <v-text-field v-model="form.username" label="用户名" prepend-icon="mdi-account" :rules="[rules.required]"></v-text-field>
              <v-text-field v-model="form.password" label="密码" prepend-icon="mdi-lock" type="password" :rules="[rules.required]"></v-text-field>
              <v-btn type="submit" color="primary" class="mt-4" block>注册</v-btn>
            </v-form>
            <div class="mt-5 text-center">
              已有账号？<span class="link-text" @click="goLogin">去登录</span>
            </div>
          </v-card-text>
        </v-card>
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
    const form = reactive({ username: '', password: '' })
    const rules = { required: (v: string) => !!v || '此项为必填' }

    const onSubmit = async () => {
      try {
        const res = await request.post('/user/register', form)
        if (res.data.code === 0) {
          alert('注册成功，请登录')
          router.push('/login')
        } else {
          alert(res.data.msg)
        }
      } catch (err: any) {
        alert(err.response?.data?.msg || '注册失败')
      }
    }

    const goLogin = () => { router.push('/login') }

    return { form, rules, registerForm, onSubmit, goLogin }
  }
})
</script>

<style scoped>
.link-text { color: #1976d2; cursor: pointer; text-decoration: underline; }
</style>
