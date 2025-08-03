# CK Empire Builder - Frontend

A modern React dashboard for the Advanced CK Empire Builder digital empire management tool.

## Features

- 🎨 **Empire-themed Design**: Dark theme with blue and purple color scheme
- 📊 **Real-time Charts**: Recharts integration for data visualization
- 🔄 **Live Metrics**: Polling from backend API endpoints
- 📱 **Responsive Design**: Works on desktop and mobile devices
- ⚡ **Performance Optimized**: Fast loading and smooth animations
- 🧪 **Tested**: Jest and React Testing Library integration

## Tech Stack

- **React 18** - Modern React with hooks
- **Tailwind CSS** - Utility-first CSS framework
- **Recharts** - Composable charting library
- **React Router** - Client-side routing
- **Axios** - HTTP client for API calls
- **React Hot Toast** - Toast notifications
- **Jest** - Testing framework

## Getting Started

### Prerequisites

- Node.js 16+ 
- npm or yarn
- Backend API running on `http://localhost:8000`

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

### Environment Variables

Create a `.env` file in the frontend directory:

```env
REACT_APP_API_URL=http://localhost:8000
```

## Project Structure

```
src/
├── components/          # React components
│   ├── charts/         # Recharts components
│   ├── Sidebar.js      # Navigation sidebar
│   ├── Dashboard.js    # Main dashboard
│   ├── MetricCard.js   # Metric display cards
│   └── ...            # Other page components
├── context/            # React context
│   └── MetricsContext.js # Metrics state management
├── App.js              # Main app component
├── index.js            # React entry point
└── index.css           # Tailwind CSS styles
```

## Components

### Dashboard
- Real-time metrics display
- Interactive charts
- Quick action buttons
- Auto-refresh functionality

### Charts
- **ConsciousnessChart**: AGI consciousness evolution
- **RevenueChart**: Revenue growth trends
- **AgentsChart**: Active agents distribution
- **PerformanceChart**: System performance metrics

### MetricCard
- Reusable metric display component
- Color-coded themes (empire, royal, gold, green)
- Change indicators with icons

## Styling

The app uses a custom Tailwind configuration with Empire-themed colors:

- **Empire Blue**: `#6366f1` - Primary brand color
- **Royal Purple**: `#a855f7` - Secondary accent
- **Gold**: `#f59e0b` - Revenue and success indicators
- **Dark Theme**: Dark backgrounds with light text

## API Integration

The frontend connects to the backend API endpoints:

- `/metrics` - Basic metrics
- `/performance/metrics` - Performance data
- `/ethics/stats` - Ethics statistics
- `/ai/agi-state` - AI consciousness state

## Testing

Run tests with Jest:

```bash
npm test
```

Run tests with coverage:

```bash
npm test -- --coverage
```

## Building for Production

```bash
npm run build
```

This creates an optimized production build in the `build` folder.

## Docker

The frontend includes a Dockerfile for containerization:

```bash
docker build -t ck-empire-frontend .
docker run -p 3000:3000 ck-empire-frontend
```

## Development

### Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm eject` - Eject from Create React App
- `npm lint` - Run ESLint
- `npm format` - Format code with Prettier

### Code Style

The project uses:
- ESLint for code linting
- Prettier for code formatting
- Husky for git hooks

## Contributing

1. Follow the existing code style
2. Write tests for new components
3. Update documentation as needed
4. Ensure all tests pass before submitting

## License

This project is part of the Advanced CK Empire Builder suite. 