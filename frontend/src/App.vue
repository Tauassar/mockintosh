<template>
  <div id="app">
    <!-- Header -->
    <header class="bg-gray-100 text-gray-800 py-2 border-b border-gray-200">
      <div class="container mx-auto px-4">
        <div class="flex justify-between items-center">
          <h1 class="flex items-center text-base font-semibold m-0">
            <img src="https://mockintosh.io/img/logo_dark.svg" alt="[M]" style="width: 32px; height: 32px;" class="mr-2">
            Mockintosh Control Plane
          </h1>
          <div class="text-sm">
            <a href="https://mockintosh.io" target="_blank" class="text-gray-600 hover:text-gray-800 transition-colors">
              <i class="bi bi-github"></i> Docs
            </a>
          </div>
        </div>
      </div>
    </header>

    <!-- Navigation -->
    <nav class="bg-gray-100 border-b border-gray-200 py-1">
      <div class="container mx-auto px-4">
        <div class="flex space-x-1">
          <router-link 
            v-for="item in navItems" 
            :key="item.path"
            :to="item.path" 
            class="nav-link"
            active-class="active"
          >
            {{ item.name }}
          </router-link>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="container mx-auto px-4">
      <router-view :key="$route.fullPath" />
    </main>

    <!-- Footer -->
    <footer class="text-gray-500 text-center text-sm border-t border-gray-200 py-3 mt-4">
      Management UI for <a href="https://mockintosh.io" target="_blank" class="text-primary-600 hover:text-primary-700">Mockintosh</a>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      navItems: [
        { path: '/http-endpoints', name: 'HTTP Endpoints' },
        { path: '/async-actors', name: 'Async Actors' },
        { path: '/traffic-log', name: 'Traffic Log' },
        { path: '/statistics', name: 'Statistics' },
        { path: '/configuration', name: 'Configuration' },
        { path: '/unhandled-requests', name: 'Unhandled Requests' }
      ]
    }
  }
}
</script>

<style>
/* Custom styles are now in style.css */
</style>
