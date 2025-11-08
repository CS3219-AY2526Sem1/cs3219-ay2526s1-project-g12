import { lazy, Suspense } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './assets/styles.css';
import type { LazyExoticComponent, ReactNode } from 'react';
import { getLayout, isProtectedRoute } from './config/RouteConfig';
import { ProtectedRoute } from './components/ProtectedRoute';
import { AuthProvider } from './context/AuthContext';
import NotFoundRedirect from './components/NotFoundRedirect';

type RouteType = {
  path: string;
  Component: LazyExoticComponent<React.ComponentType<object>>;
  Layout: React.ComponentType<{ children: ReactNode }>;
};

// Dynamically import all pages
const modules = import.meta.glob('./pages/**/*.tsx');

// Convert to route objects
const routes: RouteType[] = Object.keys(modules).map((path) => {
  const Component = lazy(
    modules[path] as () => Promise<{ default: React.ComponentType }>
  );
  const routePath = path
    .replace('./pages', '')
    .replace('.tsx', '')
    .toLowerCase();
  const formattedPath = routePath === '/landingpage' ? '/' : routePath;
  const Layout = getLayout(formattedPath);
  return { path: formattedPath, Component, Layout };
});

function AppRouter() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Routes>
        {routes.map(({ path, Component, Layout }) => {
          const element = (
            <Layout>
              {isProtectedRoute(path) ? (
                <ProtectedRoute>
                  <Component />
                </ProtectedRoute>
              ) : (
                <Component />
              )}
            </Layout>
          );
          return <Route key={path} path={path} element={element} />;
        })}
        <Route path="*" element={<NotFoundRedirect />} />
      </Routes>
    </Suspense>
  );
}

export function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRouter />
      </AuthProvider>
    </BrowserRouter>
  );
}

createRoot(document.getElementById('root')!).render(<App />);
