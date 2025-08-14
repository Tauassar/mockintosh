<template>
  <div class="async-actors">
    <div class="mb-3">
      <div class="flex justify-between items-center">
        <div class="alert alert-info mb-0 py-2">
          <small class="text-gray-600">
            Async actors appear if config contains services of type kafka/amqp/redis.
          </small>
        </div>
        <button @click="refreshActors" class="btn btn-secondary btn-sm" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm mr-2"></span>
          Refresh
        </button>
      </div>
    </div>
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Producers -->
      <div>
        <div class="bg-white border border-gray-200 rounded-lg shadow-sm">
          <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
            <h5 class="mb-0 font-medium text-gray-900">Producers</h5>
          </div>
          <div class="p-6">
            <div v-if="loading" class="text-center py-3">
              <div class="spinner-border" role="status">
                <span class="sr-only">Loading...</span>
              </div>
            </div>
            <div v-else-if="producers.length === 0" class="text-gray-500 text-center py-3">
              No producers defined
            </div>
            <div v-else class="space-y-4">
              <div 
                v-for="producer in producers" 
                :key="producer.index"
                class="border border-primary-200 rounded-lg bg-primary-50"
              >
                <div class="px-4 py-3 border-b border-primary-200 flex justify-between items-center">
                  <div>
                    <span class="text-primary-700 font-bold">Actor #{{ producer.index }}:</span>
                    <span class="ml-2">{{ producer.name || '<Name not set>' }}</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span 
                      v-if="producer.produced" 
                      class="text-green-600 text-sm"
                      style="display: none;"
                    >
                      Produced!
                    </span>
                    <button 
                      @click="triggerProducer(producer)" 
                      class="btn btn-primary btn-sm"
                      :disabled="producer.triggering"
                    >
                      <span v-if="producer.triggering" class="spinner-border spinner-border-sm mr-2"></span>
                      Trigger
                    </button>
                  </div>
                </div>
                <div class="p-4">
                  <p class="mb-2">
                    <strong>Queue Name:</strong> {{ producer.queue }}
                  </p>
                  <p class="mb-2">
                    <strong>Last Produced:</strong> 
                    {{ producer.lastProduced ? formatDateTime(producer.lastProduced * 1000) : 'N/A' }}
                  </p>
                  <p class="mb-0">
                    <strong>Message Count:</strong> {{ producer.producedMessages }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Consumers -->
      <div>
        <div class="bg-white border border-gray-200 rounded-lg shadow-sm">
          <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
            <h5 class="mb-0 font-medium text-gray-900">Consumers</h5>
          </div>
          <div class="p-6">
            <div v-if="loading" class="text-center py-3">
              <div class="spinner-border" role="status">
                <span class="sr-only">Loading...</span>
              </div>
            </div>
            <div v-else-if="consumers.length === 0" class="text-gray-500 text-center py-3">
              No consumers defined
            </div>
            <div v-else>
              <div 
                v-for="consumer in consumers" 
                :key="consumer.index"
                class="border border-info-200 rounded-lg bg-info-50"
              >
                <div class="px-4 py-3 border-b border-info-200 flex justify-between items-center">
                  <div>
                    <span class="text-info-700 font-bold">Actor #{{ consumer.index }}:</span>
                    <span class="ml-2">{{ consumer.name || '<Name not set>' }}</span>
                  </div>
                  <button 
                    @click="viewCapturedMessages(consumer)" 
                    class="btn btn-info btn-sm"
                  >
                    View Captured Messages [{{ consumer.captured }}]
                  </button>
                </div>
                <div class="p-4">
                  <p class="mb-2">
                    <strong>Queue Name:</strong> {{ consumer.queue }}
                  </p>
                  <p class="mb-2">
                    <strong>Last Consumed:</strong> 
                    {{ consumer.lastConsumed ? formatDateTime(consumer.lastConsumed * 1000) : 'N/A' }}
                  </p>
                  <p class="mb-0">
                    <strong>Message Count:</strong> {{ consumer.consumedMessages }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Captured Messages Modal -->
    <div 
      class="modal fade" 
      id="capturedMessagesModal" 
      tabindex="-1" 
      aria-labelledby="capturedMessagesModalLabel" 
      aria-hidden="true"
    >
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ modalTitle }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div v-if="capturedMessages.length === 0" class="text-center py-4">
              <p class="text-gray-500">No messages captured</p>
            </div>
            <div v-else>
              <div class="mb-3">
                <div class="btn-group" role="group">
                  <button
                    v-for="(message, index) in capturedMessages"
                    :key="index"
                    @click="selectMessage(index)"
                    :class="[
                      'btn btn-outline-secondary',
                      { 'btn-info': selectedMessageIndex === index }
                    ]"
                  >
                    #{{ index + 1 }}
                  </button>
                </div>
              </div>
              
              <div v-if="selectedMessage" class="message-details">
                <div class="bg-white border border-gray-200 rounded-lg shadow-sm">
                  <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
                    <h6 class="mb-0 font-medium text-gray-900">Message Details</h6>
                  </div>
                  <div class="p-6">
                    <div class="mb-3">
                      <strong>Timestamp:</strong> {{ formatDateTime(selectedMessage.startedDateTime) }}
                    </div>
                    
                    <!-- Request Details -->
                    <div class="mb-3">
                      <h6 class="small text-gray-600">Request</h6>
                      <div class="bg-gray-100 p-2 rounded-lg">
                        <div class="mb-2">
                          <span class="badge bg-gray-600 mr-2">{{ selectedMessage.request.method }}</span>
                          <span>{{ selectedMessage.request.url }}</span>
                        </div>
                        <div v-if="selectedMessage.request.headers && selectedMessage.request.headers.length > 0">
                          <strong>Headers:</strong>
                          <div class="overflow-x-auto">
                            <table class="table table-sm table-borderless">
                              <tbody>
                                <tr v-for="header in selectedMessage.request.headers" :key="header.name">
                                  <td class="text-gray-600 text-sm" style="width: 30%;">{{ header.name }}:</td>
                                  <td class="text-gray-900 text-sm">{{ header.value }}</td>
                                </tr>
                              </tbody>
                            </table>
                          </div>
                        </div>
                        <div v-if="selectedMessage.request.postData && selectedMessage.request.postData.text">
                          <strong>Body:</strong>
                          <pre class="mb-0 text-sm mt-2">{{ selectedMessage.request.postData.text }}</pre>
                        </div>
                      </div>
                    </div>
                    
                    <!-- Response Details -->
                    <div>
                      <h6 class="small text-gray-600">Response</h6>
                      <div class="bg-gray-100 p-2 rounded-lg">
                        <div class="mb-2">
                          <span 
                            :class="`badge bg-${getStatusColor(selectedMessage.response.status)} mr-2`"
                          >
                            {{ selectedMessage.response.status }} {{ selectedMessage.response.statusText }}
                          </span>
                        </div>
                        <div v-if="selectedMessage.response.headers && selectedMessage.response.headers.length > 0">
                          <strong>Headers:</strong>
                          <div class="overflow-x-auto">
                            <table class="table table-sm table-borderless">
                              <tbody>
                                <tr v-for="header in selectedMessage.response.headers" :key="header.name">
                                  <td class="text-gray-600 text-sm" style="width: 30%;">{{ header.name }}:</td>
                                  <td class="text-gray-900 text-sm">{{ header.value }}</td>
                                </tr>
                              </tbody>
                            </table>
                          </div>
                        </div>
                        <div v-if="selectedMessage.response.content && selectedMessage.response.content.text">
                          <strong>Body:</strong>
                          <pre class="mb-0 text-sm mt-2">{{ selectedMessage.response.content.text }}</pre>
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
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'

export default {
  name: 'AsyncActors',
  setup() {
    const loading = ref(false)
    const producers = ref([])
    const consumers = ref([])
    const capturedMessages = ref([])
    const selectedMessageIndex = ref(0)
    const modalTitle = ref('')
    
    const selectedMessage = computed(() => {
      if (capturedMessages.value.length === 0 || selectedMessageIndex.value >= capturedMessages.value.length) {
        return null
      }
      return capturedMessages.value[selectedMessageIndex.value]
    })
    
    const formatDateTime = (timestamp) => {
      return new Date(timestamp).toLocaleString()
    }
    
    const getStatusColor = (status) => {
      const code = parseInt(status)
      if (code >= 500) return 'danger'
      if (code >= 400) return 'warning'
      if (code >= 300) return 'primary'
      if (code >= 200) return 'success'
      return 'secondary'
    }
    
    const refreshActors = async () => {
      loading.value = true
      try {
        const response = await fetch('/api/async')
        const data = await response.json()
        
        producers.value = data.producers || []
        consumers.value = data.consumers || []
      } catch (error) {
        console.error('Failed to fetch async actors:', error)
        alert('Failed to fetch async actors')
      } finally {
        loading.value = false
      }
    }
    
    const triggerProducer = async (producer) => {
      const producerId = producer.name || producer.index
      producer.triggering = true
      
      try {
        const response = await fetch(`/api/async/producers/${producerId}`, { method: 'POST' })
        const updatedProducer = await response.json()
        
        // Update the producer data
        Object.assign(producer, updatedProducer)
        
        // Show success message
        const successElement = producer.$el?.querySelector('.text-green-600')
        if (successElement) {
          successElement.style.display = 'inline'
          setTimeout(() => {
            successElement.style.display = 'none'
          }, 2000)
        }
      } catch (error) {
        console.error('Failed to trigger producer:', error)
        alert('Failed to trigger producer')
      } finally {
        producer.triggering = false
      }
    }
    
    const viewCapturedMessages = async (consumer) => {
      const consumerId = consumer.name || consumer.index
      
      try {
        const response = await fetch(`/api/async/consumers/${consumerId}`)
        const data = await response.json()
        
        capturedMessages.value = data.log.entries || []
        selectedMessageIndex.value = 0
        modalTitle.value = `Captured Messages for Actor '${consumerId}'`
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('capturedMessagesModal'))
        modal.show()
      } catch (error) {
        console.error('Failed to fetch captured messages:', error)
        alert('Failed to fetch captured messages')
      }
    }
    
    const selectMessage = (index) => {
      selectedMessageIndex.value = index
    }
    
    onMounted(() => {
      refreshActors()
    })
    
    return {
      loading,
      producers,
      consumers,
      capturedMessages,
      selectedMessageIndex,
      modalTitle,
      selectedMessage,
      formatDateTime,
      getStatusColor,
      refreshActors,
      triggerProducer,
      viewCapturedMessages,
      selectMessage
    }
  }
}
</script>

<style scoped>
.async-actors {
  min-height: 500px;
}

.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.message-details pre {
  font-family: 'Courier New', Courier, monospace;
  font-size: 0.75rem;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.btn-group .btn {
  font-size: 0.875rem;
}
</style>
