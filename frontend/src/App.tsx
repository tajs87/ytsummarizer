import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import './styles/globals.css';
import { Home } from './pages/Home';
import { VideoDetail } from './pages/VideoDetail';
import { History } from './pages/History';
import { SharePage } from './pages/Share';
import { AuthProvider, useAuth } from './hooks/useAuth';
import { useGuestSession } from './hooks/useGuestSession';

// Create QueryClient instance
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <GuestSessionBootstrap />
        <BrowserRouter>
          <div className="min-h-screen bg-background">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/history" element={<History />} />
              <Route path="/video/:id" element={<VideoDetail />} />
              <Route path="/share/:token" element={<SharePage />} />
            </Routes>
          </div>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}

function GuestSessionBootstrap() {
  const { isAuthenticated } = useAuth();
  useGuestSession(isAuthenticated);
  return null;
}

export default App;
