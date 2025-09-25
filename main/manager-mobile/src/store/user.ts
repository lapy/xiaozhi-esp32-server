import type { UserInfo } from '@/api/auth'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  getUserInfo as _getUserInfo,
} from '@/api/auth'

// Initialize state
const userInfoState: UserInfo & { avatar?: string, token?: string } = {
  id: 0,
  username: '',
  realName: '',
  email: '',
  mobile: '',
  status: 0,
  superAdmin: 0,
  avatar: '/static/images/default-avatar.png',
  token: '',
}

export const useUserStore = defineStore(
  'user',
  () => {
    // Define user info
    const userInfo = ref<UserInfo & { avatar?: string, token?: string }>({ ...userInfoState })
    // Set user info
    const setUserInfo = (val: UserInfo & { avatar?: string, token?: string }) => {
      console.log('Set user info', val)
      // If avatar is empty, use default avatar
      if (!val.avatar) {
        val.avatar = userInfoState.avatar
      }
      else {
        val.avatar = 'https://oss.laf.run/ukw0y1-site/avatar.jpg?feige'
      }
      userInfo.value = val
    }
    const setUserAvatar = (avatar: string) => {
      userInfo.value.avatar = avatar
      console.log('Set user avatar', avatar)
      console.log('userInfo', userInfo.value)
    }
    // Delete user info
    const removeUserInfo = () => {
      userInfo.value = { ...userInfoState }
      uni.removeStorageSync('userInfo')
      uni.removeStorageSync('token')
    }
    /**
     * Get user info
     */
    const getUserInfo = async () => {
      const userData = await _getUserInfo()
      const userInfoWithExtras = {
        ...userData,
        avatar: userInfoState.avatar,
        token: uni.getStorageSync('token') || '',
      }
      setUserInfo(userInfoWithExtras)
      uni.setStorageSync('userInfo', userInfoWithExtras)
      // TODO Can add method to get user routes here, dynamically generate routes based on user role
      return userInfoWithExtras
    }
    /**
     * Logout and delete user info
     */
    const logout = async () => {
      removeUserInfo()
    }

    return {
      userInfo,
      getUserInfo,
      setUserInfo,
      setUserAvatar,
      logout,
      removeUserInfo,
    }
  },
  {
    persist: true,
  },
)
