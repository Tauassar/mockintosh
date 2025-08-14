<template>
  <div class="http-endpoints">
    <!-- <div class="mb-4">
      <div class="alert alert-info">
        <small class="text-gray-600">
          Pick any endpoint below and use "Try it out" button to send the request
        </small>
      </div>
    </div> -->
    
    <div>
      <div id="swagger-ui" ref="swaggerContainer">
        <div class="text-center py-12">
          <div class="spinner-border" role="status">
            <span class="sr-only">Loading...</span>
          </div>
          <p class="mt-2 text-gray-600">Loading OpenAPI specification...</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import SwaggerUIBundle from 'swagger-ui'
import 'swagger-ui/dist/swagger-ui.css'

export default {
  name: 'HttpEndpoints',
  setup() {
    const swaggerContainer = ref(null)
    let swaggerInstances = []
    
    const loadOpenAPI = async () => {
      try {
        // Clear previous instances
        clearSwaggerInstances()
        
        const response = await fetch('/api/oas')
        const data = await response.json()
        
        // Clear loading state
        swaggerContainer.value.innerHTML = ''
        
        let specs = []
        if (data.openapi) {
          specs = [data]
        } else {
          specs = data.documents || []
        }
        
        // Wait for DOM to be ready
        await nextTick()
        
        specs.forEach((spec, index) => {
          const container = document.createElement('div')
          container.id = `swagger-${Date.now()}-${index}`
          swaggerContainer.value.appendChild(container)
          
          const swaggerInstance = SwaggerUIBundle({
            spec: spec,
            dom_id: `#${container.id}`,
            presets: [
              SwaggerUIBundle.presets.apis,
              SwaggerUIBundle.standalonePreset
            ],
            layout: "BaseLayout"
          })
          
          swaggerInstances.push(swaggerInstance)
        })
      } catch (error) {
        console.error('Failed to load OpenAPI spec:', error)
        swaggerContainer.value.innerHTML = `
          <div class="alert alert-danger">
            Failed to load OpenAPI specification. Please check the server connection.
          </div>
        `
      }
    }
    
    const clearSwaggerInstances = () => {
      // Clean up previous Swagger instances
      swaggerInstances.forEach(instance => {
        if (instance && typeof instance.destroy === 'function') {
          try {
            instance.destroy()
          } catch (e) {
            console.warn('Error destroying Swagger instance:', e)
          }
        }
      })
      swaggerInstances = []
      
      // Clear container
      if (swaggerContainer.value) {
        swaggerContainer.value.innerHTML = ''
      }
    }
    
    onMounted(() => {
      loadOpenAPI()
    })
    
    onUnmounted(() => {
      clearSwaggerInstances()
    })
    
    return {
      swaggerContainer
    }
  }
}
</script>

<style scoped>
.http-endpoints {
  min-height: 600px;
}

#swagger-ui {
  min-height: 500px;
}

/* Override Swagger UI styles */
:deep(.swagger-ui .wrapper) {
  padding: 0;
}

:deep(.scheme-container) {
  display: none;
}
</style>
