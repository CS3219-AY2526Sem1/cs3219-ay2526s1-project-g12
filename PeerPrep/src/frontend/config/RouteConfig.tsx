import AuthLayout from "../layouts/AuthLayout";
import MainLayout from "../layouts/MainLayout";

export const routeSettings = {
  public: ["/auth/login", "/auth/register", "/"],
};

export const getLayout = (path: string) => {
  if (path.startsWith("/auth")) return AuthLayout;
  return MainLayout;
};

// Helper to check if route is protected
export const isProtectedRoute = (path: string) => {
  return !routeSettings.public.includes(path);
};
