import 'element-ui/lib/theme-chalk/index.css';
import 'normalize.css/normalize.css'; // A modern alternative to CSS resets
import Vue from 'vue';
import ElementUI from 'element-ui';
import App from './App.vue';
import router from './router';
import store from './store';
import i18n from './i18n';
import './styles/global.scss';
import { register as registerServiceWorker } from './registerServiceWorker';

// Create event bus for component communication
Vue.prototype.$eventBus = new Vue();

Vue.use(ElementUI, { locale: 'en' });

Vue.config.productionTip = false

// Register Service Worker
registerServiceWorker();

// Create Vue instance
new Vue({
  router,
  store,
  i18n,
  render: function (h) { return h(App) }
}).$mount('#app')
