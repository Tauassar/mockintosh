<template>
  <div class="configuration">
    <div class="mb-3">
      <div class="flex gap-2 items-center flex-wrap">
        <select v-model="selectedFile" class="form-select" style="width: auto;">
          <option value="">&lt;&lt;&lt; Main Configuration &gt;&gt;&gt;</option>
          <option v-for="file in availableFiles" :key="file" :value="file">
            {{ file }}
          </option>
        </select>
        
        <button @click="loadFile" class="btn btn-primary" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm mr-2"></span>
          Load
        </button>
        
        <button @click="applyChanges" class="btn btn-success" :disabled="!configContent">
          Apply Changes
        </button>
        
        <button @click="resetIterators" class="btn btn-info">
          Reset Dataset Iterators
        </button>
        
        <div v-if="availableTags.length > 0" class="ml-auto flex items-center gap-2">
          <label class="mb-0">Enable tag:</label>
          <select v-model="selectedTag" class="form-select" style="width: auto;">
            <option value="">None</option>
            <option v-for="tag in availableTags" :key="tag" :value="tag">
              {{ tag }}
            </option>
          </select>
        </div>
      </div>
    </div>
    
    <div>
      <div class="border border-gray-200 rounded-lg p-3 bg-gray-50">
        <div class="flex justify-between items-center mb-2">
          <small class="text-gray-600">Configuration Editor</small>
          <small class="text-gray-600">{{ selectedFile || 'Main Config' }}</small>
        </div>
        <div class="relative">
          <pre v-if="!configContent" class="text-gray-500 text-center py-12">
            Select a file to load configuration...
          </pre>
          <pre v-else><code ref="codeEditor" class="language-yaml"></code></pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch, nextTick } from 'vue'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'

export default {
  name: 'Configuration',
  setup() {
    const selectedFile = ref('')
    const configContent = ref('')
    const availableFiles = ref([])
    const availableTags = ref([])
    const selectedTag = ref('')
    const loading = ref(false)
    const codeEditor = ref(null)
    
    const loadFile = async () => {
      loading.value = true
      try {
        let url
        if (selectedFile.value) {
          url = `/api/resources?path=${selectedFile.value}`
        } else {
          url = '/api/config?format=yaml'
        }
        
        const response = await fetch(url)
        configContent.value = await response.text()
        
        // Wait for DOM to be ready and highlight the code
        await nextTick()
        if (codeEditor.value) {
          codeEditor.value.textContent = configContent.value
          hljs.highlightElement(codeEditor.value)
        }
      } catch (error) {
        console.error('Failed to load file:', error)
        alert('Failed to load file')
      } finally {
        loading.value = false
      }
    }
    
    const applyChanges = async () => {
      if (!configContent.value) return
      
      try {
        if (selectedFile.value) {
          // Update resource file
          const formData = new FormData()
          formData.append(selectedFile.value, new Blob([configContent.value]), selectedFile.value)
          
          await fetch('/api/resources', {
            method: 'POST',
            body: formData
          })
          
          alert('File has been updated')
        } else {
          // Update main config
          await fetch('/api/config', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/x-yaml'
            },
            body: configContent.value
          })
          
          alert('Config has been updated')
          window.location.reload()
        }
      } catch (error) {
        console.error('Failed to apply changes:', error)
        alert('Failed to apply changes')
      }
    }
    
    const resetIterators = async () => {
      try {
        await fetch('/api/reset-iterators', { method: 'POST' })
        alert('Iterators reset successfully')
      } catch (error) {
        console.error('Failed to reset iterators:', error)
        alert('Failed to reset iterators')
      }
    }
    
    const loadResources = async () => {
      try {
        const response = await fetch('/api/resources')
        const resources = await response.json()
        availableFiles.value = resources.files || []
      } catch (error) {
        console.error('Failed to load resources:', error)
      }
    }
    
    const loadTags = async () => {
      try {
        const response = await fetch('/api/tag')
        const tagData = await response.json()
        if (tagData.tags) {
          selectedTag.value = tagData.tags[0]
        }
      } catch (error) {
        console.error('Failed to load tags:', error)
      }
    }
    
    const extractTagsFromConfig = (config) => {
      const tags = new Set()
      
      if (!config.services) {
        config = { services: [config] }
      }
      
      for (const service of config.services) {
        if (service.endpoints) {
          for (const endpoint of service.endpoints) {
            if (endpoint.response) {
              const responses = Array.isArray(endpoint.response) ? endpoint.response : [endpoint.response]
              for (const resp of responses) {
                if (resp.tag) {
                  tags.add(resp.tag)
                }
              }
            }
          }
        } else if (service.actors) {
          for (const actor of service.actors) {
            if (actor.produce) {
              const responses = Array.isArray(actor.produce) ? actor.produce : [actor.produce]
              for (const resp of responses) {
                if (resp.tag) {
                  tags.add(resp.tag)
                }
              }
            }
          }
        }
      }
      
      return Array.from(tags).sort()
    }
    
    const loadConfig = async () => {
      try {
        const response = await fetch('/api/config')
        const config = await response.json()
        availableTags.value = extractTagsFromConfig(config)
      } catch (error) {
        console.error('Failed to load config:', error)
      }
    }
    
    watch(selectedTag, async (newTag) => {
      if (newTag !== undefined) {
        try {
          await fetch('/api/tag', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(newTag)
          })
        } catch (error) {
          console.error('Failed to update tag:', error)
        }
      }
    })
    
    onMounted(async () => {
      try {
        console.log('Configuration component mounted')
        await Promise.all([
          loadResources(),
          loadConfig()
        ])
        await loadTags()
        await loadFile()
      } catch (error) {
        console.error('Error in onMounted:', error)
      }
    })
    
    return {
      selectedFile,
      configContent,
      availableFiles,
      availableTags,
      selectedTag,
      loading,
      codeEditor,
      loadFile,
      applyChanges,
      resetIterators
    }
  }
}
</script>

<style scoped>
.configuration {
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
