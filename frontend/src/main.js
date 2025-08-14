import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import './style.css'
import 'swagger-ui/dist/swagger-ui.css'
import 'highlight.js/styles/github.css'

// Import components
import HttpEndpoints from './components/HttpEndpoints.vue'
import AsyncActors from './components/AsyncActors.vue'
import TrafficLog from './components/TrafficLog.vue'
import Statistics from './components/Statistics.vue'
import Configuration from './components/Configuration.vue'
import UnhandledRequests from './components/UnhandledRequests.vue'

// Create router
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/http-endpoints' },
    { path: '/http-endpoints', name: 'http-endpoints', component: HttpEndpoints },
    { path: '/async-actors', name: 'async-actors', component: AsyncActors },
    { path: '/traffic-log', name: 'traffic-log', component: TrafficLog },
    { path: '/statistics', name: 'statistics', component: Statistics },
    { path: '/configuration', name: 'configuration', component: Configuration },
    { path: '/unhandled-requests', name: 'unhandled-requests', component: UnhandledRequests }
  ]
})

// Add error handling
router.onError((error) => {
  console.error('Router error:', error)
})

// Create and mount app
const app = createApp(App)
app.use(router)

// Add global error handler
app.config.errorHandler = (err, vm, info) => {
  console.error('Vue error:', err)
  console.error('Component:', vm)
  console.error('Info:', info)
}

app.mount('#app')
