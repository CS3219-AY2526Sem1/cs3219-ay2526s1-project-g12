export const formatError = (error: any): string => {
  if (!error) return "";

  if (typeof error === "string") return error;

  // Handle common FastAPI-style patterns
  if (typeof error.detail === "string") return error.detail;
  if (typeof error.detail === "object" && "detail" in error.detail)
    return String(error.detail.detail);

  // Fallback — stringify the unknown object
  return JSON.stringify(error);
};
