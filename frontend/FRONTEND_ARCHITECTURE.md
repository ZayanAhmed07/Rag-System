# Frontend Architecture - Component-Based Design

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components (microservices pattern)
│   │   ├── layout/         # Page layout containers
│   │   │   ├── Header.jsx   # Top navigation bar
│   │   │   ├── Sidebar.jsx  # Left navigation menu
│   │   │   └── Footer.jsx   # Bottom footer
│   │   └── ui/             # Atomic UI components
│   │       └── index.jsx    # Button, Card, Input, Modal, Toast, Badge, etc.
│   │
│   ├── pages/              # Page-level components
│   │   ├── QueryPage.jsx    # Main RAG query interface
│   │   ├── IngestPage.jsx   # Document upload interface
│   │   ├── EvaluationPage.jsx # Performance metrics & evaluation
│   │   └── SettingsPage.jsx  # System configuration
│   │
│   ├── services/           # API communication layer
│   │   └── api.js          # Axios client + service methods
│   │
│   ├── hooks/              # Custom React hooks
│   │   └── index.js        # useQuery, useAsync, useLocalStorage, useDebounce
│   │
│   ├── utils/              # Utility functions
│   ├── styles/             # Global stylesheets
│   │   └── globals.css     # Tailwind + custom utilities
│   │
│   ├── App.jsx             # Main router & layout
│   └── main.jsx            # React entry point
│
├── public/
│   └── index.html          # HTML template
│
├── package.json            # Dependencies
├── vite.config.js          # Vite bundler config
├── tailwind.config.js      # Tailwind CSS config
└── postcss.config.js       # PostCSS config

## Component Hierarchy (Microservices Pattern)

### Services Layer
- **API Service** (queryService, ingestService, evaluationService, settingsService)
- Handles all backend communication
- Includes request/response interceptors
- Centralized error handling

### State Management Layer
- **Custom Hooks** (useQuery, useAsync, useLocalStorage, useDebounce)
- Encapsulate business logic
- Reusable across components
- Single responsibility principle

### UI Component Layer
- **Atomic Components**: Button, Card, Input, Select, Modal, Toast, Badge, Spinner, Alert
- **Composition**: Components can be combined to create complex UIs
- **Props-driven**: Full control through props
- **Consistent styling**: Tailwind CSS classes

### Layout Layer
- **Header**: Global navigation, status, user menu
- **Sidebar**: Navigation menu with route highlighting
- **Footer**: Copyright and links

### Page Layer
- **QueryPage**: Query interface with streaming support
- **IngestPage**: Document upload and management
- **EvaluationPage**: Metrics visualization and evaluation form
- **SettingsPage**: System configuration and monitoring

## Design Patterns Used

### 1. Separation of Concerns
- Services handle API communication
- Hooks handle state and side effects
- Components handle UI rendering

### 2. Composition Over Inheritance
- Build complex components from simple, reusable pieces
- Flexible and maintainable architecture

### 3. Single Responsibility Principle
- Each component does one thing well
- Each service has a single purpose
- Each hook manages one piece of state

### 4. Dependency Injection
- Components receive dependencies via props
- Easy to test and mock

### 5. Microservices-like Architecture
- Service layer is independent and modular
- Each service (query, ingest, evaluation) is self-contained
- Easy to scale or replace individual services

## Key Features

### Modern UI/UX
- Clean Material Design-inspired interface
- Responsive grid layouts
- Smooth animations and transitions
- Accessibility-first approach

### State Management
- useState for local component state
- Custom hooks for complex logic
- useLocalStorage for persistence
- Debouncing for optimized queries

### API Integration
- Axios client with interceptors
- Service layer abstraction
- Error handling and user feedback
- Streaming support for real-time responses

### Performance Optimizations
- Code splitting with lazy loading
- Responsive images
- Efficient re-renders with hooks
- Caching with localStorage

## Styling Strategy

### Tailwind CSS
- Utility-first CSS framework
- No CSS files needed for simple components
- Consistent spacing and colors
- Dark mode support ready

### Custom Utilities (globals.css)
- `.card-shadow`: Consistent shadow effects
- `.btn-*`: Button variants
- `.input-base`: Form input styling
- `.label-base`: Form label styling

## Component Examples

### Simple Component (Button)
```jsx
<Button variant="primary" size="lg" loading={isLoading} onClick={handleClick}>
  Send Query
</Button>
```

### Composed Component (Form)
```jsx
<Card>
  <Input label="Query" value={query} onChange={handleChange} />
  <Select label="Type" options={options} />
  <Button variant="primary">Submit</Button>
</Card>
```

### Page Integration
```jsx
export default function QueryPage() {
  const { loading, error, data, query } = useQuery();
  
  return (
    <Card>
      <Input value={queryText} onChange={...} />
      <Button onClick={() => query(queryText)}>Search</Button>
      {data && <div>{data.response}</div>}
    </Card>
  );
}
```

## Setup Instructions

```bash
# Install dependencies
npm install

# Add React Router for page navigation (auto-imported in App.jsx)
npm install react-router-dom

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## API Integration

### Query Service Example
```javascript
const { loading, error, data, query } = useQuery();
await query("What is AI?", { top_k: 5, use_cache: true });
```

### Custom Hook Usage
```javascript
const [value, setValue] = useLocalStorage('key', 'default');
const debouncedValue = useDebounce(searchInput, 500);
```

## Next Steps for Production

1. **Authentication**: Add JWT/OAuth integration
2. **Error Boundaries**: Add React error boundaries
3. **Testing**: Add Jest + React Testing Library
4. **Analytics**: Add tracking service
5. **PWA**: Make installable as web app
6. **Accessibility**: Add ARIA labels and keyboard navigation
7. **Performance**: Add performance monitoring
8. **i18n**: Add internationalization support
