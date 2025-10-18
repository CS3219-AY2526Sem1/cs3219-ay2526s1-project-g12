import { lazy, Suspense } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./assets/styles.css";
import type { LazyExoticComponent, ReactNode } from "react";
import { getLayout, isProtectedRoute } from "./config/RouteConfig";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { AuthProvider } from "./context/AuthContext";
import NotFoundRedirect from "./components/NotFoundRedirect";

// Type for our route object
type RouteType = {
  path: string;
  Component: LazyExoticComponent<React.ComponentType<unknown>>;
  Layout: React.ComponentType<{ children: ReactNode }>;
};

// Dynamically import all pages
const modules = import.meta.glob("./pages/**/*.tsx");

// Convert to route objects
const routes: RouteType[] = Object.keys(modules).map((path) => {
  const Component = lazy(
    modules[path] as () => Promise<{ default: React.ComponentType<unknown> }>,
  );

  // Derive route path
  const routePath = path
    .replace("./pages", "")
    .replace(".tsx", "")
    .toLowerCase();

  const formattedPath = routePath === "/landingpage" ? "/" : routePath;
  const Layout = getLayout(formattedPath);

  return {
    path: formattedPath,
    Component,
    Layout,
  };
});

export default function AppRouter() {
  return (
    <AuthProvider>
      <BrowserRouter>
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
            {/* 👇 Add this fallback route at the end */}
            <Route path="*" element={<NotFoundRedirect />} />
          </Routes>
        </Suspense>
      </BrowserRouter>
    </AuthProvider>
  );
}

createRoot(document.getElementById("root")!).render(<AppRouter />);
