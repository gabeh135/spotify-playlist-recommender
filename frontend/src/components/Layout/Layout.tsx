import { NavLink, Outlet } from "react-router-dom"

const navLinks = [
  { to: "/", label: "Collection" },
  { to: "/generate", label: "Generate" },
  { to: "/sort", label: "Sort Library" },
]

export default function Layout() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <nav className="border-b border-border px-6 py-4 flex items-center gap-8">
        <span className="font-semibold tracking-tight text-foreground">Playlist Recommender</span>
        <div className="flex gap-6">
          {navLinks.map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              className={({ isActive }) =>
                isActive
                  ? "text-primary font-medium"
                  : "text-muted-foreground hover:text-foreground transition-colors"
              }
            >
              {label}
            </NavLink>
          ))}
        </div>
      </nav>
      <main className="px-6 py-8 max-w-4xl mx-auto">
        <Outlet />
      </main>
    </div>
  )
}
