import Vue from 'vue';
import VueI18n from 'vue-i18n';
import en from './en';

Vue.use(VueI18n);

// Get language setting from local storage, if not available use browser language or default language
const getDefaultLanguage = () => {
  const savedLang = localStorage.getItem('userLanguage');
  if (savedLang) {
    return savedLang;
  }
  return 'en';
};

const i18n = new VueI18n({
  locale: getDefaultLanguage(),
  fallbackLocale: 'en',
  messages: {
    'en': en
  }
});

export default i18n;

// Provide a method to switch language
export const changeLanguage = (lang) => {
  i18n.locale = lang;
  localStorage.setItem('userLanguage', lang);
  // Notify components that language has changed
  Vue.prototype.$eventBus.$emit('languageChanged', lang);
};