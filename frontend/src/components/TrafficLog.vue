<template>
  <div class="traffic-log">
    <div class="mb-3">
      <div class="flex justify-between items-center">
        <div class="flex items-center">
          <input 
            v-model="trafficLogEnabled" 
            @change="toggleTrafficLog" 
            class="w-4 h-4 text-primary-600 bg-gray-100 border-gray-300 rounded focus:ring-primary-500 focus:ring-2" 
            type="checkbox" 
            id="enableTrafficLog"
          >
          <label class="ml-2 text-sm font-medium text-gray-700" for="enableTrafficLog">
            Enable Traffic Log
          </label>
        </div>
        <button @click="clearTrafficLog" class="btn btn-info btn-sm">
          Clear
        </button>
      </div>
    </div>
    
    <div>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Left sidebar - Traffic items -->
        <div class="md:col-span-1">
          <div class="border border-gray-200 rounded-lg p-3 h-96 overflow-y-auto">
            <h6 class="mb-3 font-medium text-gray-900">Traffic Entries</h6>
            <div v-if="!trafficLogEnabled" class="text-gray-500 text-center py-8">
              Enable traffic logging to see entries
            </div>
            <div v-else-if="trafficEntries.length === 0" class="text-gray-500 text-center py-8">
              No traffic entries yet
            </div>
            <div v-else class="space-y-2">
              <div
                v-for="entry in trafficEntries"
                :key="entry.startedDateTime"
                @click="selectEntry(entry)"
                :class="[
                  'p-3 border border-gray-200 rounded-lg cursor-pointer transition-colors duration-200',
                  { 'bg-primary-50 border-primary-300': selectedEntry === entry }
                ]"
              >
                <div class="flex justify-between items-start">
                  <div class="flex-1">
                    <div class="flex items-center gap-2 mb-1">
                      <span 
                        :class="`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-${getMethodColor(entry.request.method)} text-white`"
                      >
                        {{ entry.request.method }}
                      </span>
                      <span 
                        :class="`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-${getStatusColor(entry.response.status)} text-white`"
                      >
                        {{ isMQ(entry) ? 'K' : entry.response.status }}
                      </span>
                      <span v-if="isUnhandled(entry)" class="text-yellow-600">
                        <i class="bi bi-exclamation-triangle" title="Request was forwarded to real service"></i>
                      </span>
                    </div>
                    <div class="text-xs text-gray-500">
                      {{ formatDateTime(entry.startedDateTime) }}
                    </div>
                    <div class="text-xs text-gray-700 truncate">
                      {{ getUrlPath(entry.request.url) }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Right side - Traffic details -->
        <div class="md:col-span-2">
          <div class="border border-gray-200 rounded-lg p-3 h-96 overflow-y-auto">
            <div v-if="!selectedEntry" class="text-gray-500 text-center py-12">
              Select traffic entry from the left sidebar...
            </div>
            <div v-else class="traffic-details">
              <div class="flex justify-between items-center mb-3">
                <div>
                  <small class="text-gray-500">{{ formatDateTime(selectedEntry.startedDateTime) }}</small>
                  <div v-if="selectedEntry._serviceName" class="text-sm text-gray-500">
                    Service: {{ selectedEntry._serviceName }}
                  </div>
                </div>
                <div class="flex gap-2">
                  <button 
                    v-if="isUnhandled(selectedEntry)"
                    @click="addToConfig" 
                    class="btn btn-primary btn-sm"
                  >
                    <i class="bi bi-eyedropper me-1"></i>
                    Add to config
                  </button>
                  <button @click="clearSelection" class="btn btn-outline-secondary btn-sm">
                    <i class="bi bi-x"></i>
                  </button>
                </div>
              </div>
              
              <!-- Request Details -->
              <div class="card mb-3">
                <div class="card-header">
                  <h6 class="mb-0">Request</h6>
                </div>
                <div class="card-body">
                  <div class="mb-2">
                    <span 
                      :class="`badge bg-${getMethodColor(selectedEntry.request.method)} me-2`"
                    >
                      {{ selectedEntry.request.method }}
                    </span>
                    <a :href="selectedEntry.request.url" target="_blank" class="text-decoration-none">
                      {{ selectedEntry.request.url }}
                    </a>
                  </div>
                  
                  <!-- Request Headers -->
                  <div v-if="selectedEntry.request.headers.length > 0" class="mb-3">
                    <h6 class="small text-muted">Headers</h6>
                    <div class="table-responsive">
                      <table class="table table-sm table-borderless">
                        <tbody>
                          <tr v-for="header in selectedEntry.request.headers" :key="header.name">
                            <td class="text-muted small" style="width: 30%;">{{ header.name }}:</td>
                            <td class="small">{{ header.value }}</td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                  
                  <!-- Request Body -->
                  <div v-if="selectedEntry.request.postData && selectedEntry.request.postData.text">
                    <h6 class="small text-muted">Body</h6>
                    <div class="bg-light p-2 rounded">
                      <pre class="mb-0 small">{{ selectedEntry.request.postData.text }}</pre>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Response Details -->
              <div class="card">
                <div class="card-header">
                  <h6 class="mb-0">Response</h6>
                </div>
                <div class="card-body">
                  <div class="mb-2">
                    <span 
                      :class="`badge bg-${getStatusColor(selectedEntry.response.status)} me-2`"
                    >
                      {{ selectedEntry.response.status }} {{ selectedEntry.response.statusText }}
                    </span>
                  </div>
                  
                  <!-- Response Headers -->
                  <div v-if="selectedEntry.response.headers.length > 0" class="mb-3">
                    <h6 class="small text-muted">Headers</h6>
                    <div class="table-responsive">
                      <table class="table table-sm table-borderless">
                        <tbody>
                          <tr v-for="header in selectedEntry.response.headers" :key="header.name">
                            <td class="text-muted small" style="width: 30%;">{{ header.name }}:</td>
                            <td class="small">{{ header.value }}</td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                  
                  <!-- Response Body -->
                  <div v-if="selectedEntry.response.content && selectedEntry.response.content.text">
                    <h6 class="small text-muted">Body</h6>
                    <div class="bg-light p-2 rounded">
                      <pre class="mb-0 small">{{ selectedEntry.response.content.text }}</pre>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'

export default {
  name: 'TrafficLog',
  setup() {
    const trafficLogEnabled = ref(false)
    const trafficEntries = ref([])
    const selectedEntry = ref(null)
    let pollInterval = null
    
    const getMethodColor = (method) => {
      const colors = {
        'GET': 'info',
        'POST': 'success',
        'PUT': 'warning',
        'DELETE': 'danger',
        'PATCH': 'primary',
        'HEAD': 'secondary'
      }
      return colors[method] || 'dark'
    }
    
    const getStatusColor = (status) => {
      const code = parseInt(status)
      if (code >= 500) return 'danger'
      if (code >= 400) return 'warning'
      if (code >= 300) return 'primary'
      if (code >= 200) return 'success'
      return 'secondary'
    }
    
    const formatDateTime = (dateTime) => {
      return new Date(dateTime).toLocaleString()
    }
    
    const getUrlPath = (url) => {
      try {
        const urlObj = new URL(url)
        return urlObj.pathname + urlObj.search
      } catch {
        return url
      }
    }
    
    const isMQ = (entry) => {
      try {
        const url = new URL(entry.request.url)
        return url.protocol === 'kafka:'
      } catch {
        return false
      }
    }
    
    const isUnhandled = (entry) => {
      if (isMQ(entry)) return false
      
      for (const header of entry.response.headers) {
        if (header.name.toLowerCase() === 'x-mockintosh-prompt') {
          return false
        }
      }
      return true
    }
    
    const selectEntry = (entry) => {
      selectedEntry.value = entry
    }
    
    const clearSelection = () => {
      selectedEntry.value = null
    }
    
    const toggleTrafficLog = async () => {
      try {
        await fetch('/api/traffic-log', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ enable: trafficLogEnabled.value })
        })
        
        if (trafficLogEnabled.value) {
          startPolling()
        } else {
          stopPolling()
        }
      } catch (error) {
        console.error('Failed to toggle traffic log:', error)
        trafficLogEnabled.value = !trafficLogEnabled.value
      }
    }
    
    const clearTrafficLog = async () => {
      try {
        await fetch('/api/traffic-log', { method: 'DELETE' })
        trafficEntries.value = []
        selectedEntry.value = null
      } catch (error) {
        console.error('Failed to clear traffic log:', error)
        alert('Failed to clear traffic log')
      }
    }
    
    const loadTrafficLog = async () => {
      try {
        const response = await fetch('/api/traffic-log')
        const data = await response.json()
        
        trafficLogEnabled.value = data.log._enabled
        trafficEntries.value = data.log.entries || []
        
        if (trafficLogEnabled.value) {
          startPolling()
        }
      } catch (error) {
        console.error('Failed to load traffic log:', error)
      }
    }
    
    const startPolling = () => {
      if (pollInterval) return
      
      pollInterval = setInterval(async () => {
        if (trafficLogEnabled.value) {
          try {
            const response = await fetch('/api/traffic-log')
            const data = await response.json()
            trafficEntries.value = data.log.entries || []
          } catch (error) {
            console.error('Failed to poll traffic log:', error)
          }
        }
      }, 1000)
    }
    
    const stopPolling = () => {
      if (pollInterval) {
        clearInterval(pollInterval)
        pollInterval = null
      }
    }
    
    const addToConfig = async () => {
      if (!selectedEntry.value) return
      
      try {
        const response = await fetch('/api/config')
        const config = await response.json()
        
        // Find the service and add the endpoint
        for (const service of config.services) {
          if (service.name === selectedEntry.value._serviceName) {
            if (!service.endpoints) {
              service.endpoints = []
            }
            
            const endpoint = createEndpointFromEntry(selectedEntry.value)
            service.endpoints.push(endpoint)
            
            // Update config
            await fetch('/api/config', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify(config)
            })
            
            alert('Endpoint added to configuration')
            break
          }
        }
      } catch (error) {
        console.error('Failed to add to config:', error)
        alert('Failed to add to config')
      }
    }
    
    const createEndpointFromEntry = (entry) => {
      const url = new URL(entry.request.url)
      const endpoint = {
        path: url.pathname,
        method: entry.request.method
      }
      
      // Add query parameters
      if (entry.request.queryString && entry.request.queryString.length > 0) {
        endpoint.queryString = {}
        for (const param of entry.request.queryString) {
          endpoint.queryString[param.name] = param.value
        }
      }
      
      // Add custom headers
      const regularHeaders = [
        'a-im', 'accept', 'accept-charset', 'accept-datetime', 'accept-encoding', 'accept-language',
        'access-control-allow-credentials', 'access-control-allow-origin', 'access-control-request-headers',
        'access-control-request-method', 'access-control-allow-methods', 'authorization', 'cache-control',
        'connection', 'content-encoding', 'content-length', 'cookie', 'date', 'dnt', 'expect', 'forwarded',
        'from', 'front-end-https', 'host', 'http2-settings', 'if-match', 'if-modified-since', 'if-none-match',
        'if-range', 'if-unmodified-since', 'max-forwards', 'origin', 'pragma', 'proxy-authorization',
        'proxy-connection', 'range', 'referer', 'save-data', 'sec-fetch-user', 'te', 'trailer',
        'transfer-encoding', 'upgrade', 'upgrade-insecure-requests', 'user-agent', 'via', 'warning',
        'x-att-deviceid', 'x-correlation-id', 'x-forwarded-for', 'x-forwarded-host', 'x-forwarded-port',
        'x-forwarded-proto', 'x-http-method-override', 'x-real-ip', 'x-request-id', 'x-request-start',
        'x-requested-with', 'x-uidh', 'x-wap-profile', 'x-envoy-expected-rq-timeout-ms', 'x-envoy-external-address',
        'sec-ch-ua', 'sec-ch-ua-mobile', 'sec-fetch-site', 'sec-fetch-mode', 'sec-fetch-dest',
        'server', 'vary', 'etag', 'strict-transport-security'
      ]
      
      if (entry.request.headers) {
        endpoint.headers = {}
        for (const header of entry.request.headers) {
          if (!regularHeaders.includes(header.name.toLowerCase())) {
            endpoint.headers[header.name] = header.value
          }
        }
      }
      
      // Add request body
      if (entry.request.postData && entry.request.postData.text) {
        endpoint.body = { text: "{{regEx '.+'}}" }
      }
      
      // Add response
      endpoint.response = {
        status: entry.response.status
      }
      
      if (entry.response.headers) {
        endpoint.response.headers = {}
        for (const header of entry.response.headers) {
          if (!regularHeaders.includes(header.name.toLowerCase())) {
            endpoint.response.headers[header.name] = header.value
          }
        }
      }
      
      if (entry.response.content && entry.response.content.text) {
        try {
          endpoint.response.body = JSON.stringify(JSON.parse(entry.response.content.text), null, 2)
        } catch {
          endpoint.response.body = entry.response.content.text
        }
        
        if (entry.response.content.encoding) {
          endpoint.response.body = "Seems binary, please use external file to provide it (@-prefix value)"
        }
      }
      
      return endpoint
    }
    
    onMounted(() => {
      loadTrafficLog()
    })
    
    onUnmounted(() => {
      stopPolling()
    })
    
    return {
      trafficLogEnabled,
      trafficEntries,
      selectedEntry,
      getMethodColor,
      getStatusColor,
      formatDateTime,
      getUrlPath,
      isMQ,
      isUnhandled,
      selectEntry,
      clearSelection,
      toggleTrafficLog,
      clearTrafficLog,
      addToConfig
    }
  }
}
</script>

<style scoped>
.traffic-log {
  min-height: 600px;
}

.list-group-item {
  border-left: none;
  border-right: none;
}

.list-group-item:first-child {
  border-top: none;
}

.list-group-item:last-child {
  border-bottom: none;
}

.list-group-item.active {
  background-color: #e3f2fd;
  border-color: #2196f3;
  color: #000;
}

pre {
  font-family: 'Courier New', Courier, monospace;
  font-size: 0.75rem;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
