<template>
  <div class="statistics">
    <div class="mb-3">
      <div class="flex gap-2">
        <button @click="refreshStats" class="btn btn-primary" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm mr-2"></span>
          Refresh
        </button>
        <button @click="resetStats" class="btn btn-danger" :disabled="loading">
          Reset Statistics
        </button>
      </div>
    </div>
    
    <div>
      <div class="overflow-x-auto">
        <table class="min-w-full bg-white border border-gray-200 rounded-lg">
          <thead class="bg-gray-200 text-gray-800">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">Service/Endpoint</th>
              <th class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">Request Count</th>
              <th class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">Avg. Response Time</th>
              <th class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">Response Codes</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-if="loading" class="text-center">
              <td colspan="4" class="px-6 py-4">
                <div class="spinner-border" role="status">
                  <span class="sr-only">Loading...</span>
                </div>
              </td>
            </tr>
            <tr v-else-if="!statsData" class="text-center text-gray-500">
              <td colspan="4" class="px-6 py-4">No statistics available</td>
            </tr>
            <template v-else>
              <!-- Global stats -->
              <tr v-if="statsData.global" class="bg-blue-50 font-bold">
                <td class="px-6 py-4">Overall</td>
                <td class="px-6 py-4">{{ statsData.global.request_counter }}</td>
                <td class="px-6 py-4">{{ formatResponseTime(statsData.global.avg_resp_time) }}</td>
                <td class="px-6 py-4">
                  <span 
                    v-for="(count, code) in statsData.global.status_code_distribution" 
                    :key="code"
                    :class="`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-${getStatusColor(code)} text-white mr-1`"
                    :title="`${count} responses`"
                  >
                    {{ code }}
                  </span>
                </td>
              </tr>
              
              <!-- Service stats -->
              <template v-for="service in statsData.services" :key="service.hint">
                <tr class="bg-gray-100 font-bold">
                  <td class="px-6 py-4">{{ service.hint }}</td>
                  <td class="px-6 py-4">{{ service.request_counter }}</td>
                  <td class="px-6 py-4">{{ formatResponseTime(service.avg_resp_time) }}</td>
                  <td class="px-6 py-4">
                    <span 
                      v-for="(count, code) in service.status_code_distribution" 
                      :key="code"
                      :class="`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-${getStatusColor(code)} text-white mr-1`"
                      :title="`${count} responses`"
                    >
                      {{ code }}
                    </span>
                  </td>
                </tr>
                
                <!-- Endpoint stats -->
                <tr v-for="endpoint in service.endpoints" :key="endpoint.hint" class="text-sm">
                  <td class="px-6 py-4 pl-12">{{ endpoint.hint }}</td>
                  <td class="px-6 py-4">{{ endpoint.request_counter }}</td>
                  <td class="px-6 py-4">{{ formatResponseTime(endpoint.avg_resp_time) }}</td>
                  <td class="px-6 py-4">
                    <span 
                      v-for="(count, code) in endpoint.status_code_distribution" 
                      :key="code"
                      :class="`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-${getStatusColor(code)} text-white mr-1`"
                      :title="`${count} responses`"
                    >
                      {{ code }}
                    </span>
                  </td>
                </tr>
              </template>
            </template>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'Statistics',
  setup() {
    const statsData = ref(null)
    const loading = ref(false)
    
    const formatResponseTime = (time) => {
      if (time < 100) {
        return `${time}ms`
      }
      if (time < 10000) {
        return `${(time / 1000).toFixed(1)}s`
      }
      return `${Math.round(time / 1000)}s`
    }
    
    const getStatusColor = (status) => {
      const code = parseInt(status)
      if (code >= 500) return 'danger'
      if (code >= 400) return 'warning'
      if (code >= 300) return 'primary'
      if (code >= 200) return 'success'
      return 'secondary'
    }
    
    const refreshStats = async () => {
      loading.value = true
      try {
        const response = await fetch('/api/stats')
        statsData.value = await response.json()
      } catch (error) {
        console.error('Failed to fetch statistics:', error)
        alert('Failed to fetch statistics')
      } finally {
        loading.value = false
      }
    }
    
    const resetStats = async () => {
      if (!confirm('Are you sure you want to reset all statistics?')) {
        return
      }
      
      try {
        await fetch('/api/stats', { method: 'DELETE' })
        alert('Statistics have been reset')
        await refreshStats()
      } catch (error) {
        console.error('Failed to reset statistics:', error)
        alert('Failed to reset statistics')
      }
    }
    
    onMounted(() => {
      refreshStats()
    })
    
    return {
      statsData,
      loading,
      formatResponseTime,
      getStatusColor,
      refreshStats,
      resetStats
    }
  }
}
</script>

<style scoped>
.statistics {
  min-height: 400px;
}

.badge {
  font-size: 0.75rem;
}
</style>
