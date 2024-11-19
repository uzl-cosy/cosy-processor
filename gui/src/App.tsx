import { createRoot } from "react-dom/client";
import { RouterProvider, createHashRouter } from "react-router-dom";
import Error from "./pages/Error";
import Home from "./pages/Home";
import Settings from "./pages/Settings";
import Controller from "./pages/Controller";
import Log from "./pages/Log";
import { QueryClient, QueryClientProvider } from "react-query";

const router = createHashRouter([
  {
    path: "/",
    element: <Home />,
    errorElement: <Error />,
    children: [
      {
        path: "/",
        element: <Controller />,
      },
      {
        path: "log",
        element: <Log />,
      },
      {
        path: "settings",
        element: <Settings />,
      },
    ],
  },
]);

const queryClient = new QueryClient();

/**
 * The main application component
 *
 * @returns The main application component
 */
function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  );
}

createRoot(document.getElementById("app")).render(<App />);
