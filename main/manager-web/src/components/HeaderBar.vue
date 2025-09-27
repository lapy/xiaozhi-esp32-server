<template>
  <el-header class="header">
    <div class="header-container">
      <!-- Left side elements -->
      <div class="header-left" @click="goHome">
        <img loading="lazy" alt="" src="@/assets/xiaozhi-logo.png" class="logo-img" />
      </div>

      <!-- Center navigation menu -->
      <div class="header-center">
        <div class="equipment-management"
          :class="{ 'active-tab': $route.path === '/home' || $route.path === '/role-config' || $route.path === '/device-management' }"
          @click="goHome">
          <img loading="lazy" alt="" src="@/assets/header/robot.png"
            :style="{ filter: $route.path === '/home' || $route.path === '/role-config' || $route.path === '/device-management' ? 'brightness(0) invert(1)' : 'None' }" />
          <span class="nav-text">{{ $t('header.smartManagement') }}</span>
        </div>
        <div v-if="isSuperAdmin" class="equipment-management" :class="{ 'active-tab': $route.path === '/model-config' }"
          @click="goModelConfig">
          <img loading="lazy" alt="" src="@/assets/header/model_config.png"
            :style="{ filter: $route.path === '/model-config' ? 'brightness(0) invert(1)' : 'None' }" />
          <span class="nav-text">{{ $t('header.modelConfig') }}</span>
        </div>
        <div v-if="isSuperAdmin" class="equipment-management"
          :class="{ 'active-tab': $route.path === '/user-management' }" @click="goUserManagement">
          <img loading="lazy" alt="" src="@/assets/header/user_management.png"
            :style="{ filter: $route.path === '/user-management' ? 'brightness(0) invert(1)' : 'None' }" />
          <span class="nav-text">{{ $t('header.userManagement') }}</span>
        </div>
        <div v-if="isSuperAdmin" class="equipment-management"
          :class="{ 'active-tab': $route.path === '/ota-management' }" @click="goOtaManagement">
          <img loading="lazy" alt="" src="@/assets/header/firmware_update.png"
            :style="{ filter: $route.path === '/ota-management' ? 'brightness(0) invert(1)' : 'None' }" />
          <span class="nav-text">{{ $t('header.otaManagement') }}</span>
        </div>
        <el-dropdown v-if="isSuperAdmin" trigger="click" class="equipment-management more-dropdown"
          :class="{ 'active-tab': $route.path === '/dict-management' || $route.path === '/params-management' || $route.path === '/provider-management' || $route.path === '/server-side-management' || $route.path === '/agent-template-management' }"
          @visible-change="handleParamDropdownVisibleChange">
          <span class="el-dropdown-link">
            <img loading="lazy" alt="" src="@/assets/header/param_management.png"
              :style="{ filter: $route.path === '/dict-management' || $route.path === '/params-management' || $route.path === '/provider-management' || $route.path === '/server-side-management' || $route.path === '/agent-template-management' ? 'brightness(0) invert(1)' : 'None' }" />
            <span class="nav-text">{{ $t('header.paramDictionary') }}</span>
            <i class="el-icon-arrow-down el-icon--right" :class="{ 'rotate-down': paramDropdownVisible }"></i>
          </span>
          <el-dropdown-menu slot="dropdown">
            <el-dropdown-item @click.native="goParamManagement">
              {{ $t('header.paramManagement') }}
            </el-dropdown-item>
            <el-dropdown-item @click.native="goDictManagement">
              {{ $t('header.dictManagement') }}
            </el-dropdown-item>
            <el-dropdown-item @click.native="goProviderManagement">
              {{ $t('header.providerManagement') }}
            </el-dropdown-item>
            <el-dropdown-item @click.native="goAgentTemplateManagement">
              {{ $t('header.agentTemplate') }}
            </el-dropdown-item>
            <el-dropdown-item @click.native="goServerSideManagement">
              {{ $t('header.serverSideManagement') }}
            </el-dropdown-item>
          </el-dropdown-menu>
        </el-dropdown>
      </div>

      <!-- Right side elements -->
      <div class="header-right">
        <div class="search-container" v-if="$route.path === '/home' && !(isSuperAdmin && isSmallScreen)">
          <el-input v-model="search" :placeholder="$t('header.searchPlaceholder')" class="custom-search-input"
            @keyup.enter.native="handleSearch">
            <i slot="suffix" class="el-icon-search search-icon" @click="handleSearch"></i>
          </el-input>
        </div>

        <!-- Language switching dropdown menu -->
        <el-dropdown trigger="click" class="language-dropdown" @visible-change="handleLanguageDropdownVisibleChange">
          <span class="el-dropdown-link">
            <span class="current-language-text">{{ currentLanguageText }}</span>
            <i class="el-icon-arrow-down el-icon--right" :class="{ 'rotate-down': languageDropdownVisible }"></i>
          </span>
          <el-dropdown-menu slot="dropdown">
            <el-dropdown-item @click.native="changeLanguage('zh_CN')">
              {{ $t('language.zhCN') }}
            </el-dropdown-item>
            <el-dropdown-item @click.native="changeLanguage('zh_TW')">
              {{ $t('language.zhTW') }}
            </el-dropdown-item>
            <el-dropdown-item @click.native="changeLanguage('en')">
              {{ $t('language.en') }}
            </el-dropdown-item>
          </el-dropdown-menu>
        </el-dropdown>

        <img loading="lazy" alt="" src="@/assets/home/avatar.png" class="avatar-img" />
        <el-dropdown trigger="click" class="user-dropdown" @visible-change="handleUserDropdownVisibleChange">
          <span class="el-dropdown-link">
            {{ userInfo.username || 'Loading...' }}
            <i class="el-icon-arrow-down el-icon--right" :class="{ 'rotate-down': userDropdownVisible }"></i>
          </span>
          <el-dropdown-menu slot="dropdown">
            <el-dropdown-item @click.native="showChangePasswordDialog">{{ $t('header.changePassword')
              }}</el-dropdown-item>
            <el-dropdown-item @click.native="handleLogout">{{ $t('header.logout') }}</el-dropdown-item>
          </el-dropdown-menu>
        </el-dropdown>
      </div>
    </div>

    <!-- Change password dialog -->
    <ChangePasswordDialog v-model="isChangePasswordDialogVisible" />
  </el-header>
</template>

<script>
import userApi from '@/apis/module/user';
import i18n, { changeLanguage } from '@/i18n';
import { mapActions, mapGetters } from 'vuex';
import ChangePasswordDialog from './ChangePasswordDialog.vue'; // Import change password dialog component

export default {
  name: 'HeaderBar',
  components: {
    ChangePasswordDialog
  },
  props: ['devices'],  // Receive parent component device list
  data() {
    return {
      search: '',
      userInfo: {
        username: '',
        mobile: ''
      },
      isChangePasswordDialogVisible: false, // Control change password dialog display
      userDropdownVisible: false,
      paramDropdownVisible: false,
      languageDropdownVisible: false,
      isSmallScreen: false
    }
  },
  computed: {
    ...mapGetters(['getIsSuperAdmin']),
    isSuperAdmin() {
      return this.getIsSuperAdmin;
    },
    // Get current language
    currentLanguage() {
      return i18n.locale || 'en';
    },
    // Get current language display text
    currentLanguageText() {
      const currentLang = this.currentLanguage;
      switch (currentLang) {
        case 'zh_CN':
          return this.$t('language.zhCN');
        case 'zh_TW':
          return this.$t('language.zhTW');
        case 'en':
          return this.$t('language.en');
        default:
          return this.$t('language.en');
      }
    }
  },
  mounted() {
    this.fetchUserInfo();
    this.checkScreenSize();
    window.addEventListener('resize', this.checkScreenSize);
  },
  // Remove event listener
  beforeDestroy() {
    window.removeEventListener('resize', this.checkScreenSize);
  },
  methods: {
    goHome() {
      // Navigate to home page
      this.$router.push('/home')
    },
    goUserManagement() {
      this.$router.push('/user-management')
    },
    goModelConfig() {
      this.$router.push('/model-config')
    },
    goParamManagement() {
      this.$router.push('/params-management')
    },
    goOtaManagement() {
      this.$router.push('/ota-management')
    },
    goDictManagement() {
      this.$router.push('/dict-management')
    },
    goProviderManagement() {
      this.$router.push('/provider-management')
    },
    goServerSideManagement() {
      this.$router.push('/server-side-management')
    },
    // Add default role template management navigation method
    goAgentTemplateManagement() {
      this.$router.push('/agent-template-management')
    },
    // Get user information
    fetchUserInfo() {
      userApi.getUserInfo(({ data }) => {
        this.userInfo = data.data
        if (data.data.superAdmin !== undefined) {
          this.$store.commit('setUserInfo', data.data);
        }
      })
    },
    checkScreenSize() {
      this.isSmallScreen = window.innerWidth <= 1386;
    },
    // Handle search
    handleSearch() {
      const searchValue = this.search.trim();

      // If search content is empty, trigger reset event
      if (!searchValue) {
        this.$emit('search-reset');
        return;
      }

      try {
        // Create case-insensitive regular expression
        const regex = new RegExp(searchValue, 'i');
        // Trigger search event, pass regular expression to parent component
        this.$emit('search', regex);
      } catch (error) {
        console.error('Regular expression creation failed:', error);
        this.$message.error({
          message: this.$t('message.error'),
          showClose: true
        });
      }
    },
    // Show change password dialog
    showChangePasswordDialog() {
      this.isChangePasswordDialogVisible = true;
    },
    // Logout
    async handleLogout() {
      try {
        // Call Vuex logout action
        await this.logout();
        this.$message.success({
          message: this.$t('message.success'),
          showClose: true
        });
      } catch (error) {
        console.error('Logout failed:', error);
        this.$message.error({
          message: this.$t('message.error'),
          showClose: true
        });
      }
    },
    handleUserDropdownVisibleChange(visible) {
      this.userDropdownVisible = visible;
    },
    // Listen to second dropdown menu visibility change
    handleParamDropdownVisibleChange(visible) {
      this.paramDropdownVisible = visible;
    },
    // Listen to language dropdown menu visibility change
    handleLanguageDropdownVisibleChange(visible) {
      this.languageDropdownVisible = visible;
    },
    // Switch language
    changeLanguage(lang) {
      changeLanguage(lang);
      this.languageDropdownVisible = false;
      this.$message.success({
        message: this.$t('message.success'),
        showClose: true
      });
    },

    // Use mapActions to introduce Vuex logout action
    ...mapActions(['logout'])
  }
}
</script>

<style lang="scss" scoped>
.header {
  background: #f6fcfe66;
  border: 1px solid #fff;
  height: 63px !important;
  min-width: 900px;
  /* Set minimum width to prevent excessive compression */
  overflow: visible;
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  padding: 0 10px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 120px;
}

.logo-img {
  width: 42px;
  height: 42px;
}

.brand-img {
  height: 20px;
}

.header-center {
  display: flex;
  align-items: center;
  gap: 25px;
  position: absolute;
  left: 44%;
  transform: translateX(-50%);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 7px;
  min-width: 300px;
  justify-content: flex-end;
}

.equipment-management {
  height: 30px;
  border-radius: 15px;
  background: #deeafe;
  display: flex;
  justify-content: center;
  font-size: 14px;
  font-weight: 500;
  gap: 7px;
  color: #3d4566;
  margin-left: 1px;
  align-items: center;
  transition: all 0.3s ease;
  cursor: pointer;
  flex-shrink: 0;
  /* Prevent navigation buttons from being compressed */
  padding: 0 15px;
  position: relative;
}

.equipment-management.active-tab {
  background: #5778ff !important;
  color: #fff !important;
}

.equipment-management img {
  width: 15px;
  height: 13px;
}

.search-container {
  margin-right: 5px;
  flex: 0.9;
  min-width: 60px;
  max-width: none;
}

.custom-search-input>>>.el-input__inner {
  height: 18px;
  border-radius: 9px;
  background-color: #fff;
  border: 1px solid #e4e6ef;
  padding-left: 8px;
  font-size: 9px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  width: 100%;
}

.search-icon {
  cursor: pointer;
  color: #909399;
  margin-right: 3px;
  font-size: 9px;
  line-height: 18px;
}

.custom-search-input::v-deep .el-input__suffix-inner {
  display: flex;
  align-items: center;
  height: 100%;
}

.avatar-img {
  width: 21px;
  height: 21px;
  flex-shrink: 0;
}

.user-dropdown {
  flex-shrink: 0;
}

.language-dropdown {
  flex-shrink: 0;
  margin-right: 5px;
}

.current-language-text {
  margin-left: 4px;
  margin-right: 4px;
  font-size: 12px;
  color: #3d4566;
}

.more-dropdown {
  padding-right: 20px;
}

.more-dropdown .el-dropdown-link {
  display: flex;
  align-items: center;
  gap: 7px;
}

.rotate-down {
  transform: rotate(180deg);
  transition: transform 0.3s ease;
}

.el-icon-arrow-down {
  transition: transform 0.3s ease;
}

/* Navigation text styles - support international text line breaks */
.nav-text {
  white-space: normal;
  text-align: center;
  max-width: 80px;
  line-height: 1.2;
}

/* Responsive adjustments */
@media (max-width: 1200px) {
  .header-center {
    gap: 14px;
  }

  .equipment-management {
    width: 79px;
    font-size: 9px;
  }
}

.equipment-management.more-dropdown {
  position: relative;
}

.equipment-management.more-dropdown .el-dropdown-menu {
  position: absolute;
  right: 0;
  min-width: 120px;
  margin-top: 5px;
}

.el-dropdown-menu__item {
  min-width: 60px;
  padding: 8px 20px;
  font-size: 14px;
  color: #606266;
  white-space: nowrap;
}
</style>