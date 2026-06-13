import Vue from 'vue';
import VueI18n from 'vue-i18n';
import en from './en';
import de from './de';
import vi from './vi';
import ptBR from './pt_BR';

Vue.use(VueI18n);

export const supportedLanguages = Object.freeze([
  { code: 'en', labelKey: 'language.en' },
  { code: 'de', labelKey: 'language.de' },
  { code: 'vi', labelKey: 'language.vi' },
  { code: 'pt_BR', labelKey: 'language.pt_BR' },
]);

export const getLanguageLabelKey = (lang) => {
  const match = supportedLanguages.find((item) => item.code === lang);
  return match ? match.labelKey : 'language.en';
};

// Get language setting from local storage, if not available use browser language or default language
const getDefaultLanguage = () => {
  const savedLang = localStorage.getItem('userLanguage');
  if (savedLang) {
    return savedLang;
  }
  const browserLang = navigator.language || navigator.userLanguage;
  if (browserLang.indexOf('de') === 0) {
    return 'de';
  }
  if (browserLang.indexOf('vi') === 0) {
    return 'vi';
  }
  if (browserLang === 'pt-BR' || browserLang === 'pt') {
    return 'pt_BR';
  }
  return 'en';
};

const i18n = new VueI18n({
  locale: getDefaultLanguage(),
  fallbackLocale: 'en',
  messages: {
    'en': en,
    'de': de,
    'vi': vi,
    'pt_BR': ptBR,
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
