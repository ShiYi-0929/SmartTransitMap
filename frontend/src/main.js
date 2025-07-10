// import { createApp } from 'vue'
// import App from './App.vue'
// import router from './router'
// import store from "./store";
// import "./assets/css/tailwind.css";
// import { createPinia } from 'pinia'
// import ElementPlus from 'element-plus'
// import 'element-plus/dist/index.css'
// import { library } from '@fortawesome/fontawesome-svg-core'
// import { faUser, faList, faSignOutAlt } from '@fortawesome/free-solid-svg-icons'
// import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
//
// library.add(faUser, faList, faSignOutAlt)
//
// const app = createApp(App)
// app.component('font-awesome-icon', FontAwesomeIcon)
// app.use(router)
// app.use(createPinia())
// app.use(ElementPlus)
// app.mount('#app')


import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import "./assets/css/tailwind.css";
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import { library } from '@fortawesome/fontawesome-svg-core'
import { faUser, faList, faSignOutAlt } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

library.add(faUser, faList, faSignOutAlt)

const app = createApp(App)
app.component('font-awesome-icon', FontAwesomeIcon)
app.use(router)
app.use(createPinia())
app.use(ElementPlus)
app.mount('#app')
