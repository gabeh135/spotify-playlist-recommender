import { BrowserRouter, Routes, Route } from "react-router-dom"
import Layout from "./components/Layout/Layout"
import Collection from "./pages/Collection"
import Generate from "./pages/Generate"
import SortLibrary from "./pages/SortLibrary"

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Collection />} />
          <Route path="generate" element={<Generate />} />
          <Route path="sort" element={<SortLibrary />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
