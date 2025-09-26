import { lazy, Suspense } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import AuthLayout from "./layouts/AuthLayout";
import MainLayout from "./layouts/MainLayout";
import "./assets/styles.css";
import type { LazyExoticComponent, ReactNode } from "react";

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

  // Choose layout based on folder
  let Layout = MainLayout;
  if (routePath.startsWith("/auth")) {
    Layout = AuthLayout;
  }

  return {
    path: routePath === "/landingpage" ? "/" : routePath,
    Component,
    Layout,
  };
});

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Suspense fallback={<div>Loading...</div>}>
        <Routes>
          {routes.map(({ path, Component, Layout }) => (
            <Route
              key={path}
              path={path}
              element={
                <Layout>
                  <Component />
                </Layout>
              }
            />
          ))}
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}

createRoot(document.getElementById("root")!).render(<AppRouter />);
