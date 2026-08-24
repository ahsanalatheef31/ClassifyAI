import { BrowserRouter, Routes, Route } from "react-router-dom";

import Layout from "./components/Layout";

import Dashboard from "./pages/Dashboard";
import ClassifyProduct from "./pages/ClassifyProduct";
import BulkUpload from "./pages/BulkUpload";
import Products from "./pages/Products";
import ProductDetails from "./pages/ProductDetails";
import ManualReview from "./pages/ManualReview";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route
            path="/classify"
            element={<ClassifyProduct />}
          />
          <Route
            path="/bulk-upload"
            element={<BulkUpload />}
          />
          <Route
            path="/products"
            element={<Products />}
          />
          <Route
            path="/products/:id"
            element={<ProductDetails />}
          />
          <Route
            path="/review"
            element={<ManualReview />}
          />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}