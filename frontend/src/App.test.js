import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import App from './App';

// Mock the components to avoid complex dependencies
jest.mock('./components/Sidebar', () => {
  return function MockSidebar() {
    return <div data-testid="sidebar">Sidebar</div>;
  };
});

jest.mock('./components/Dashboard', () => {
  return function MockDashboard() {
    return <div data-testid="dashboard">Dashboard</div>;
  };
});

jest.mock('./components/Projects', () => {
  return function MockProjects() {
    return <div data-testid="projects">Projects</div>;
  };
});

jest.mock('./components/Revenue', () => {
  return function MockRevenue() {
    return <div data-testid="revenue">Revenue</div>;
  };
});

jest.mock('./components/AI', () => {
  return function MockAI() {
    return <div data-testid="ai">AI</div>;
  };
});

jest.mock('./components/Ethics', () => {
  return function MockEthics() {
    return <div data-testid="ethics">Ethics</div>;
  };
});

jest.mock('./components/Performance', () => {
  return function MockPerformance() {
    return <div data-testid="performance">Performance</div>;
  };
});

jest.mock('./components/LogViewer', () => {
  return function MockLogViewer() {
    return <div data-testid="logs">Logs</div>;
  };
});

// Mock axios
jest.mock('axios', () => ({
  get: jest.fn(),
  defaults: {
    baseURL: 'http://localhost:8000',
    timeout: 10000,
  },
  interceptors: {
    request: { use: jest.fn() },
    response: { use: jest.fn() },
  },
}));

// Mock react-hot-toast
jest.mock('react-hot-toast', () => ({
  Toaster: () => <div data-testid="toaster">Toaster</div>,
}));

const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('App Component', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
  });

  test('renders loading state initially', () => {
    renderWithRouter(<App />);
    
    // Should show loading spinner initially
    expect(screen.getByText('CK Empire Builder')).toBeInTheDocument();
    expect(screen.getByText('Initializing your digital empire...')).toBeInTheDocument();
  });

  test('renders sidebar', () => {
    renderWithRouter(<App />);
    
    // After loading, should show sidebar
    expect(screen.getByTestId('sidebar')).toBeInTheDocument();
  });

  test('renders toaster for notifications', () => {
    renderWithRouter(<App />);
    
    expect(screen.getByTestId('toaster')).toBeInTheDocument();
  });

  test('has proper styling classes', () => {
    renderWithRouter(<App />);
    
    // Check for dark theme classes
    const mainContainer = screen.getByText('CK Empire Builder').closest('div');
    expect(mainContainer).toHaveClass('min-h-screen', 'bg-dark-gradient');
  });
});

describe('App Integration', () => {
  test('renders without crashing', () => {
    expect(() => renderWithRouter(<App />)).not.toThrow();
  });

  test('has proper structure', () => {
    renderWithRouter(<App />);
    
    // Should have main container
    const mainContainer = document.querySelector('.flex.h-screen.bg-dark-900');
    expect(mainContainer).toBeInTheDocument();
  });
}); 