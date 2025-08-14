# Mockintosh Management UI

A modern Vue.js 3 application for managing Mockintosh services, built with Vue 3 Composition API, Vue Router, and Tailwind CSS.

## Features

- **HTTP Endpoints**: Interactive OpenAPI/Swagger UI for testing endpoints
- **Async Actors**: Management of Kafka/AMQP/Redis producers and consumers
- **Traffic Log**: Real-time monitoring and analysis of HTTP traffic
- **Statistics**: Request counts, response times, and status code distributions
- **Configuration**: YAML/JSON configuration editor with syntax highlighting
- **Unhandled Requests**: Template generation for missing endpoint configurations

## Prerequisites

- Node.js 16+ and npm
- Mockintosh server running (default: http://localhost:8000)

## Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Build for production:
```bash
npm run build
```

4. Preview production build:
```bash
npm run preview
```

## Development

The application is structured as follows:

```
src/
├── components/           # Vue components
│   ├── HttpEndpoints.vue
│   ├── AsyncActors.vue
│   ├── TrafficLog.vue
│   ├── Statistics.vue
│   ├── Configuration.vue
│   └── UnhandledRequests.vue
├── App.vue              # Main application component
├── main.js              # Application entry point
├── style.css            # Tailwind CSS and custom styles
└── router.js            # Vue Router configuration
```

## Styling & Design

The application uses **Tailwind CSS** for styling, providing:
- Utility-first CSS framework for rapid development
- Responsive design with mobile-first approach
- Custom color palette with primary brand colors
- Consistent spacing, typography, and component styling
- Modern, clean interface design

### Custom Components
- Responsive navigation with active state indicators
- Custom button variants (primary, success, info, danger, secondary)
- Form controls with consistent styling
- Alert components for user feedback
- Table layouts with proper spacing and borders
- Card components for content organization

## API Endpoints

The application communicates with Mockintosh via the following endpoints:

- `/api/oas` - OpenAPI specifications
- `/api/stats` - Request statistics
- `/api/config` - Configuration management
- `/api/traffic-log` - Traffic logging
- `/api/async` - Async actors management
- `/api/unhandled` - Unhandled requests
- `/api/resources` - Resource file management
- `/api/tag` - Tag-based response selection

## Configuration

The Vite configuration includes a proxy to forward API requests to the Mockintosh server:

```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, '')
    }
  }
}
```

## Build Configuration

### Tailwind CSS
- **Config**: `tailwind.config.js` - Custom color palette and content paths
- **PostCSS**: `postcss.config.js` - Autoprefixer and Tailwind processing
- **Custom Styles**: `src/style.css` - Tailwind directives and component styles

### Vite
- **Plugin**: Vue 3 support with hot module replacement
- **Build**: Optimized production builds with CSS purging
- **Dev Server**: Fast development with instant hot reload

## Technologies Used

- **Vue 3** - Progressive JavaScript framework with Composition API
- **Vue Router 4** - Official router for Vue.js
- **Tailwind CSS** - Utility-first CSS framework for modern design
- **Vite** - Fast build tool and dev server
- **PostCSS** - CSS processing with autoprefixer
- **Highlight.js** - Syntax highlighting for code
- **Swagger UI** - Interactive API documentation

## Browser Support

- Chrome 88+
- Firefox 85+
- Safari 14+
- Edge 88+

## Recent Updates

### v2.0.0 - Tailwind CSS Migration
- ✅ Migrated from Bootstrap 5 to Tailwind CSS
- ✅ Improved responsive design and mobile experience
- ✅ Enhanced visual consistency and modern aesthetics
- ✅ Custom component library with reusable styles
- ✅ Optimized build process with PostCSS
- ✅ Better accessibility and focus states

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the same license as Mockintosh.
