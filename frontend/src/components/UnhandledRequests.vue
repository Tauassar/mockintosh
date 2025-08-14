<template>
  <div class="unhandled-requests">
    <div class="mb-3">
      <div class="flex justify-between items-center">
        <div class="alert alert-warning mb-0 py-2">
          <small class="text-gray-600">
            Below is the config template for requests that are missing in Mockintosh config:
          </small>
        </div>
        <div class="flex gap-2 items-center">
          <div class="flex items-center mb-0">
            <input 
              v-model="unhandledEnabled" 
              @change="toggleUnhandled" 
              class="w-4 h-4 text-primary-600 bg-gray-100 border-gray-300 rounded focus:ring-primary-500 focus:ring-2" 
              type="checkbox" 
              id="enableUnhandled"
            >
            <label class="ml-2 text-sm font-medium text-gray-700" for="enableUnhandled">
              Enabled
            </label>
          </div>
          <button @click="refreshUnhandled" class="btn btn-primary btn-sm" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm mr-2"></span>
            Refresh
          </button>
          <button @click="clearUnhandled" class="btn btn-info btn-sm">
            Clear
          </button>
        </div>
      </div>
    </div>
    
    <div>
      <div class="border border-gray-200 rounded-lg p-3 bg-gray-50">
        <div class="flex justify-between items-center mb-2">
          <small class="text-gray-600">Unhandled Requests Configuration</small>
          <small class="text-gray-600">YAML Format</small>
        </div>
        <div class="relative">
          <div v-if="loading" class="text-center py-12">
            <div class="spinner-border" role="status">
              <span class="sr-only">Loading...</span>
            </div>
          </div>
          <div v-else-if="!unhandledConfig" class="text-gray-500 text-center py-12">
            No unhandled requests configuration available
          </div>
          <pre v-else><code ref="configEditor" class="language-yaml"></code></pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'

export default {
  name: 'UnhandledRequests',
  setup() {
    const unhandledEnabled = ref(false)
    const unhandledConfig = ref('')
    const loading = ref(false)
    const configEditor = ref(null)
    
    const toggleUnhandled = async () => {
      try {
        await fetch('/api/unhandled', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(unhandledEnabled.value)
        })
        
        if (unhandledEnabled.value) {
          await refreshUnhandled()
        }
      } catch (error) {
        console.error('Failed to toggle unhandled requests:', error)
        unhandledEnabled.value = !unhandledEnabled.value
      }
    }
    
    const refreshUnhandled = async () => {
      loading.value = true
      try {
        const response = await fetch('/api/unhandled?format=yaml')
        unhandledConfig.value = await response.text()
        
        // Check if unhandled data is available
        const hasUnhandledData = response.headers.get('x-mockintosh-unhandled-data') === 'true'
        unhandledEnabled.value = hasUnhandledData
        
        // Highlight the code
        if (configEditor.value) {
          configEditor.value.textContent = unhandledConfig.value
          hljs.highlightElement(configEditor.value)
        }
      } catch (error) {
        console.error('Failed to load unhandled requests:', error)
        alert('Failed to load unhandled requests')
      } finally {
        loading.value = false
      }
    }
    
    const clearUnhandled = async () => {
      try {
        await fetch('/api/unhandled', { method: 'DELETE' })
        await refreshUnhandled()
      } catch (error) {
        console.error('Failed to clear unhandled requests:', error)
        alert('Failed to clear unhandled requests')
      }
    }
    
    onMounted(() => {
      refreshUnhandled()
    })
    
    return {
      unhandledEnabled,
      unhandledConfig,
      loading,
      configEditor,
      toggleUnhandled,
      refreshUnhandled,
      clearUnhandled
    }
  }
}
</script>

<style scoped>
.unhandled-requests {
  min-height: 500px;
}

pre {
  background: transparent;
  border: none;
  margin: 0;
  padding: 0;
}

code {
  font-family: 'Courier New', Courier, monospace;
  font-size: 0.875rem;
  line-height: 1.5;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
