import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: '',
    userInfo: {}
  }),
  actions: {
    setToken(token) {
      this.token = token
    },
    setUserInfo(info) {
      this.userInfo = info
    },
    logout() {
      this.token = ''
      this.userInfo = {}
    }
  }
})